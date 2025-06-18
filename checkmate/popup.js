// This script runs when the popup is opened
document.addEventListener('DOMContentLoaded', function() {
  console.log('Checkmate popup opened!');

  // Get API key from storage
  chrome.storage.sync.get(['apiKey'], function(result) {
    console.log('API Key status: ' + (result.apiKey ? 'Set' : 'Not set'));
  });

  // Add click handler for options link
  document.getElementById('optionsLink').addEventListener('click', function() {
    chrome.runtime.openOptionsPage();
  });
});
