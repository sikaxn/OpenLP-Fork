/*jshint esversion: 9 */
class CommunicationBridge {
    constructor() {
        this.target = null;
        this.initOptions = null;
    }
    
    requestAction(action, ...values) {
        if (action == 'init') {
            this.initOptions = (values && values[0]) || null;
        }

        let returnValue;
        if (this.target) {
            returnValue = this.target._handleNativeCall(action, ...values);
        }

        if (action == 'init') {
            this._onInitialized();
        }

        return returnValue;
    }

    requestActionAsync(action, returnEvent, ...values) {
        let returnValue;
        if (this.target) {
            returnValue = this.target._handleNativeCall(action, ...values);
        }

        if (returnValue && ('then' in returnValue)) {
            returnValue.then((value) => {
                this._dispatchEvent(returnEvent, value || {});
            });
        } else {
            this._dispatchEvent(returnEvent, returnValue || {});
        }

        return returnValue;
    }
    
    setDisplayTarget(newTarget) {
        this.target = newTarget;
        if (this.initOptions) {
            this.target._handleNativeCall('init', ...[this.initOptions]);
            this._onInitialized();
        }
    }

    isReady() {
        return !!this.target;
    }

    pleaseRepaint() {
        if (window.displayWatcher) {
            return window.displayWatcher.pleaseRepaint();
        }
    }

    _onInitialized() {
        if (window.displayWatcher) {
            window.displayWatcher.setInitialised(true);
        }
    }

    _dispatchEvent(eventName, eventParameter) {
        if (window.displayWatcher) {
            window.displayWatcher.dispatchEvent(eventName, eventParameter || {});
        }
    }
}

function initNativeHandlerIfAvailable() {
    if (window.QWebChannel) {
        // Means we're running inside OpenLP
        new window.QWebChannel(window.qt.webChannelTransport, (channel) => {
            window.displayWatcher = channel.objects.displayWatcher;

            // Defining window title as exposed by OpenLP
            (window.displayWatcher.getWindowTitle || (() => Promise.resolve('')))()
                .then((windowTitle) => {
                    if (windowTitle) {
                        const titleTag = document.head.getElementsByTagName('title')[0];
                        if (titleTag) {
                            titleTag.innerText = `${titleTag.innerText} (${windowTitle})`;
                        }
                    }
                });

        });
    }
}

window.initCommunicationBridge = () => {
    initNativeHandlerIfAvailable();
    var communicationBridge = new CommunicationBridge();
    window.communicationBridge = communicationBridge;
    window.requestAction = communicationBridge.requestAction.bind(communicationBridge);
    window.requestActionAsync = communicationBridge.requestActionAsync.bind(communicationBridge);
    window.isReady = communicationBridge.isReady.bind(communicationBridge);
};