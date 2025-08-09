# Checkmate - AI Chess Tutor Extension

A browser extension for Chrome and Firefox that provides real-time chess analysis and educational insights for lichess.org games using OpenAI's GPT-4.

## Features

- **Real-time Analysis**: AI-powered chess tutor that analyzes your lichess.org games
- **Interactive Chat**: Ask questions about specific moves, positions, and strategies
- **Move Context**: Automatically detects current move and position for contextual advice
- **Game Data Extraction**: Extracts PGN, FEN positions, and Stockfish evaluations
- **Draggable Interface**: Resizable, minimizable, and draggable chat window

## Prerequisites

- Chrome or Firefox browser
- OpenAI API key (GPT-4 access required)
- lichess.org account (for playing/analyzing games)

## Installation

### 1. Download the Extension
Clone or download this repository to your local machine:
```bash
git clone <repository-url>
cd checkmate
```

### 2. Install in Your Browser

#### For Chrome:
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `checkmate` folder containing the extension files

#### For Firefox:
1. Copy `manifest-firefox.json` to `manifest.json` in the `checkmate` folder:
   ```bash
   cd checkmate
   cp manifest-firefox.json manifest.json
   ```
2. Open Firefox and navigate to `about:debugging`
3. Click "This Firefox" in the sidebar
4. Click "Load Temporary Add-on"
5. Select the `manifest.json` file in the `checkmate` folder

**Note:** Firefox temporary add-ons are removed when you restart the browser. For permanent installation, you'll need to package and sign the extension through Mozilla's Add-on Developer Hub.

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

# License

Apache 2.0
