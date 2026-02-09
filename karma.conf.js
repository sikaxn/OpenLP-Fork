module.exports = function(config) {
  config.set({
    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: "",

    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ["jasmine"],

    // list of files / patterns to load in the browser
    files: [
      "tests/js/polyfill.js",
      "tests/js/fake_webchannel.js",
      "openlp/core/display/html/reveal.js",
      "openlp/core/display/html/display-init.js",
      "openlp/core/display/html/display.js",
      "tests/js/test_*.js"
    ],

    // list of files to exclude
    exclude: [
    ],

    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
      // source files, that you wanna generate coverage for
      // do not include tests or libraries
      // (these files will be instrumented by Istanbul)
      // "display.js": ["coverage"]
    },

    // test results reporter to use
    // possible values: "dots", "progress"
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ["dots", "junit"],

    // configure the coverateReporter
    /* coverageReporter: {
      type : "html",
      dir : "htmlcov/"
    }, */
    junitReporter: {
      outputFile: "test-results.xml"
    },

    // web server port
    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_DEBUG,

    // loggers
    /* loggers: [
        {"type": "file", "filename": "karma.log"}
    ],*/

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,

    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ["Chromium"],
    customLaunchers: {
      ChromiumHeadlessCI: {
        base: 'ChromiumHeadless',
        flags: ['--no-sandbox']
      }
    },

    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true,

    // Concurrency level
    // how many browser should be started simultaneous
    concurrency: Infinity,

    client: {
        captureConsole: true
    }
  })
}
