// Cross-browser compatibility polyfill
(function() {
  'use strict';

  // Check if we're in Firefox (has browser API) or Chrome (has chrome API)
  if (typeof browser !== 'undefined') {
    // Firefox - browser API is already promise-based
    window.browserAPI = browser;
  } else if (typeof chrome !== 'undefined') {
    // Chrome - wrap chrome API to be promise-based like Firefox
    window.browserAPI = {
      storage: {
        sync: {
          get: function(keys) {
            return new Promise(function(resolve) {
              chrome.storage.sync.get(keys, resolve);
            });
          },
          set: function(items) {
            return new Promise(function(resolve) {
              chrome.storage.sync.set(items, resolve);
            });
          }
        }
      },
      runtime: {
        openOptionsPage: function() {
          return new Promise(function(resolve) {
            chrome.runtime.openOptionsPage(resolve);
          });
        }
      }
    };
  } else {
    console.error('Neither chrome nor browser API is available');
  }
})();