"use strict";

describe("The CommunicationBridge object", () => {
    /** @type {CommunicationBridge} */
    let testCommunicationBridge;
    let SimpleTarget;

    beforeEach(() => {
        testCommunicationBridge = new CommunicationBridge();
        SimpleTarget = class {
            _handleNativeCall(action, ...values) {}
        }
    });

    it("should exist", () => {
        expect(CommunicationBridge).toBeDefined()
    });
    it("should not be ready after instantiated", () => {
        expect(testCommunicationBridge.isReady()).toBe(false);
    });
    it("should register target", () => {
        testCommunicationBridge.setDisplayTarget(new SimpleTarget());
        expect(testCommunicationBridge.isReady()).toBe(true);
        
    });
    it("should be able to requestAction", (done) => {
        const target = new SimpleTarget()
        target._handleNativeCall = (action, ...values) => done();
        testCommunicationBridge.setDisplayTarget(target);
        testCommunicationBridge.requestAction('dummy');
    });
    it("should be able to replay init action before setDisplayTarget", (done) => {
        const target = new SimpleTarget()
        target._handleNativeCall = (action, ...values) => {
            if (action == 'init') {
                expect(values[0]).toBe('replayed init');
                done();
            }
        }
        testCommunicationBridge.requestAction('init', 'replayed init');
        testCommunicationBridge.setDisplayTarget(target);
    });
    it("should dispatch initialized event", (done) => {
        displayWatcher.setInitialised = () => done();
        testCommunicationBridge.setDisplayTarget(new SimpleTarget());
        testCommunicationBridge.requestAction('init', {do_init: true});
    });
    it("should dispatch event on async call and promise-based handlers", (done) => {
        const target = new SimpleTarget()
        target._handleNativeCall = (action, ...values) => {
            if (action == 'async') {
                return new Promise((resolve) => resolve({value: 'async value'}));
            }
        }
        testCommunicationBridge.setDisplayTarget(target);
        displayWatcher.dispatchEvent = (event, parameter) => {
            expect(event).toBe('async_callback');
            expect(parameter).toEqual({value: 'async value'});
            done();
        }

        // THEN: async callback should return value over displayWatch.dispatchEvent()
        testCommunicationBridge.requestActionAsync('async', 'async_callback');
    });
    it("should dispatch event on async call and normal handlers", (done) => {
        const target = new SimpleTarget()
        target._handleNativeCall = (action, ...values) => {
            if (action == 'sync') {
                return {value: 'sync value'};
            }
        }
        testCommunicationBridge.setDisplayTarget(target);
        displayWatcher.dispatchEvent = (event, parameter) => {
            expect(event).toBe('sync_callback');
            expect(parameter).toEqual({value: 'sync value'});
            done();
        }

        // THEN: async callback should return value over displayWatch.dispatchEvent()
        testCommunicationBridge.requestActionAsync('sync', 'sync_callback');
    });
});