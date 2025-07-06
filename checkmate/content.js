// This script runs on lichess.org pages
console.log('Hello from the Checkmate extension!');

// Create a floating message
function createHelloMessage(message) {
  const messageDiv = document.createElement('div');
  messageDiv.textContent = message;
  messageDiv.style.position = 'fixed';
  messageDiv.style.top = '10px';
  messageDiv.style.right = '10px';
  messageDiv.style.backgroundColor = 'white';
  messageDiv.style.color = 'black';
  messageDiv.style.padding = '10px';
  messageDiv.style.borderRadius = '5px';
  messageDiv.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
  messageDiv.style.zIndex = '9999';

  document.body.appendChild(messageDiv);

  // Remove the message after 5 seconds
  setTimeout(() => {
    messageDiv.remove();
  }, 5000);
}

// Check if API key is set
function checkApiKey() {
  chrome.storage.sync.get(['apiKey'], function(result) {
    if (result.apiKey) {
      createHelloMessage('Hello, Lichess! API Key is set.');
      console.log('API Key is set and ready to use with OpenAI.');
      // Here you could use the API key to make requests to OpenAI
    } else {
      createHelloMessage('Hello, Lichess! Please set your OpenAI API Key in the extension settings.');
    }
  });
}

// Wait for the page to fully load
window.addEventListener('load', function() {
  checkApiKey();
});
