import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Stack
} from '@mui/material';

// Mock data for games
const games = Array.from({ length: 50 }).map((_, index) => ({
  id: `game-${index + 1}`,
  opponent: `Player${Math.floor(Math.random() * 1000)}`,
  date: new Date(2025, 5, Math.floor(Math.random() * 30) + 1).toISOString().split('T')[0],
  result: ['Win', 'Loss', 'Draw'][Math.floor(Math.random() * 3)],
  timeControl: ['Bullet', 'Blitz', 'Rapid', 'Classical'][Math.floor(Math.random() * 4)],
  opening: ['Sicilian Defense', 'Queen\'s Gambit', 'Ruy Lopez', 'French Defense', 'King\'s Indian'][Math.floor(Math.random() * 5)],
  moves: Math.floor(Math.random() * 60) + 20,
  yourRating: Math.floor(Math.random() * 400) + 1600,
  opponentRating: Math.floor(Math.random() * 400) + 1600,
}));

const GamesPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [timeControl, setTimeControl] = useState('all');
  const [result, setResult] = useState('all');

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleTimeControlChange = (event: SelectChangeEvent) => {
    setTimeControl(event.target.value);
    setPage(0);
  };

  const handleResultChange = (event: SelectChangeEvent) => {
    setResult(event.target.value);
    setPage(0);
  };

  // Filter games based on selected filters
  const filteredGames = games.filter(game => {
    if (timeControl !== 'all' && game.timeControl !== timeControl) return false;
    if (result !== 'all' && game.result !== result) return false;
    return true;
  });

  // Get current page of games
  const currentGames = filteredGames.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        My Games
      </Typography>

      <Paper
        sx={{
          p: 2,
          mb: 3,
          backgroundColor: '#1e1e1e',
          color: 'white',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel id="time-control-label" sx={{ color: 'rgba(255,255,255,0.7)' }}>Time Control</InputLabel>
            <Select
              labelId="time-control-label"
              value={timeControl}
              label="Time Control"
              onChange={handleTimeControlChange}
              sx={{
                color: 'white',
                '.MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.3)',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.5)',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'primary.main',
                },
                '.MuiSvgIcon-root': {
                  color: 'rgba(255,255,255,0.7)',
                }
              }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="Bullet">Bullet</MenuItem>
              <MenuItem value="Blitz">Blitz</MenuItem>
              <MenuItem value="Rapid">Rapid</MenuItem>
              <MenuItem value="Classical">Classical</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel id="result-label" sx={{ color: 'rgba(255,255,255,0.7)' }}>Result</InputLabel>
            <Select
              labelId="result-label"
              value={result}
              label="Result"
              onChange={handleResultChange}
              sx={{
                color: 'white',
                '.MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.3)',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(255,255,255,0.5)',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'primary.main',
                },
                '.MuiSvgIcon-root': {
                  color: 'rgba(255,255,255,0.7)',
                }
              }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="Win">Win</MenuItem>
              <MenuItem value="Loss">Loss</MenuItem>
              <MenuItem value="Draw">Draw</MenuItem>
            </Select>
          </FormControl>
        </Stack>
      </Paper>

      <TableContainer
        component={Paper}
        sx={{
          backgroundColor: '#1e1e1e',
          color: 'white',
          border: '1px solid rgba(255,255,255,0.1)'
        }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Date</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Opponent</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Result</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Time Control</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Opening</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Moves</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Your Rating</TableCell>
              <TableCell sx={{ color: 'rgba(255,255,255,0.7)', fontWeight: 'bold' }}>Opponent Rating</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {currentGames.map((game) => (
              <TableRow
                key={game.id}
                hover
                sx={{
                  cursor: 'pointer',
                  '&:hover': { backgroundColor: 'rgba(255,255,255,0.05)' },
                  '& .MuiTableCell-root': { color: 'white', borderBottomColor: 'rgba(255,255,255,0.1)' }
                }}
              >
                <TableCell>{game.date}</TableCell>
                <TableCell>{game.opponent}</TableCell>
                <TableCell>
                  <Chip
                    label={game.result}
                    color={
                      game.result === 'Win' ? 'success' :
                      game.result === 'Loss' ? 'error' :
                      'warning'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>{game.timeControl}</TableCell>
                <TableCell>{game.opening}</TableCell>
                <TableCell>{game.moves}</TableCell>
                <TableCell>{game.yourRating}</TableCell>
                <TableCell>{game.opponentRating}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredGames.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          sx={{
            color: 'white',
            '.MuiTablePagination-selectIcon': { color: 'rgba(255,255,255,0.7)' },
            '.MuiTablePagination-actions': { color: 'rgba(255,255,255,0.7)' }
          }}
        />
      </TableContainer>
    </Box>
  );
};

export default GamesPage;
