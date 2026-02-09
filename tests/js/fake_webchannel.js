// This is a mock QWebChannel
var qt = {webChannelTransport: 1};
var displayWatcher = {
  setInitialised: function (is_initialised) {
    // do nothing
  }
}
var QWebChannel = function (transport, callback) {
  callback({objects: {mediaWatcher: {}, displayWatcher: displayWatcher}});
};
