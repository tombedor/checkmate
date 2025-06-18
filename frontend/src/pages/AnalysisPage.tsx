import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  Button,
  Stack,
  Chip
} from '@mui/material';
import ChessBoard from '../components/chess/ChessBoard';

// Mock data for analysis
const gameInfo = {
  white: 'ChessPlayer',
  black: 'Magnus_Fan',
  date: '2025-06-15',
  result: 'Win',
  timeControl: 'Rapid',
  opening: 'Sicilian Defense',
  whiteRating: 1845,
  blackRating: 1832,
};

const analysisPoints = [
  {
    id: 1,
    move: 15,
    type: 'Mistake',
    description: 'Missed tactical opportunity with Nxe4, which would have won material.',
    position: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' // Starting position as placeholder
  },
  {
    id: 2,
    move: 24,
    type: 'Blunder',
    description: 'Knight fork was missed after Qd7, allowing opponent to gain advantage.',
    position: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' // Starting position as placeholder
  },
  {
    id: 3,
    move: 32,
    type: 'Good Move',
    description: 'Excellent defensive resource with Rf8, neutralizing opponent\'s attack.',
    position: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' // Starting position as placeholder
  },
];

const strategicTakeaways = [
  'Work on recognizing tactical patterns, particularly knight forks',
  'Improve calculation in complex positions',
  'Good endgame technique, but could be more efficient in converting advantage'
];

const similarGames = [
  { id: 1, opponent: 'ChessWizard', result: 'Loss', date: '2025-06-10', opening: 'Sicilian Defense' },
  { id: 2, opponent: 'KnightRider', result: 'Win', date: '2025-05-28', opening: 'Sicilian Defense' },
];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AnalysisPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedAnalysisPoint, setSelectedAnalysisPoint] = useState(analysisPoints[0]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAnalysisPointClick = (point: typeof analysisPoints[0]) => {
    setSelectedAnalysisPoint(point);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Game Analysis
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3, mb: 3 }}>
        {/* Chess Board */}
        <Box sx={{ flex: 1 }}>
          <ChessBoard
            position={selectedAnalysisPoint.position}
            title={`Move ${selectedAnalysisPoint.move}: ${selectedAnalysisPoint.type}`}
            boardWidth={500}
          />
        </Box>

        {/* Game Info and Analysis Points */}
        <Paper
          sx={{
            p: 2,
            flex: 1,
            backgroundColor: '#1e1e1e',
            color: 'white',
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        >
          <Typography variant="h6" gutterBottom>
            Game Information
          </Typography>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1">
              {gameInfo.white} ({gameInfo.whiteRating}) vs {gameInfo.black} ({gameInfo.blackRating})
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              {gameInfo.date} • {gameInfo.timeControl} • {gameInfo.opening}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Result: <Chip
                label={gameInfo.result}
                color={
                  gameInfo.result === 'Win' ? 'success' :
                  gameInfo.result === 'Loss' ? 'error' :
                  'warning'
                }
                size="small"
              />
            </Typography>
          </Box>

          <Typography variant="h6" gutterBottom>
            Key Moments
          </Typography>
          <List>
            {analysisPoints.map((point) => (
              <React.Fragment key={point.id}>
                <ListItem disablePadding>
                  <ListItemButton
                    selected={selectedAnalysisPoint.id === point.id}
                    onClick={() => handleAnalysisPointClick(point)}
                    sx={{
                      '&.Mui-selected': {
                        backgroundColor: 'rgba(255,255,255,0.1)',
                      },
                      '&.Mui-selected:hover': {
                        backgroundColor: 'rgba(255,255,255,0.15)',
                      },
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.05)',
                      }
                    }}
                  >
                    <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography>Move {point.move}</Typography>
                        <Chip
                          label={point.type}
                          color={
                            point.type === 'Mistake' ? 'warning' :
                            point.type === 'Blunder' ? 'error' :
                            'success'
                          }
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {point.description}
                      </Typography>
                    }
                    />
                  </ListItemButton>
                </ListItem>
                <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
              </React.Fragment>
            ))}
          </List>
        </Paper>
      </Box>

      <Paper
        sx={{
          backgroundColor: '#1e1e1e',
          color: 'white',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          sx={{
            borderBottom: 1,
            borderColor: 'rgba(255,255,255,0.1)',
            '& .MuiTabs-indicator': {
              backgroundColor: 'primary.main',
            },
            '& .MuiTab-root': {
              color: 'rgba(255,255,255,0.7)',
              '&.Mui-selected': {
                color: 'white',
              }
            }
          }}
        >
          <Tab label="Strategy Takeaways" />
          <Tab label="Similar Games" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <List>
            {strategicTakeaways.map((takeaway, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemText primary={takeaway} />
                </ListItem>
                <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
              </React.Fragment>
            ))}
          </List>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <List>
            {similarGames.map((game) => (
              <React.Fragment key={game.id}>
                <ListItem>
                  <ListItemText
                    primary={`vs ${game.opponent}`}
                    secondary={
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                        {game.date} • {game.result} • {game.opening}
                      </Typography>
                    }
                  />
                  <Button variant="outlined" size="small" sx={{ ml: 2 }}>
                    View
                  </Button>
                </ListItem>
                <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
              </React.Fragment>
            ))}
          </List>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default AnalysisPage;
