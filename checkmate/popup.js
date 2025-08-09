// This script runs when the popup is opened
document.addEventListener('DOMContentLoaded', async function() {
  console.log('Checkmate popup opened!');

  // Get API key from storage
  try {
    const result = await browserAPI.storage.sync.get(['apiKey']);
    console.log('API Key status: ' + (result.apiKey ? 'Set' : 'Not set'));
  } catch (error) {
    console.error('Failed to get API key:', error);
  }

  // Add click handler for options link
  document.getElementById('optionsLink').addEventListener('click', async function() {
    try {
      await browserAPI.runtime.openOptionsPage();
    } catch (error) {
      console.error('Failed to open options page:', error);
    }
  });
});
