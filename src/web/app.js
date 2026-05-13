const PIECE_URLS = {
  wp: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wp.png',
  wn: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wn.png',
  wb: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wb.png',
  wr: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wr.png',
  wq: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wq.png',
  wk: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/wk.png',
  bp: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bp.png',
  bn: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bn.png',
  bb: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bb.png',
  br: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/br.png',
  bq: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bq.png',
  bk: 'https://images.chesscomfiles.com/chess-themes/pieces/neo/150/bk.png',
};

const state = {
  data: null,
  currentIndex: 0,
  streak: 0,
  game: null,
  playerColor: 'white',
  pendingMove: null,
  submitted: false,
  selectedSquare: null,
  legalTargets: [],
  dragState: null,
};

function getProgress() {
  try {
    return JSON.parse(localStorage.getItem('chess_progress') || '{}');
  } catch {
    return {};
  }
}

function saveProgress(progress) {
  localStorage.setItem('chess_progress', JSON.stringify(progress));
}

function ownColor() {
  return state.playerColor === 'white' ? 'w' : 'b';
}

function pieceKey(piece) {
  return piece ? `${piece.color}${piece.type}` : null;
}

function clearSelection() {
  state.selectedSquare = null;
  state.legalTargets = [];
}

function removeWindowDragListeners() {
  window.removeEventListener('pointermove', handlePointerMove);
  window.removeEventListener('pointerup', handlePointerUp);
  window.removeEventListener('pointercancel', handlePointerCancel);
}

function removeDragGhost() {
  document.getElementById('drag-ghost')?.remove();
}

function clearDragState() {
  removeWindowDragListeners();
  removeDragGhost();
  state.dragState = null;
}

function createDragGhost(src, x, y) {
  removeDragGhost();
  const ghost = document.createElement('img');
  ghost.id = 'drag-ghost';
  ghost.className = 'drag-ghost';
  ghost.src = src;
  ghost.alt = '';
  document.body.appendChild(ghost);
  moveDragGhost(x, y);
}

function moveDragGhost(x, y) {
  const ghost = document.getElementById('drag-ghost');
  if (!ghost) return;
  ghost.style.left = `${x}px`;
  ghost.style.top = `${y}px`;
}

function updateHeader() {
  const total = state.data.challenges.length;
  document.getElementById('stat-current').textContent = total ? String(state.currentIndex + 1) : '0';
  document.getElementById('stat-total').textContent = String(total);
  document.getElementById('stat-streak').textContent = String(state.streak);
}

function renderSidebar() {
  const focusList = document.getElementById('focus-list');
  focusList.innerHTML = '';
  state.data.lichess_focus.forEach((item) => {
    const card = document.createElement('div');
    card.className = 'focus-card';
    card.innerHTML = `
      <div class="focus-card-top">
        <span class="focus-theme">${item.theme}</span>
        <span class="focus-count">${item.count} spots</span>
      </div>
      <p class="focus-reason">${item.reason}</p>
    `;
    focusList.appendChild(card);
  });

  const conceptList = document.getElementById('concept-list');
  conceptList.innerHTML = '';
  const entries = Object.entries(state.data.concept_counts).sort((a, b) => b[1] - a[1]);
  const max = entries.length ? entries[0][1] : 1;

  entries.forEach(([concept, count]) => {
    const wrap = document.createElement('div');
    wrap.className = 'concept-bar';
    wrap.innerHTML = `
      <div class="concept-label">
        <span class="concept-name">${concept.replace(/_/g, ' ')}</span>
        <span class="concept-count">${count}</span>
      </div>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round((count / max) * 100)}%"></div></div>
    `;
    conceptList.appendChild(wrap);
  });
}

function getDisplayedSquares() {
  const files = state.playerColor === 'black'
    ? ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    : ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = state.playerColor === 'black'
    ? [1, 2, 3, 4, 5, 6, 7, 8]
    : [8, 7, 6, 5, 4, 3, 2, 1];

  const squares = [];
  ranks.forEach((rank, rankIndex) => {
    files.forEach((file, fileIndex) => {
      squares.push({ name: `${file}${rank}`, file, rank, fileIndex, rankIndex });
    });
  });
  return squares;
}

function squareColor(fileIndex, rankIndex) {
  return (fileIndex + rankIndex) % 2 === 0 ? 'light' : 'dark';
}

function renderBoard() {
  const board = document.getElementById('board');
  board.innerHTML = '';

  getDisplayedSquares().forEach((square) => {
    const piece = state.game.get(square.name);
    const ownPiece = piece && piece.color === ownColor();
    const el = document.createElement('div');
    el.className = `square ${squareColor(square.fileIndex, square.rankIndex)}`;
    el.dataset.square = square.name;

    if (state.selectedSquare === square.name) el.classList.add('selected');
    if (state.pendingMove && (state.pendingMove.from === square.name || state.pendingMove.to === square.name)) el.classList.add('pending');
    if (state.legalTargets.includes(square.name)) el.classList.add('target');
    if (state.dragState?.hoverSquare === square.name) el.classList.add('drop-target');

    const showRank = state.playerColor === 'white' ? square.file === 'a' : square.file === 'h';
    const showFile = state.playerColor === 'white' ? square.rank === 1 : square.rank === 8;

    if (showRank) {
      const label = document.createElement('span');
      label.className = 'square-label rank';
      label.textContent = String(square.rank);
      el.appendChild(label);
    }
    if (showFile) {
      const label = document.createElement('span');
      label.className = 'square-label file';
      label.textContent = square.file;
      el.appendChild(label);
    }

    if (piece) {
      const img = document.createElement('img');
      img.className = 'piece';
      img.alt = '';
      img.src = PIECE_URLS[pieceKey(piece)];
      if (!state.submitted && ownPiece) {
        img.addEventListener('pointerdown', (event) => handlePointerDown(event, square.name));
      }
      el.appendChild(img);
    }

    el.addEventListener('click', () => handleSquareClick(square.name));
    board.appendChild(el);
  });
}

function setPendingMove(from, to) {
  state.pendingMove = { from, to };
  clearSelection();
  document.getElementById('instruction-text').textContent = `Selected ${from}→${to}. Click Submit to confirm.`;
}

function tryStageMove(from, to) {
  const move = state.game.move({ from, to, promotion: 'q' });
  if (!move) return false;
  state.game.undo();
  setPendingMove(from, to);
  return true;
}

function handleSquareClick(square) {
  if (state.submitted || state.dragState) return;

  const piece = state.game.get(square);
  if (state.selectedSquare) {
    if (tryStageMove(state.selectedSquare, square)) {
      renderBoard();
      return;
    }
  }

  if (piece && piece.color === ownColor()) {
    state.selectedSquare = square;
    state.pendingMove = null;
    state.legalTargets = state.game.moves({ square, verbose: true }).map((move) => move.to);
    document.getElementById('instruction-text').textContent = `Selected ${square}. Choose a destination square.`;
  } else {
    state.pendingMove = null;
    clearSelection();
    document.getElementById('instruction-text').textContent = 'Find the best move.';
  }

  renderBoard();
}

function handlePointerDown(event, square) {
  if (state.submitted || event.button !== 0) return;

  const piece = state.game.get(square);
  if (!piece || piece.color !== ownColor()) return;

  event.preventDefault();
  state.pendingMove = null;
  state.selectedSquare = square;
  state.legalTargets = state.game.moves({ square, verbose: true }).map((move) => move.to);
  state.dragState = {
    from: square,
    pointerId: event.pointerId,
    moved: false,
    hoverSquare: null,
    pieceSrc: PIECE_URLS[pieceKey(piece)],
  };

  createDragGhost(state.dragState.pieceSrc, event.clientX, event.clientY);
  window.addEventListener('pointermove', handlePointerMove);
  window.addEventListener('pointerup', handlePointerUp);
  window.addEventListener('pointercancel', handlePointerCancel);
  renderBoard();
}

function updateDragHover(clientX, clientY) {
  const el = document.elementFromPoint(clientX, clientY);
  const squareEl = el ? el.closest('[data-square]') : null;
  const square = squareEl?.dataset.square || null;
  const legal = square && square !== state.dragState.from && state.legalTargets.includes(square);
  state.dragState.hoverSquare = legal ? square : null;
}

function handlePointerMove(event) {
  if (!state.dragState || event.pointerId !== state.dragState.pointerId) return;
  state.dragState.moved = true;
  moveDragGhost(event.clientX, event.clientY);
  updateDragHover(event.clientX, event.clientY);
  renderBoard();
}

function finalizePointerDrag(cancelled = false) {
  const drag = state.dragState;
  if (!drag) return;

  const hoverSquare = drag.hoverSquare;
  const moved = drag.moved;

  clearDragState();

  if (cancelled) {
    renderBoard();
    return;
  }

  if (hoverSquare) {
    const staged = tryStageMove(drag.from, hoverSquare);
    if (!staged) {
      document.getElementById('instruction-text').textContent = 'That move is not legal in this position.';
    }
    renderBoard();
    return;
  }

  if (!moved) {
    state.selectedSquare = drag.from;
    state.legalTargets = state.game.moves({ square: drag.from, verbose: true }).map((move) => move.to);
    document.getElementById('instruction-text').textContent = `Selected ${drag.from}. Choose a destination square.`;
  }

  renderBoard();
}

function handlePointerUp(event) {
  if (!state.dragState || event.pointerId !== state.dragState.pointerId) return;
  finalizePointerDrag(false);
}

function handlePointerCancel(event) {
  if (!state.dragState || event.pointerId !== state.dragState.pointerId) return;
  finalizePointerDrag(true);
}

function loadChallenge(index) {
  const c = state.data.challenges[index];
  state.currentIndex = index;
  state.submitted = false;
  state.pendingMove = null;
  clearSelection();
  clearDragState();
  state.game = new Chess(c.fen);
  state.playerColor = c.user_color || 'white';

  document.getElementById('concept-badge').textContent = (c.concept || 'general').replace(/_/g, ' ');
  document.getElementById('progress-text').textContent = `${index + 1} / ${state.data.challenges.length}`;
  document.getElementById('context-text').textContent = c.context || '';
  document.getElementById('instruction-text').textContent = 'Find the best move.';
  document.getElementById('btn-submit').disabled = false;
  document.getElementById('btn-next').hidden = true;
  document.getElementById('feedback-box').hidden = true;

  const link = document.getElementById('game-link');
  link.href = c.game_url;
  link.textContent = `Open ${c.game_id} on Lichess`;

  updateHeader();
  renderBoard();
}

function handleSubmit() {
  if (state.submitted) return;
  state.submitted = true;

  const c = state.data.challenges[state.currentIndex];
  const userUci = state.pendingMove ? state.pendingMove.from + state.pendingMove.to : '';
  const correctUci = (c.correct_move_uci || '').toLowerCase().slice(0, 4);
  const isCorrect = userUci.length >= 4 && userUci.slice(0, 4) === correctUci;

  const progress = getProgress();
  const key = String(c.id);
  if (!progress[key]) progress[key] = { times_seen: 0, times_correct: 0 };
  progress[key].times_seen += 1;
  if (isCorrect) {
    progress[key].times_correct += 1;
    state.streak += 1;
  } else {
    state.streak = 0;
  }
  saveProgress(progress);
  updateHeader();

  const feedback = document.getElementById('feedback-box');
  feedback.hidden = false;
  feedback.className = `feedback-box panel ${isCorrect ? 'correct' : 'incorrect'}`;
  document.getElementById('feedback-title').textContent = isCorrect ? 'Correct' : 'Not quite';
  document.getElementById('feedback-explanation').textContent = c.explanation || 'No explanation available.';
  document.getElementById('move-comparison').innerHTML = isCorrect
    ? `Best move: <span>${c.correct_move_san || correctUci}</span>`
    : `You played: <span>${c.user_move_san || userUci || '?'}</span> | Better: <span>${c.correct_move_san || correctUci || '?'}</span>`;

  if (c.correct_move_uci && c.correct_move_uci.length >= 4) {
    state.game.move({
      from: c.correct_move_uci.slice(0, 2),
      to: c.correct_move_uci.slice(2, 4),
      promotion: 'q',
    });
  }

  state.pendingMove = null;
  clearSelection();
  renderBoard();
  document.getElementById('btn-submit').disabled = true;
  document.getElementById('btn-next').hidden = false;
}

function handleNext() {
  if (!state.data.challenges.length) return;
  loadChallenge((state.currentIndex + 1) % state.data.challenges.length);
}

async function init() {
  const response = await fetch('study-data.json');
  state.data = await response.json();

  renderSidebar();

  document.getElementById('btn-submit').addEventListener('click', handleSubmit);
  document.getElementById('btn-next').addEventListener('click', handleNext);

  if (!state.data.challenges.length) {
    document.getElementById('empty-state').hidden = false;
    document.getElementById('challenge-shell').hidden = true;
    return;
  }

  updateHeader();
  loadChallenge(0);
}

init().catch((error) => {
  console.error(error);
  document.getElementById('empty-state').hidden = false;
  document.getElementById('empty-state').innerHTML = '<h2>Failed to load study data</h2><p>Check the browser console for details.</p>';
  document.getElementById('challenge-shell').hidden = true;
});
