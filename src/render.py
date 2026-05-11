import json
import os

from src.study_plan import get_challenge_queue, get_lichess_focus_recommendations


def render_html(output_path: str = "output/study.html"):
    """Generate a self-contained HTML study file with all challenges."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    challenges = get_challenge_queue()
    lichess_focus = get_lichess_focus_recommendations()

    # Compute weakness summary by concept
    concept_counts: dict[str, int] = {}
    for c in challenges:
        concept = c.get('concept') or 'general'
        concept_counts[concept] = concept_counts.get(concept, 0) + 1

    challenges_json = json.dumps(challenges, ensure_ascii=False)
    concept_counts_json = json.dumps(concept_counts, ensure_ascii=False)
    lichess_focus_json = json.dumps(lichess_focus, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chess Study — tbonez</title>

  <!-- chessboard.js 1.0.0 -->
  <link rel="stylesheet"
        href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css"
        crossorigin="anonymous">

  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}

    :root {{
      --bg: #1a1a2e;
      --surface: #16213e;
      --surface2: #0f3460;
      --accent: #e94560;
      --accent2: #533483;
      --text: #eaeaea;
      --text-muted: #888;
      --green: #4caf50;
      --red: #e94560;
      --border: #2a2a4a;
    }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
    }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    header h1 {{
      margin: 0;
      font-size: 1.4rem;
      color: var(--accent);
      letter-spacing: 0.05em;
    }}

    #stats {{
      display: flex;
      gap: 1.5rem;
      font-size: 0.9rem;
      color: var(--text-muted);
    }}

    #stats span {{ color: var(--text); font-weight: 600; }}

    .main-layout {{
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 0;
      min-height: calc(100vh - 60px);
    }}

    /* Sidebar */
    .sidebar {{
      background: var(--surface);
      border-right: 1px solid var(--border);
      padding: 1.5rem 1rem;
      overflow-y: auto;
    }}

    .sidebar h2 {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin: 0 0 1rem 0;
    }}

    .concept-bar {{
      margin-bottom: 0.6rem;
    }}

    .focus-list {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      margin-bottom: 1.75rem;
    }}

    .focus-card {{
      background: rgba(15, 52, 96, 0.45);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 0.8rem;
    }}

    .focus-card-top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 0.35rem;
    }}

    .focus-theme {{
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--text);
    }}

    .focus-count {{
      color: var(--accent);
      font-size: 0.78rem;
      font-weight: 700;
      white-space: nowrap;
    }}

    .focus-reason {{
      margin: 0;
      color: var(--text-muted);
      font-size: 0.8rem;
      line-height: 1.45;
    }}

    .concept-label {{
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      margin-bottom: 0.2rem;
    }}

    .concept-name {{ color: var(--text); text-transform: capitalize; }}
    .concept-count {{ color: var(--accent); font-weight: 700; }}

    .bar-track {{
      height: 6px;
      background: var(--border);
      border-radius: 3px;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, var(--accent2), var(--accent));
      border-radius: 3px;
      transition: width 0.4s ease;
    }}

    /* Main area */
    .challenge-area {{
      padding: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }}

    .challenge-header {{
      width: 100%;
      max-width: 600px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .concept-badge {{
      background: var(--accent2);
      color: var(--text);
      padding: 0.3rem 0.8rem;
      border-radius: 20px;
      font-size: 0.8rem;
      text-transform: capitalize;
      font-weight: 600;
    }}

    .progress-text {{
      color: var(--text-muted);
      font-size: 0.85rem;
    }}

    .streak {{
      color: #ffd700;
      font-weight: 700;
      font-size: 0.9rem;
    }}

    /* Board */
    #board-container {{
      width: 100%;
      max-width: 480px;
      aspect-ratio: 1;
    }}

    #board {{ width: 100%; }}

    /* Context */
    .context-box {{
      width: 100%;
      max-width: 480px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1rem 1.2rem;
    }}

    .context-box h3 {{
      margin: 0 0 0.5rem 0;
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
    }}

    .context-box p {{
      margin: 0;
      font-size: 0.95rem;
      line-height: 1.5;
    }}

    .instruction {{
      color: var(--accent);
      font-style: italic;
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }}

    /* Feedback */
    .feedback-box {{
      width: 100%;
      max-width: 480px;
      border-radius: 8px;
      padding: 1rem 1.2rem;
      border-left: 4px solid;
      display: none;
    }}

    .feedback-box.correct {{
      background: rgba(76, 175, 80, 0.15);
      border-color: var(--green);
    }}

    .feedback-box.incorrect {{
      background: rgba(233, 69, 96, 0.15);
      border-color: var(--red);
    }}

    .feedback-box h3 {{
      margin: 0 0 0.4rem 0;
      font-size: 1rem;
    }}

    .feedback-box.correct h3 {{ color: var(--green); }}
    .feedback-box.incorrect h3 {{ color: var(--red); }}

    .feedback-box p {{
      margin: 0;
      font-size: 0.9rem;
      line-height: 1.55;
      color: var(--text);
    }}

    .move-comparison {{
      margin-top: 0.6rem;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .move-comparison span {{ color: var(--text); font-weight: 600; }}

    /* Buttons */
    .btn-row {{
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    button {{
      padding: 0.65rem 1.4rem;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
    }}

    button:hover {{ opacity: 0.85; }}
    button:active {{ transform: scale(0.98); }}
    button:disabled {{ opacity: 0.4; cursor: not-allowed; }}

    #btn-submit {{
      background: var(--accent);
      color: #fff;
    }}

    #btn-next {{
      background: var(--surface2);
      color: var(--text);
      display: none;
    }}

    #empty-state {{
      text-align: center;
      color: var(--text-muted);
      padding: 4rem 2rem;
    }}

    #empty-state h2 {{ color: var(--text); margin-bottom: 0.5rem; }}
  </style>
</head>
<body>

<header>
  <h1>Chess Study Board</h1>
  <div id="stats">
    Challenge <span id="stat-current">1</span> of <span id="stat-total">0</span>
    &nbsp;|&nbsp; Streak: <span class="streak" id="stat-streak">0</span>
  </div>
</header>

<div class="main-layout">
  <!-- Sidebar: weakness summary -->
  <aside class="sidebar">
    <h2>Lichess Puzzle Focus</h2>
    <div id="focus-list"></div>

    <h2>Weakness Summary</h2>
    <div id="concept-list"></div>
  </aside>

  <!-- Main challenge area -->
  <main class="challenge-area" id="challenge-area">
    <div id="empty-state" style="display:none;">
      <h2>All caught up!</h2>
      <p>No challenges available. Run the pipeline to generate more.</p>
    </div>

    <div class="challenge-header" id="challenge-header">
      <span class="concept-badge" id="concept-badge">concept</span>
      <span class="progress-text" id="progress-text">1 / 1</span>
    </div>

    <div id="board-container">
      <div id="board"></div>
    </div>

    <div class="context-box" id="context-box">
      <h3>Position Context</h3>
      <p id="context-text"></p>
      <p class="instruction" id="instruction-text">Find the best move — drag a piece on the board, then click Submit.</p>
    </div>

    <div class="btn-row">
      <button id="btn-submit">Submit Move</button>
      <button id="btn-next">Next Challenge →</button>
    </div>

    <div class="feedback-box" id="feedback-box">
      <h3 id="feedback-title"></h3>
      <p id="feedback-explanation"></p>
      <div class="move-comparison" id="move-comparison"></div>
    </div>
  </main>
</div>

<!-- chess.js -->
<script src="https://unpkg.com/chess.js@0.10.3/chess.js"></script>
<!-- chessboard.js -->
<script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"
        crossorigin="anonymous"></script>
<!-- jQuery (required by chessboard.js) -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"
        crossorigin="anonymous"></script>

<script>
// ─── Embedded data ───────────────────────────────────────────────────────────
const CHALLENGES = {challenges_json};
const CONCEPT_COUNTS = {concept_counts_json};
const LICHESS_FOCUS = {lichess_focus_json};

// ─── State ───────────────────────────────────────────────────────────────────
let currentIndex = 0;
let streak = 0;
let board = null;
let game = null;
let pendingMove = null;   // {{ from, to }} of the user's attempted move
let submitted = false;

// ─── localStorage helpers ─────────────────────────────────────────────────────
function getProgress() {{
  try {{ return JSON.parse(localStorage.getItem('chess_progress') || '{{}}'); }}
  catch(e) {{ return {{}}; }}
}}

function saveProgress(p) {{
  localStorage.setItem('chess_progress', JSON.stringify(p));
}}

// ─── Sidebar ──────────────────────────────────────────────────────────────────
function renderSidebar() {{
  const focusList = document.getElementById('focus-list');
  focusList.innerHTML = '';
  LICHESS_FOCUS.forEach((item) => {{
    focusList.innerHTML += `
      <div class="focus-card">
        <div class="focus-card-top">
          <span class="focus-theme">${{item.theme}}</span>
          <span class="focus-count">${{item.count}} spots</span>
        </div>
        <p class="focus-reason">${{item.reason}}</p>
      </div>`;
  }});

  const list = document.getElementById('concept-list');
  list.innerHTML = '';
  const entries = Object.entries(CONCEPT_COUNTS).sort((a,b) => b[1]-a[1]);
  const max = entries.length ? entries[0][1] : 1;
  entries.forEach(([concept, count]) => {{
    const pct = Math.round(count / max * 100);
    list.innerHTML += `
      <div class="concept-bar">
        <div class="concept-label">
          <span class="concept-name">${{concept.replace(/_/g,' ')}}</span>
          <span class="concept-count">${{count}}</span>
        </div>
        <div class="bar-track"><div class="bar-fill" style="width:${{pct}}%"></div></div>
      </div>`;
  }});
}}

// ─── Board helpers ────────────────────────────────────────────────────────────
function onDragStart(source, piece, position, orientation) {{
  // only allow moving the current player's pieces
  if (submitted) return false;
  if (orientation === 'white' && piece.search(/^b/) !== -1) return false;
  if (orientation === 'black' && piece.search(/^w/) !== -1) return false;
  return true;
}}

function onDrop(source, target) {{
  if (submitted) return 'snapback';
  if (source === target) return 'snapback';

  // Validate move with chess.js
  const move = game.move({{ from: source, to: target, promotion: 'q' }});
  if (move === null) return 'snapback';

  // Undo so board stays at challenge position (we re-apply after submit)
  game.undo();

  pendingMove = {{ from: source, to: target }};
  document.getElementById('instruction-text').textContent =
    `You selected ${{source}}→${{target}}. Click Submit to confirm.`;
}}

function onSnapEnd() {{
  board.position(game.fen());
}}

// ─── Load challenge ───────────────────────────────────────────────────────────
function loadChallenge(idx) {{
  if (CHALLENGES.length === 0) {{
    document.getElementById('challenge-area').innerHTML = '';
    document.getElementById('empty-state').style.display = 'block';
    return;
  }}

  const c = CHALLENGES[idx];
  submitted = false;
  pendingMove = null;

  // Header
  document.getElementById('concept-badge').textContent = (c.concept||'general').replace(/_/g,' ');
  document.getElementById('progress-text').textContent = `${{idx+1}} / ${{CHALLENGES.length}}`;
  document.getElementById('stat-current').textContent = idx+1;
  document.getElementById('stat-total').textContent = CHALLENGES.length;
  document.getElementById('stat-streak').textContent = streak;

  // Context
  document.getElementById('context-text').textContent = c.context || '';
  document.getElementById('instruction-text').textContent =
    'Find the best move — drag a piece on the board, then click Submit.';

  // Hide feedback / next
  const fb = document.getElementById('feedback-box');
  fb.style.display = 'none';
  fb.className = 'feedback-box';
  document.getElementById('btn-next').style.display = 'none';
  document.getElementById('btn-submit').disabled = false;

  // Chess.js + board
  game = new Chess(c.fen);
  const orientation = c.user_color || 'white';

  if (board) {{
    board.destroy();
  }}

  board = Chessboard('board', {{
    position: c.fen,
    orientation: orientation,
    draggable: true,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    pieceTheme: 'https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/img/chesspieces/wikipedia/{{piece}}.png',
  }});
}}

// ─── Submit ───────────────────────────────────────────────────────────────────
function handleSubmit() {{
  if (submitted) return;
  submitted = true;

  const c = CHALLENGES[currentIndex];

  let userUci = '';
  if (pendingMove) {{
    userUci = pendingMove.from + pendingMove.to;
  }}

  const correctUci = (c.correct_move_uci || '').toLowerCase().substring(0,4);
  const isCorrect = userUci.length >= 4 &&
                    userUci.substring(0,4) === correctUci;

  // Update localStorage progress
  const progress = getProgress();
  const key = String(c.id);
  if (!progress[key]) progress[key] = {{ times_seen: 0, times_correct: 0 }};
  progress[key].times_seen++;
  progress[key].last_seen = new Date().toISOString();
  if (isCorrect) {{
    progress[key].times_correct++;
    streak++;
  }} else {{
    streak = 0;
  }}
  saveProgress(progress);

  document.getElementById('stat-streak').textContent = streak;

  // Show feedback
  const fb = document.getElementById('feedback-box');
  fb.style.display = 'block';
  fb.className = 'feedback-box ' + (isCorrect ? 'correct' : 'incorrect');
  document.getElementById('feedback-title').textContent =
    isCorrect ? '✓ Correct!' : '✗ Not quite';
  document.getElementById('feedback-explanation').textContent =
    c.explanation || 'No explanation available.';

  const comparison = document.getElementById('move-comparison');
  if (!isCorrect) {{
    comparison.innerHTML = `You played: <span>${{c.user_move_san || userUci || '?'}}</span> &nbsp;|&nbsp; ` +
                           `Better: <span>${{c.correct_move_san || correctUci || '?'}}</span>`;
  }} else {{
    comparison.innerHTML = `Best move: <span>${{c.correct_move_san || correctUci}}</span>`;
  }}

  // Show correct move on board
  if (c.correct_move_uci && c.correct_move_uci.length >= 4) {{
    const from = c.correct_move_uci.substring(0,2);
    const to   = c.correct_move_uci.substring(2,4);
    game.move({{ from, to, promotion: 'q' }});
    board.position(game.fen());
  }}

  document.getElementById('btn-submit').disabled = true;
  document.getElementById('btn-next').style.display = 'inline-block';
}}

// ─── Next ─────────────────────────────────────────────────────────────────────
function handleNext() {{
  currentIndex = (currentIndex + 1) % CHALLENGES.length;
  loadChallenge(currentIndex);
}}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.getElementById('btn-submit').addEventListener('click', handleSubmit);
document.getElementById('btn-next').addEventListener('click', handleNext);

renderSidebar();
if (CHALLENGES.length > 0) {{
  loadChallenge(0);
}} else {{
  document.getElementById('challenge-header').style.display = 'none';
  document.getElementById('board-container').style.display = 'none';
  document.getElementById('context-box').style.display = 'none';
  document.querySelector('.btn-row').style.display = 'none';
  document.getElementById('empty-state').style.display = 'block';
}}
</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Rendered {len(challenges)} challenges to {output_path}")
