// Save options to storage
async function saveOptions() {
  const apiKey = document.getElementById('apiKey').value;

  try {
    await browserAPI.storage.sync.set({ apiKey: apiKey });
    // Update status to let user know options were saved
    const status = document.getElementById('status');
    status.textContent = 'Options saved.';
    status.className = 'status success';
    status.style.display = 'block';

    setTimeout(function() {
      status.style.display = 'none';
    }, 3000);
  } catch (error) {
    console.error('Failed to save options:', error);
    const status = document.getElementById('status');
    status.textContent = 'Error saving options.';
    status.className = 'status error';
    status.style.display = 'block';
  }
}

// Restore options from storage
async function restoreOptions() {
  try {
    const items = await browserAPI.storage.sync.get({ apiKey: '' });
    document.getElementById('apiKey').value = items.apiKey;
  } catch (error) {
    console.error('Failed to restore options:', error);
  }
}

// Add event listeners
document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('saveButton').addEventListener('click', saveOptions);
