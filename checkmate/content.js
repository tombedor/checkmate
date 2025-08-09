// This script runs on lichess.org pages
console.log('Checkmate Chess Tutor loaded!');

class ChessAnalyzer {
  constructor() {
    this.apiKey = null;
    this.gameData = null;
    this.chatWindow = null;
    this.isMinimized = false;
    this.isMaximized = false;
    this.originalSize = { width: '350px', height: '500px' };
    this.conversationHistory = [];
    this.init();
  }

  async init() {
    // Get API key from storage
    try {
      const result = await browserAPI.storage.sync.get(['apiKey']);
      this.apiKey = result.apiKey;
      if (this.apiKey) {
        this.createChatWindow();
        // Initialize basic game data structure
        this.gameData = {
          gameUrl: window.location.href,
          timestamp: new Date().toISOString()
        };
      } else {
        this.showSetupMessage();
      }
    } catch (error) {
      console.error('Failed to get API key:', error);
      this.showSetupMessage();
    }
  }

  showSetupMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = 'Please set your OpenAI API Key in Checkmate settings to use the chess tutor.';
    messageDiv.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: #ff6b6b;
      color: white;
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      z-index: 10000;
      font-family: Arial, sans-serif;
      font-size: 14px;
      cursor: pointer;
    `;

    document.body.appendChild(messageDiv);

    setTimeout(() => {
      messageDiv.remove();
    }, 10000);
  }

  createChatWindow() {
    // Create main chat container
    this.chatWindow = document.createElement('div');
    this.chatWindow.id = 'checkmate-chat';
    this.chatWindow.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: ${this.originalSize.width};
      height: ${this.originalSize.height};
      background: white;
      border: 2px solid #4CAF50;
      border-radius: 10px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      display: flex;
      flex-direction: column;
      resize: both;
      overflow: hidden;
      transition: all 0.3s ease;
    `;

    // Create header
    const header = document.createElement('div');
    header.style.cssText = `
      background: #4CAF50;
      color: white;
      padding: 10px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: move;
    `;
    header.innerHTML = `
      <span>♟️ Chess Tutor</span>
      <div>
        <button id="clear-btn" style="background: none; border: none; color: white; font-size: 14px; cursor: pointer; margin-right: 5px; padding: 2px 6px; border-radius: 3px;" title="Clear conversation">🗑️</button>
        <button id="maximize-btn" style="background: none; border: none; color: white; font-size: 16px; cursor: pointer; margin-right: 5px; padding: 2px 6px; border-radius: 3px;" title="Maximize">□</button>
        <button id="minimize-btn" style="background: none; border: none; color: white; font-size: 16px; cursor: pointer; margin-right: 5px; padding: 2px 6px; border-radius: 3px;" title="Minimize">−</button>
        <button id="close-btn" style="background: none; border: none; color: white; font-size: 16px; cursor: pointer; padding: 2px 6px; border-radius: 3px;" title="Close">×</button>
      </div>
    `;

    // Create messages container
    const messagesContainer = document.createElement('div');
    messagesContainer.id = 'messages-container';
    messagesContainer.style.cssText = `
      flex: 1;
      overflow-y: auto;
      padding: 15px;
      background: #fafafa;
      line-height: 1.5;
      font-size: 14px;
    `;

    // Create input area
    const inputArea = document.createElement('div');
    inputArea.style.cssText = `
      display: flex;
      padding: 10px;
      background: white;
      border-top: 1px solid #ddd;
    `;

    const messageInput = document.createElement('input');
    messageInput.type = 'text';
    messageInput.placeholder = 'Ask about this chess game...';
    messageInput.style.cssText = `
      flex: 1;
      padding: 8px;
      border: 1px solid #ddd;
      border-radius: 4px;
      margin-right: 10px;
    `;

    const sendButton = document.createElement('button');
    sendButton.textContent = 'Send';
    sendButton.style.cssText = `
      background: #4CAF50;
      color: white;
      border: none;
      padding: 8px 16px;
      border-radius: 4px;
      cursor: pointer;
    `;

    // Add event listeners
    header.addEventListener('mousedown', this.startDrag.bind(this));
    document.getElementById = (id) => {
      if (id === 'minimize-btn') return header.querySelector('#minimize-btn');
      if (id === 'close-btn') return header.querySelector('#close-btn');
      return document.querySelector('#' + id);
    };

    // Assemble the window
    inputArea.appendChild(messageInput);
    inputArea.appendChild(sendButton);
    this.chatWindow.appendChild(header);
    this.chatWindow.appendChild(messagesContainer);
    this.chatWindow.appendChild(inputArea);
    document.body.appendChild(this.chatWindow);

    // Add event listeners after DOM is ready
    setTimeout(() => {
      const clearBtn = this.chatWindow.querySelector('#clear-btn');
      const maximizeBtn = this.chatWindow.querySelector('#maximize-btn');
      const minimizeBtn = this.chatWindow.querySelector('#minimize-btn');
      const closeBtn = this.chatWindow.querySelector('#close-btn');

      clearBtn.addEventListener('click', this.clearConversation.bind(this));
      maximizeBtn.addEventListener('click', this.toggleMaximize.bind(this));
      minimizeBtn.addEventListener('click', this.toggleMinimize.bind(this));
      closeBtn.addEventListener('click', this.closeChatWindow.bind(this));
      sendButton.addEventListener('click', () => this.sendMessage(messageInput.value));
      messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.sendMessage(messageInput.value);
        }
      });

      // Add hover effects for buttons
      [clearBtn, maximizeBtn, minimizeBtn, closeBtn].forEach(btn => {
        btn.addEventListener('mouseenter', () => {
          btn.style.backgroundColor = 'rgba(255,255,255,0.2)';
        });
        btn.addEventListener('mouseleave', () => {
          btn.style.backgroundColor = 'transparent';
        });
      });
    }, 0);

    // Add initial welcome message
    this.addMessage('system', 'Welcome! I\'m your chess tutor. I can help analyze this game and answer questions about chess strategy and tactics.');
  }

  startDrag(e) {
    const rect = this.chatWindow.getBoundingClientRect();
    const offsetX = e.clientX - rect.left;
    const offsetY = e.clientY - rect.top;

    const drag = (e) => {
      this.chatWindow.style.left = (e.clientX - offsetX) + 'px';
      this.chatWindow.style.top = (e.clientY - offsetY) + 'px';
      this.chatWindow.style.right = 'auto';
      this.chatWindow.style.bottom = 'auto';
    };

    const stopDrag = () => {
      document.removeEventListener('mousemove', drag);
      document.removeEventListener('mouseup', stopDrag);
    };

    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDrag);
  }

  toggleMaximize() {
    const maximizeBtn = this.chatWindow.querySelector('#maximize-btn');

    if (this.isMaximized) {
      // Restore to original size
      this.chatWindow.style.width = this.originalSize.width;
      this.chatWindow.style.height = this.originalSize.height;
      this.chatWindow.style.top = 'auto';
      this.chatWindow.style.left = 'auto';
      this.chatWindow.style.bottom = '20px';
      this.chatWindow.style.right = '20px';
      maximizeBtn.textContent = '□';
      maximizeBtn.title = 'Maximize';
      this.isMaximized = false;
    } else {
      // Maximize to full screen
      this.chatWindow.style.width = '80vw';
      this.chatWindow.style.height = '80vh';
      this.chatWindow.style.top = '10vh';
      this.chatWindow.style.left = '10vw';
      this.chatWindow.style.bottom = 'auto';
      this.chatWindow.style.right = 'auto';
      maximizeBtn.textContent = '⧉';
      maximizeBtn.title = 'Restore';
      this.isMaximized = true;
    }
  }

  toggleMinimize() {
    const messagesContainer = this.chatWindow.querySelector('#messages-container');
    const inputArea = this.chatWindow.querySelector('div:last-child');
    const minimizeBtn = this.chatWindow.querySelector('#minimize-btn');

    if (this.isMinimized) {
      // Restore from minimized
      if (this.isMaximized) {
        this.chatWindow.style.height = '80vh';
      } else {
        this.chatWindow.style.height = this.originalSize.height;
      }
      messagesContainer.style.display = 'block';
      inputArea.style.display = 'flex';
      minimizeBtn.textContent = '−';
      minimizeBtn.title = 'Minimize';

      // Reset header appearance
      const header = this.chatWindow.querySelector('div:first-child');
      header.style.cursor = 'move';
      header.style.opacity = '1';
      header.onclick = null;

      this.isMinimized = false;
    } else {
      // Minimize - keep header visible with buttons
      this.chatWindow.style.height = '50px';
      messagesContainer.style.display = 'none';
      inputArea.style.display = 'none';
      minimizeBtn.textContent = '□';
      minimizeBtn.title = 'Restore';

      // Add visual indicator when minimized
      const header = this.chatWindow.querySelector('div:first-child');
      header.style.cursor = 'pointer';
      header.style.opacity = '0.9';

      // Make entire header clickable to restore
      header.onclick = (e) => {
        if (e.target === header || e.target.tagName === 'SPAN') {
          this.toggleMinimize();
        }
      };

      this.isMinimized = true;
    }
  }

  closeChatWindow() {
    this.chatWindow.remove();
  }

  clearConversation() {
    this.conversationHistory = [];
    const messagesContainer = this.chatWindow.querySelector('#messages-container');
    messagesContainer.innerHTML = '';
    this.addMessage('system', 'Welcome! I\'m your chess tutor. I can help analyze this game and answer questions about chess strategy and tactics.');
  }


  extractMoves() {
    const moves = [];

    // Extract moves from the new format with <move> elements
    const moveElements = document.querySelectorAll('move');
    
    moveElements.forEach((moveEl, index) => {
      // Extract the move text, excluding move numbers and glyphs
      const moveText = moveEl.textContent.trim();
      
      // Filter out move numbers (like "1.", "2.", etc.) and empty moves
      const cleanMoveText = moveText.replace(/^\d+\.\s*/, '').replace(/[?!]{1,2}$/, '').trim();
      
      if (cleanMoveText && cleanMoveText.length > 1) {
        // Check if this move has a comment
        const nextElement = moveEl.nextElementSibling;
        let comment = null;
        if (nextElement && nextElement.tagName === 'COMMENT') {
          comment = nextElement.textContent.trim();
        }

        // Check for evaluation within the move element
        const evalElement = moveEl.querySelector('eval');
        let evaluation = null;
        if (evalElement) {
          evaluation = evalElement.textContent.trim();
        }

        // Check for alternative lines within the move element
        const lineElements = moveEl.querySelectorAll('line');
        let alternativeLines = [];
        if (lineElements.length > 0) {
          lineElements.forEach(lineEl => {
            const lineMoves = [];
            const lineMovesElements = lineEl.querySelectorAll('move');
            lineMovesElements.forEach(lineMoveEl => {
              const lineMoveText = lineMoveEl.textContent.trim().replace(/^\d+\.\s*/, '').replace(/[?!]{1,2}$/, '').trim();
              if (lineMoveText && lineMoveText.length > 1) {
                lineMoves.push(lineMoveText);
              }
            });
            if (lineMoves.length > 0) {
              alternativeLines.push(lineMoves);
            }
          });
        }

        // Determine move number and color
        const moveNumber = Math.floor(index / 2) + 1;
        const color = index % 2 === 0 ? 'white' : 'black';

        // Check for move annotations (blunder, mistake, etc.)
        const moveClasses = moveEl.className || '';
        let annotation = null;
        if (moveClasses.includes('blunder')) annotation = 'blunder';
        else if (moveClasses.includes('mistake')) annotation = 'mistake';
        else if (moveClasses.includes('inaccuracy')) annotation = 'inaccuracy';
        else if (moveClasses.includes('good')) annotation = 'good';
        else if (moveClasses.includes('brilliant')) annotation = 'brilliant';

        // Check if this is the currently active move
        const isActive = moveClasses.includes('active');

        moves.push({
          moveNumber: moveNumber,
          color: color,
          move: cleanMoveText,
          comment: comment,
          annotation: annotation,
          evaluation: evaluation,
          alternativeLines: alternativeLines,
          isActive: isActive,
          element: moveEl
        });
      }
    });

    // Fallback to old extraction method if no moves found
    if (moves.length === 0) {
      const moveContainers = ['.moves', '.game__moves', '.analyse__moves', '.rmoves', '.tview2'];

      for (const container of moveContainers) {
        const moveList = document.querySelector(container);
        if (moveList) {
          // More comprehensive regex for chess moves
          const moveTexts = moveList.textContent.match(/[a-h][1-8]|[KQRBN][a-h]?[1-8]?x?[a-h][1-8](?:=?[QRBN])?[+#]?|O-O-O|O-O/g);
          if (moveTexts) {
            moveTexts.forEach((move, index) => {
              moves.push({
                moveNumber: Math.floor(index / 2) + 1,
                color: index % 2 === 0 ? 'white' : 'black',
                move: move,
                comment: null,
                annotation: null,
                evaluation: null,
                alternativeLines: [],
                isActive: false
              });
            });
            break;
          }
        }
      }
    }

    return moves;
  }

  extractUserInfo() {
    const userInfo = {
      isLoggedIn: false,
      username: null,
      isOwnGame: false,
      playerColor: null
    };

    // Check if user is logged in
    const userTagElement = document.querySelector('#user_tag.toggle.link');
    if (userTagElement) {
      userInfo.isLoggedIn = true;
      userInfo.username = userTagElement.textContent.trim();
    } else {
      // Check for sign in button to confirm not logged in
      const signInElement = document.querySelector('a.signin[href*="/login"]');
      if (signInElement) {
        userInfo.isLoggedIn = false;
      }
    }

    // If logged in, check if this is their own game
    if (userInfo.isLoggedIn && userInfo.username) {
      const gameInfo = this.extractGameInfo();
      if (gameInfo.white && gameInfo.white.toLowerCase() === userInfo.username.toLowerCase()) {
        userInfo.isOwnGame = true;
        userInfo.playerColor = 'white';
      } else if (gameInfo.black && gameInfo.black.toLowerCase() === userInfo.username.toLowerCase()) {
        userInfo.isOwnGame = true;
        userInfo.playerColor = 'black';
      }
    }

    return userInfo;
  }

  extractGameInfo() {
    const gameInfo = {
      white: null,
      whiteElo: null,
      black: null,
      blackElo: null,
      timeControl: null,
      date: null,
      result: null,
      termination: null,
      site: null,
      event: null
    };

    // Look for game information in study tags table
    const studyTagsTable = document.querySelector('.study__tags.slist');
    if (studyTagsTable) {
      const rows = studyTagsTable.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const th = row.querySelector('th');
        const tdInput = row.querySelector('td input');
        const tdSpan = row.querySelector('td span');
        
        if (th && (tdInput || tdSpan)) {
          const key = th.textContent.trim().toLowerCase();
          // Try input value first, then span text content
          const value = tdInput ? tdInput.value.trim() : (tdSpan ? tdSpan.textContent.trim() : '');
          
          if (value) {
            switch (key) {
              case 'white':
                gameInfo.white = value;
                break;
              case 'whiteelo':
                gameInfo.whiteElo = value;
                break;
              case 'black':
                gameInfo.black = value;
                break;
              case 'blackelo':
                gameInfo.blackElo = value;
                break;
              case 'timecontrol':
                gameInfo.timeControl = value;
                break;
              case 'date':
                gameInfo.date = value;
                break;
              case 'result':
                gameInfo.result = value;
                break;
              case 'termination':
                gameInfo.termination = value;
                break;
              case 'site':
                gameInfo.site = value;
                break;
              case 'event':
                gameInfo.event = value;
                break;
            }
          }
        }
      });
    }

    // Alternative selectors for different page layouts
    if (!gameInfo.white || !gameInfo.black) {
      // Look for player names in other common locations
      const playerSelectors = [
        '.analyse__players .player',
        '.game__meta .player',
        '.study__players .player'
      ];

      playerSelectors.forEach(selector => {
        const players = document.querySelectorAll(selector);
        if (players.length >= 2) {
          gameInfo.white = players[0].textContent.trim();
          gameInfo.black = players[1].textContent.trim();
        }
      });
    }

    return gameInfo;
  }

  extractStockfishEvaluations() {
    const evaluations = [];

    // Look for computer analysis elements
    const evalElements = document.querySelectorAll('.eval, .computer-analysis .eval, [data-eval]');

    evalElements.forEach((evalEl, index) => {
      const evalText = evalEl.textContent || evalEl.getAttribute('data-eval');
      if (evalText) {
        evaluations.push({
          moveIndex: index,
          evaluation: evalText,
          type: evalText.includes('M') ? 'mate' : 'centipawn'
        });
      }
    });

    return evaluations;
  }

  extractFenPosition() {
    // Use the provided selector for FEN position
    const fenInput = document.querySelector('.copy-me.analyse__underboard__fen input');

    if (fenInput && fenInput.value) {
      return fenInput.value;
    }

    // Alternative selectors for FEN position
    const alternativeSelectors = [
      'input[placeholder*="FEN"]',
      'input[value*="rnbqkbnr"]',
      '.fen input',
      '.fen-pgn input',
      '.analyse__underboard input'
    ];

    for (const selector of alternativeSelectors) {
      const input = document.querySelector(selector);
      if (input && input.value && input.value.includes('/')) {
        return input.value;
      }
    }

    return null;
  }

  extractPGN() {
    // Look for PGN data in various locations
    const pgnSelectors = [
      '#main-wrap > main > div.analyse__underboard > div.analyse__underboard__panels > div.fen-pgn.active > div:nth-child(2) > div > textarea',
      '.pgn textarea',
      '.fen-pgn textarea',
      'textarea[placeholder*="PGN"]'
    ];

    for (const selector of pgnSelectors) {
      const pgnElement = document.querySelector(selector);
      if (pgnElement && pgnElement.value) {
        return pgnElement.value;
      }
    }

    return null;
  }

  getCurrentMoveContext() {
    // Try to detect the currently selected/highlighted move
    const context = {
      moveNumber: null,
      move: null,
      fen: null,
      ply: null,
      comment: null,
      annotation: null,
      evaluation: null,
      alternativeLines: []
    };

    // First, try to find the active move from our extracted moves
    const currentMoves = this.extractMoves();
    const activeMove = currentMoves.find(move => move.isActive);
    
    if (activeMove) {
      context.moveNumber = activeMove.moveNumber;
      context.move = activeMove.move;
      context.ply = currentMoves.indexOf(activeMove) + 1;
      context.comment = activeMove.comment;
      context.annotation = activeMove.annotation;
      context.evaluation = activeMove.evaluation;
      context.alternativeLines = activeMove.alternativeLines;
    } else {
      // Fallback to old method for backwards compatibility
      const selectedMoveSelectors = [
        'move.active',
        '.moves .active',
        '.moves .selected',
        '.game__moves .active',
        '.game__moves .selected',
        '.analyse__moves .active',
        '.analyse__moves .selected',
        '.rmoves .active',
        '.rmoves .selected',
        '.tview2 .active',
        '.tview2 .selected'
      ];

      for (const selector of selectedMoveSelectors) {
        const selectedMove = document.querySelector(selector);
        if (selectedMove) {
          const moveText = selectedMove.textContent.trim();
          const cleanMoveText = moveText.replace(/^\d+\.\s*/, '').replace(/[?!]{1,2}$/, '').trim();
          if (cleanMoveText && cleanMoveText.length > 1) {
            // Try to get move number from previous elements or context
            const moveIndex = Array.from(selectedMove.parentElement.children).indexOf(selectedMove);
            context.moveNumber = Math.floor(moveIndex / 2) + 1;
            context.move = cleanMoveText;
            context.ply = moveIndex + 1;
            break;
          }
        }
      }
    }

    // Get current FEN position for additional context
    context.fen = this.extractFenPosition();

    // If no specific move is selected, try to determine from URL or other indicators
    if (!context.move) {
      const urlMatch = window.location.href.match(/\/(\d+)(?:#.*)?$/);
      if (urlMatch) {
        context.ply = parseInt(urlMatch[1]);
        context.moveNumber = Math.ceil(context.ply / 2);
      }
    }

    return context;
  }

  addMessage(sender, content) {
    const messagesContainer = this.chatWindow.querySelector('#messages-container');
    const messageDiv = document.createElement('div');

    messageDiv.style.cssText = `
      margin-bottom: 12px;
      padding: 12px;
      border-radius: 8px;
      border-left: 3px solid ${sender === 'user' ? '#1976d2' : sender === 'system' ? '#4CAF50' : '#ff6b6b'};
      ${sender === 'user' ? 'background: #e8f4fd; margin-left: 20px;' : 'background: white; margin-right: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'}
      line-height: 1.6;
      color: #333;
    `;

    const senderSpan = document.createElement('div');
    senderSpan.style.cssText = `
      font-weight: bold;
      margin-bottom: 6px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: ${sender === 'user' ? '#1976d2' : sender === 'system' ? '#4CAF50' : '#ff6b6b'};
    `;
    senderSpan.textContent = sender === 'user' ? 'You' : sender === 'system' ? 'Tutor' : 'Assistant';

    const contentDiv = document.createElement('div');
    contentDiv.style.cssText = `
      color: #333;
      font-weight: 500;
    `;

    // Parse markdown-like formatting
    if (sender === 'assistant' || sender === 'system') {
      contentDiv.innerHTML = this.parseMarkdown(content);
    } else {
      contentDiv.textContent = content;
    }

    messageDiv.appendChild(senderSpan);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  parseMarkdown(text) {
    // Simple markdown parser for basic formatting
    let html = text;

    // Bold text **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #2c3e50;">$1</strong>');

    // Italic text *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Headers ### text
    html = html.replace(/^### (.*?)$/gm, '<h3 style="color: #2c3e50; margin: 12px 0 8px 0; font-size: 16px;">$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2 style="color: #2c3e50; margin: 14px 0 8px 0; font-size: 18px;">$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1 style="color: #2c3e50; margin: 16px 0 8px 0; font-size: 20px;">$1</h1>');

    // Code blocks ```code```
    html = html.replace(/```(.*?)```/gs, '<code style="background: #f4f4f4; padding: 8px; border-radius: 4px; display: block; margin: 8px 0; font-family: monospace; color: #d63384;">$1</code>');

    // Inline code `code`
    html = html.replace(/`(.*?)`/g, '<code style="background: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-family: monospace; color: #d63384;">$1</code>');

    // Lists - * item
    html = html.replace(/^- (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">• $1</div>');
    html = html.replace(/^\* (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">• $1</div>');

    // Numbered lists
    html = html.replace(/^(\d+)\. (.*?)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">$1. $2</div>');

    // Line breaks
    html = html.replace(/\n\n/g, '<br><br>');
    html = html.replace(/\n/g, '<br>');

    // Chess notation highlighting
    html = html.replace(/\b([KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=?[QRBN])?[+#]?|O-O-O|O-O)\b/g, '<span style="background: #e8f5e8; padding: 1px 3px; border-radius: 3px; font-weight: bold; color: #2e7d32;">$1</span>');

    return html;
  }

  async sendMessage(message) {
    if (!message.trim()) return;

    // Clear input
    const messageInput = this.chatWindow.querySelector('input');
    messageInput.value = '';

    // Extract user and game information when message is sent (ensures DOM is loaded)
    const userInfo = this.extractUserInfo();
    const gameInfo = this.extractGameInfo();

    // Get current move context
    const moveContext = this.getCurrentMoveContext();

    // Append move context to user message
    let enhancedMessage = message;
    if (moveContext.fen) {
      enhancedMessage += `\n\n[Current position FEN: ${moveContext.fen}]`;
    }
    if (moveContext.move && moveContext.moveNumber) {
      let moveDescription = `\n[Currently viewing move ${moveContext.moveNumber}: ${moveContext.move}`;
      
      // If user is logged in and viewing their own game, specify whose move it is
      if (userInfo.isLoggedIn && userInfo.isOwnGame) {
        // Determine whose move this is based on move number and color
        const currentMoveColor = moveContext.ply % 2 === 1 ? 'white' : 'black';
        const isUserMove = currentMoveColor === userInfo.playerColor;
        
        if (isUserMove) {
          moveDescription += ` (YOUR move)`;
        } else {
          moveDescription += ` (OPPONENT'S move)`;
        }
      }
      
      moveDescription += `]`;
      enhancedMessage += moveDescription;
      
      // Add annotation context
      if (moveContext.annotation) {
        enhancedMessage += `\n[Move annotation: ${moveContext.annotation}]`;
      }
      
      // Add evaluation context
      if (moveContext.evaluation) {
        enhancedMessage += `\n[Move evaluation: ${moveContext.evaluation}]`;
      }
      
      // Add comment context
      if (moveContext.comment) {
        enhancedMessage += `\n[Move comment: ${moveContext.comment}]`;
      }
      
      // Add alternative lines context
      if (moveContext.alternativeLines && moveContext.alternativeLines.length > 0) {
        enhancedMessage += `\n[Alternative lines suggested:`;
        moveContext.alternativeLines.forEach((line, index) => {
          enhancedMessage += `\n  Line ${index + 1}: ${line.join(' ')}`;
        });
        enhancedMessage += `]`;
      }
    } else if (moveContext.ply) {
      enhancedMessage += `\n[Currently viewing ply ${moveContext.ply}]`;
    } else if (moveContext.fen) {
      enhancedMessage += `\n[Viewing current board position]`;
    }

    // Add user message (display original message to user)
    this.addMessage('user', message);

    // Check if this is the first user interaction (no conversation history)
    const isFirstMessage = this.conversationHistory.length === 0;

    // Show typing indicator
    this.addMessage('system', 'Thinking...');

    try {
      // Send enhanced message with context to OpenAI
      const response = await this.callOpenAI(enhancedMessage, userInfo, gameInfo);

      // Remove typing indicator
      const messages = this.chatWindow.querySelectorAll('#messages-container > div');
      messages[messages.length - 1].remove();

      // Add personalized greeting for first message
      if (isFirstMessage && userInfo.isLoggedIn) {
        let personalizedGreeting = '';
        if (userInfo.isOwnGame) {
          personalizedGreeting = `Hello ${userInfo.username}! I can see you're analyzing your own game where you played as ${userInfo.playerColor}. `;
        } else {
          personalizedGreeting = `Hello ${userInfo.username}! `;
        }
        this.addMessage('assistant', personalizedGreeting + response);
      } else {
        // Add AI response
        this.addMessage('assistant', response);
      }

    } catch (error) {
      console.error('Error calling OpenAI:', error);

      // Remove typing indicator
      const messages = this.chatWindow.querySelectorAll('#messages-container > div');
      messages[messages.length - 1].remove();

      this.addMessage('system', 'Sorry, I encountered an error. Please check your API key and try again.');
    }
  }

  async callOpenAI(userMessage, userInfo, gameInfo) {
    const systemMessage = this.buildSystemMessage(userInfo, gameInfo);

    // Add current user message to conversation history
    this.conversationHistory.push({ role: 'user', content: userMessage });

    // Build messages array with system message and conversation history
    const messages = [
      { role: 'system', content: systemMessage },
      ...this.conversationHistory
    ];

    console.log(messages)

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: messages,
        max_tokens: 500,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const assistantResponse = data.choices[0].message.content;

    // Add assistant response to conversation history
    this.conversationHistory.push({ role: 'assistant', content: assistantResponse });

    // Keep conversation history manageable (last 10 exchanges)
    if (this.conversationHistory.length > 20) {
      this.conversationHistory = this.conversationHistory.slice(-20);
    }

    return assistantResponse;
  }

  buildSystemMessage(userInfo, gameInfo) {
    let systemMessage = `You are a helpful chess tutor assisting a student in analyzing a chess game. You should provide educational insights about chess strategy, tactics, and gameplay.`;

    // Add user and game context
    
    if (userInfo.isLoggedIn) {
      systemMessage += `\n\nUser: ${userInfo.username}`;
      if (userInfo.isOwnGame) {
        systemMessage += ` (viewing their own game as ${userInfo.playerColor})`;
      } else {
        systemMessage += ` (viewing someone else's game)`;
      }
    } else {
      systemMessage += `\n\nUser: Not logged in (guest viewer)`;
    }

    // Add game information
    if (gameInfo.white || gameInfo.black) {
      systemMessage += `\n\nGame Information:`;
      if (gameInfo.white) systemMessage += `\nWhite: ${gameInfo.white}`;
      if (gameInfo.whiteElo) systemMessage += ` (${gameInfo.whiteElo})`;
      if (gameInfo.black) systemMessage += `\nBlack: ${gameInfo.black}`;
      if (gameInfo.blackElo) systemMessage += ` (${gameInfo.blackElo})`;
      if (gameInfo.timeControl) systemMessage += `\nTime Control: ${gameInfo.timeControl}`;
      if (gameInfo.date) systemMessage += `\nDate: ${gameInfo.date}`;
      if (gameInfo.result) systemMessage += `\nResult: ${gameInfo.result}`;
      if (gameInfo.event) systemMessage += `\nEvent: ${gameInfo.event}`;
    }

    // Extract PGN data for the complete game context
    const currentPgn = this.extractPGN();
    if (currentPgn) {
      systemMessage += `\n\nGame PGN:\n${currentPgn}\n`;
    } else {
      // Fallback to move list if PGN is not available
      const currentMoves = this.extractMoves();
      if (currentMoves.length > 0) {
        systemMessage += `\n\nGame moves:\n`;
        currentMoves.forEach((move, index) => {
          let moveText = `${move.moveNumber}${move.color === 'white' ? '.' : '...'} ${move.move}`;
          
          // Add annotation if present
          if (move.annotation) {
            moveText += ` (${move.annotation})`;
          }
          
          // Add evaluation if present
          if (move.evaluation) {
            moveText += ` [${move.evaluation}]`;
          }
          
          // Mark if this is the active move
          if (move.isActive) {
            moveText += ' <- CURRENT MOVE';
          }
          
          systemMessage += moveText + '\n';
          
          // Add comment if present
          if (move.comment) {
            systemMessage += `  Comment: ${move.comment}\n`;
          }
          
          // Add alternative lines if present
          if (move.alternativeLines && move.alternativeLines.length > 0) {
            move.alternativeLines.forEach((line, lineIndex) => {
              systemMessage += `  Alternative line ${lineIndex + 1}: ${line.join(' ')}\n`;
            });
          }
        });
      }
    }

    // Include Stockfish evaluations if available
    const currentEvaluations = this.extractStockfishEvaluations();
    if (currentEvaluations.length > 0) {
      systemMessage += `\n\nStockfish evaluations:\n`;
      currentEvaluations.forEach((evaluation, index) => {
        systemMessage += `Move ${evaluation.moveIndex + 1}: ${evaluation.evaluation}\n`;
      });
    }

    systemMessage += `\n\nThe user's message will include context about which specific move or position they are currently viewing. Please provide helpful, educational responses about chess concepts, the current position, tactics, and strategy. Keep responses concise but informative.`;

    return systemMessage;
  }
}

// Initialize the chess analyzer when the page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ChessAnalyzer();
  });
} else {
  new ChessAnalyzer();
}
