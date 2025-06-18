import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Stack
} from '@mui/material';
import { Save as SaveIcon, Delete as DeleteIcon } from '@mui/icons-material';

const SettingsPage: React.FC = () => {
  const [lichessToken, setLichessToken] = useState('');
  const [cacheSize, setCacheSize] = useState('1000');
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [autoAnalyze, setAutoAnalyze] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleSaveSettings = () => {
    // In a real application, this would save the settings to a backend or local storage
    setSnackbarMessage('Settings saved successfully!');
    setSnackbarOpen(true);
  };

  const handleClearCache = () => {
    // In a real application, this would clear the local game cache
    setSnackbarMessage('Cache cleared successfully!');
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Paper
        sx={{
          p: 3,
          backgroundColor: '#1e1e1e',
          color: 'white',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <Typography variant="h6" gutterBottom>
          Lichess API
        </Typography>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label="Lichess API Token"
            variant="outlined"
            value={lichessToken}
            onChange={(e) => setLichessToken(e.target.value)}
            type="password"
            margin="normal"
            helperText="Enter your Lichess API token to connect to your account"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'white',
                '& fieldset': {
                  borderColor: 'rgba(255,255,255,0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255,255,255,0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255,255,255,0.7)',
              },
              '& .MuiFormHelperText-root': {
                color: 'rgba(255,255,255,0.5)',
              },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            sx={{ mt: 1 }}
          >
            Test Connection
          </Button>
        </Box>

        <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)', my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Cache Settings
        </Typography>
        <Box sx={{ mb: 3 }}>
          <TextField
            label="Maximum Games to Cache"
            variant="outlined"
            value={cacheSize}
            onChange={(e) => setCacheSize(e.target.value)}
            type="number"
            margin="normal"
            helperText="Maximum number of games to store locally"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'white',
                '& fieldset': {
                  borderColor: 'rgba(255,255,255,0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255,255,255,0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255,255,255,0.7)',
              },
              '& .MuiFormHelperText-root': {
                color: 'rgba(255,255,255,0.5)',
              },
            }}
          />
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearCache}
            sx={{ mt: 1, ml: 2 }}
          >
            Clear Cache
          </Button>
        </Box>

        <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)', my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Application Settings
        </Typography>
        <Stack spacing={2}>
          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
                color="primary"
              />
            }
            label="Dark Mode"
          />
          <FormControlLabel
            control={
              <Switch
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
                color="primary"
              />
            }
            label="Enable Notifications"
          />
          <FormControlLabel
            control={
              <Switch
                checked={autoAnalyze}
                onChange={(e) => setAutoAnalyze(e.target.checked)}
                color="primary"
              />
            }
            label="Automatically Analyze New Games"
          />
        </Stack>

        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={handleSaveSettings}
            size="large"
          >
            Save Settings
          </Button>
        </Box>
      </Paper>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity="success"
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SettingsPage;
