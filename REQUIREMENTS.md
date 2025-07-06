# Checkmate: Lichess AI Analysis Assistant

## Project Overview
Checkmate is a Chrome extension that enhances the Lichess.org chess analysis experience by providing an interactive AI assistant that can answer questions about games and provide personalized analysis.

## Functional Requirements

### Core Functionality
1. Integrate with Lichess.org game analysis pages (e.g., https://lichess.org/54wK8qGc/black). The HTML for this page is saved to example.html
2. Provide an interactive chat window interface for communicating with an AI assistant
3. Enable users to ask questions about their chess games
4. Extract and utilize game analysis data from the webpage to inform AI responses

### User Interface
1. Display a clean, unobtrusive chat window on Lichess analysis pages
2. Provide clear indication when the AI is processing requests
3. Support scrollable chat history within the current session

### Configuration
1. Provide options page for extension settings
2. Allow users to input and save their OpenAI or Anthropic API key
3. Store API keys securely in the browser's local storage

## Technical Requirements

### Browser Compatibility
1. Function properly as a Chrome web extension
2. Support current versions of Chrome browser

### API Integration
1. Connect to OpenAI API services using user-provided API key
2. Connect to Anthropic API services using user-provided API key
3. Handle API errors gracefully with user-friendly messages

### Data Handling
1. Extract relevant chess game data from Lichess analysis pages
2. Process and format game data appropriately for AI analysis
3. Do not store or transmit user's chess games or analysis to external servers (beyond what's needed for API calls)

### Security
1. Store API keys securely in local storage
2. Do not transmit API keys to any servers other than the respective API services
3. Request minimum necessary permissions for extension functionality

## Constraints
1. The extension must work within the limitations of Chrome's extension API
2. The extension must respect Lichess.org's terms of service and rate limits
3. Users must provide their own API keys for OpenAI or Anthropic services

## Future Enhancements (Optional)
1. Support for additional chess websites beyond Lichess.org
2. Ability to save and export analysis conversations
3. Integration with additional AI service providers
4. Enhanced visualization of AI suggestions on the chess board
