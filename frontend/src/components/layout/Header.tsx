import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Chip
} from '@mui/material';

interface HeaderProps {
  isAuthenticated: boolean;
  username?: string;
  rating?: number;
  onConnect: () => void;
}

const Header: React.FC<HeaderProps> = ({
  isAuthenticated,
  username,
  rating,
  onConnect
}) => {
  return (
    <AppBar
      position="fixed"
      sx={{
        width: `calc(100% - 240px)`,
        ml: '240px',
        backgroundColor: '#1e1e1e',
        boxShadow: 'none',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}
    >
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Chess Analysis Dashboard
        </Typography>

        {isAuthenticated ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              label={`Rating: ${rating}`}
              color="primary"
              size="small"
            />
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Avatar sx={{ width: 32, height: 32 }}>
                {username?.charAt(0).toUpperCase()}
              </Avatar>
              <Typography variant="body2">{username}</Typography>
            </Box>
          </Box>
        ) : (
          <Button
            variant="contained"
            color="primary"
            onClick={onConnect}
          >
            Connect to Lichess
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
