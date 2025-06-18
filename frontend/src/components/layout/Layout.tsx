import React, { useState } from 'react';
import { Box, CssBaseline, Toolbar } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | undefined>(undefined);
  const [rating, setRating] = useState<number | undefined>(undefined);

  const handleConnect = () => {
    // In a real application, this would initiate the Lichess OAuth flow
    // For now, we'll just simulate a successful authentication
    setIsAuthenticated(true);
    setUsername('ChessPlayer');
    setRating(1850);
  };

  return (
    <Box sx={{ display: 'flex', bgcolor: '#121212', minHeight: '100vh', color: 'white' }}>
      <CssBaseline />
      <Sidebar />
      <Header
        isAuthenticated={isAuthenticated}
        username={username}
        rating={rating}
        onConnect={handleConnect}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - 240px)` },
          ml: { sm: '240px' },
          mt: '64px'
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
