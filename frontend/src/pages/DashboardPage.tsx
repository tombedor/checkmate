import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  Stack
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data for the dashboard
const recentGames = [
  { id: 1, opponent: 'Magnus_Fan', result: 'Win', date: '2025-06-15', rating: 1845 },
  { id: 2, opponent: 'ChessWizard', result: 'Loss', date: '2025-06-14', rating: 1832 },
  { id: 3, opponent: 'KnightRider', result: 'Win', date: '2025-06-12', rating: 1840 },
  { id: 4, opponent: 'QueenGambit', result: 'Draw', date: '2025-06-10', rating: 1840 },
];

const improvementSuggestions = [
  { id: 1, category: 'Tactical Opportunities', description: 'Missed fork on move 24 against ChessWizard' },
  { id: 2, category: 'Opening Mistakes', description: 'Inaccurate development in Sicilian Defense' },
  { id: 3, category: 'Endgame Technique', description: 'Rook endgame could be improved against KnightRider' },
];

const ratingData = [
  { date: '2025-05-01', rating: 1800 },
  { date: '2025-05-15', rating: 1820 },
  { date: '2025-06-01', rating: 1810 },
  { date: '2025-06-15', rating: 1845 },
];

const DashboardPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Stack spacing={3}>
        <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
          {/* Recent Games */}
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
              Recent Games
            </Typography>
            <List>
              {recentGames.map((game) => (
                <React.Fragment key={game.id}>
                  <ListItem>
                    <ListItemText
                      primary={`vs ${game.opponent}`}
                      secondary={
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          {game.date} • {game.result} • Rating: {game.rating}
                        </Typography>
                      }
                    />
                  </ListItem>
                  <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
                </React.Fragment>
              ))}
            </List>
          </Paper>

          {/* Improvement Suggestions */}
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
              Improvement Suggestions
            </Typography>
            <List>
              {improvementSuggestions.map((suggestion) => (
                <React.Fragment key={suggestion.id}>
                  <ListItem>
                    <ListItemText
                      primary={suggestion.category}
                      secondary={
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          {suggestion.description}
                        </Typography>
                      }
                    />
                  </ListItem>
                  <Divider sx={{ backgroundColor: 'rgba(255,255,255,0.1)' }} />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Box>

        {/* Progress Chart */}
        <Paper
          sx={{
            p: 2,
            height: 300,
            backgroundColor: '#1e1e1e',
            color: 'white',
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        >
          <Typography variant="h6" gutterBottom>
            Rating Progress
          </Typography>
          <ResponsiveContainer width="100%" height="80%">
            <LineChart
              data={ratingData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.7)" />
              <YAxis stroke="rgba(255,255,255,0.7)" domain={['dataMin - 50', 'dataMax + 50']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#2e2e2e',
                  color: 'white',
                  border: '1px solid rgba(255,255,255,0.2)'
                }}
              />
              <Line
                type="monotone"
                dataKey="rating"
                stroke="#8884d8"
                activeDot={{ r: 8 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Stack>
    </Box>
  );
};

export default DashboardPage;
