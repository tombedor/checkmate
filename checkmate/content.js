// This script runs on lichess.org pages
console.log('Hello from the Checkmate extension!');

// Create a floating message
function createHelloMessage() {
  const messageDiv = document.createElement('div');
  messageDiv.textContent = 'Hello, Lichess!';
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

// Wait for the page to fully load
window.addEventListener('load', function() {
  createHelloMessage();
});
