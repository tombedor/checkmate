import React from 'react';
import { Chessboard } from 'react-chessboard';
import { Box, Paper, Typography } from '@mui/material';

interface ChessBoardProps {
  position: string;
  title?: string;
  showCoordinates?: boolean;
  boardWidth?: number;
  onPieceDrop?: (sourceSquare: string, targetSquare: string) => boolean;
}

const ChessBoard: React.FC<ChessBoardProps> = ({
  position,
  title,
  showCoordinates = true,
  boardWidth = 500,
  onPieceDrop
}) => {
  return (
    <Paper
      sx={{
        p: 2,
        backgroundColor: '#1e1e1e',
        color: 'white',
        border: '1px solid rgba(255,255,255,0.1)'
      }}
    >
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <Box sx={{ maxWidth: boardWidth, mx: 'auto' }}>
        <Chessboard
          position={position}
          boardWidth={boardWidth}
          showBoardNotation={showCoordinates}
          areArrowsAllowed={true}
          onPieceDrop={onPieceDrop}
          customDarkSquareStyle={{ backgroundColor: '#779556' }}
          customLightSquareStyle={{ backgroundColor: '#edeed1' }}
        />
      </Box>
    </Paper>
  );
};

export default ChessBoard;
