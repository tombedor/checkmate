# Checkmate - AI Chess Tutor Extension

A Chrome extension that provides real-time chess analysis and educational insights for lichess.org games using OpenAI's GPT-4.

## Features

- **Real-time Analysis**: AI-powered chess tutor that analyzes your lichess.org games
- **Interactive Chat**: Ask questions about specific moves, positions, and strategies
- **Move Context**: Automatically detects current move and position for contextual advice
- **Game Data Extraction**: Extracts PGN, FEN positions, and Stockfish evaluations
- **Draggable Interface**: Resizable, minimizable, and draggable chat window

## Known issues

Hallucination is a major issue, the AI gets confused about what positions exist and are valid. This is a POC

## Prerequisites

- Google Chrome browser
- OpenAI API key (GPT-4 access required)
- lichess.org account (for playing/analyzing games)

## Installation

### 1. Download the Extension
Clone or download this repository to your local machine:
```bash
git clone <repository-url>
cd checkmate
```

### 2. Load Extension in Chrome
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `checkmate` folder containing the extension files

### 3. Configure API Key
1. Click the Checkmate extension icon in your browser toolbar
2. Click "⚙️ Settings" in the popup
3. Enter your OpenAI API key
4. Click "Save"

## Usage

1. Navigate to lichess.org and open any chess game or analysis
2. The Checkmate chat window will appear in the bottom-right corner
3. Ask questions about the current position, moves, or general chess strategy
4. The AI tutor will provide educational insights and analysis

### Chat Window Controls
- **Drag**: Click and drag the header to reposition
- **Minimize**: Click the "−" button to minimize to header only
- **Maximize**: Click the "□" button to expand to full screen
- **Clear**: Click the "🗑️" button to clear conversation history
- **Close**: Click the "×" button to close the chat window
