# AI Chess Tutor — PRD

## Overview

An experimental AI-powered chess tutor for a single user. The system analyzes the user's game history using Stockfish and LLM reasoning to identify recurring weaknesses, explain the *why* behind mistakes, and generate study material that requires active engagement rather than passive review.

The core insight: Stockfish tells you *what* the best move is. This system explains *why*, traces mistakes to their root causes, and structures practice around productive struggle.

---

## Data Pipeline

### Step 1 — PGN Ingestion

User downloads PGN files from their chess platform (Chess.com, Lichess). Each game contains:
- Moves and result
- Opponent rating and color played
- Time control
- Opening ECO code (if provided)
- Per-move clock times (if available — useful for detecting time pressure decisions)

### Step 2 — Stockfish Analysis

Run Stockfish on every position in every game. Extract per move:
- Centipawn evaluation (from the moving player's perspective)
- Eval delta vs. previous move
- Best engine move
- Top 2-3 alternative lines with evaluations
- Whether the position is tactical (sharp) or positional (stable)

Store raw analysis alongside the PGN so downstream steps can re-query without re-running the engine.

### Step 3 — Per-Game Structured Analysis

For each game, produce a structured record (not just a prose summary) covering three phases.

**Opening (moves 1–~15, until piece development complete)**

- Identify opening name and ECO code
- Compare moves against opening theory; flag deviations
- Eval threshold for flagging: >0.2 delta
- For each deviation: what principle was violated (center control, development tempo, king safety, pawn structure)
- Structural features at opening exit: pawn islands, open files, piece activity, king safety score

**Middlegame (~15–40, until material simplification begins)**

- Eval threshold for flagging: >0.5 delta
- For each flagged moment: categorize the concept (tactics, piece coordination, weak square, open file, king attack, positional exchange)
- Causal tracing: when a large eval shift occurs, identify the earliest move that created the losing condition — often 5–15 moves earlier
- Track structural feature changes across the phase (not just individual moves)

**Endgame (~40+)**

- Eval threshold for flagging: >1.0 (or >0.3 in known technical endgames)
- Different conceptual vocabulary: king activity, pawn promotion, opposition, zugzwang, piece coordination
- Identify endgame type (K+P, rook, minor piece) and whether technique was sound

**Cross-phase summary fields (structured, not prose)**

```
opening_deviation: bool
opening_principle_violated: str | null
phase_most_ground_lost: "opening" | "middlegame" | "endgame"
turning_point_move: int
turning_point_category: str
causal_root_move: int | null
result: "win" | "loss" | "draw"
opponent_rating: int
time_control: str
```

### Step 4 — Clustering

Cluster games by structured features, not text summaries. Cluster inputs:

- Opening played (ECO family)
- Phase where most eval was lost
- Concept category of turning point
- Result

Use text summaries as human-readable cluster labels, not as embedding inputs. Goal: surface patterns like "you lose positional games from the opening when playing the French" or "your tactical losses cluster around piece coordination in the middlegame."

Minimum meaningful cluster size: 3 games. Surface top 3 clusters by frequency.

### Step 5 — Weakness Identification and Study Plan

From clusters, rank weaknesses by:
1. Frequency (how often does this pattern appear)
2. Impact (how much eval is lost on average when it occurs)
3. Phase (opening weaknesses ranked higher — they compound)

Output a prioritized list of concept areas to study, each with:
- The weakness in plain language
- Representative game positions that illustrate it
- Estimated frequency and impact

---

## Study Material

### Design Principle: Productive Struggle

Research shows unrestricted access to engine analysis halves learning gains versus structured delivery. All study material must:
- Require the user to commit to a move or plan before seeing any analysis
- Withhold eval bars entirely during the attempt phase
- Reveal engine lines only after submission, with plain-language explanation of the why
- Progressively reduce hints for concepts seen before (spaced retrieval)

### Study Unit: Position Challenge

The core study atom. Each challenge is a position extracted from the user's own games.

```
Position: [board state]
Context: "Move 14, you're playing Black. You've just played Bd6."
Prompt: "What would you play here?"

[User submits move]

→ Reveal:
  - What you actually played in the game
  - What Stockfish prefers
  - Why in plain language: "Nf6 allows White to establish a strong knight on e5,
    which you can never easily remove. The engine's c5 fights for that square immediately."
  - If opening deviation: the positional principle being violated
  - If tactical miss: the full combination shown step by step
  - If positional drift: trace back to the move where the weakness originated
```

Never show the concept category before the attempt — labeling it "this is a weak square problem" eliminates the recognition challenge.

### Study Unit: Comparison Challenge

For opening deviations. Show two resulting positions side by side — the theoretical move and the user's move — after 3–4 more moves.

Prompt: "These positions arose from the same opening. What's structurally different?"

User writes a short answer, then sees the explanation. Forces active comparison rather than passive reading.

### Study Unit: Concept Drill Set

After clustering identifies a recurring weakness, generate a set of 5–10 positions sharing the same underlying concept — drawn from the user's games and supplemented with master game positions illustrating the same theme.

Presented as a sequential queue. No labels, no hints. Concept name revealed only after completing the set.

### Study Queue

The study plan output is a prioritized queue of challenges, not a report to read. Ordered by:
1. Concept priority (from weakness ranking)
2. Spaced repetition schedule (concepts answered correctly recede; missed ones resurface sooner)

---

## Form Factor

### Phase 1 — CLI + Static Web Output

Given this is a single-user experimental project, minimize infrastructure:

- Python script ingests PGN files, runs Stockfish, calls LLM API for analysis
- Outputs a static HTML file: the study queue rendered as an interactive chess board
- User opens HTML file in browser, works through challenges locally
- No server, no auth, no database — just files

Board interaction: use an existing JavaScript chess board library (chessboard.js or similar) embedded in the HTML output. User makes moves on the board, clicks "Submit", then sees the reveal.

Progress state stored in localStorage so the queue persists across sessions.

### Phase 2 — Ongoing Analysis (future)

Re-run the pipeline incrementally as new games are played. New games feed into existing clusters, updating the weakness ranking and appending to the study queue.

---

## Technical Notes

- Stockfish is the source of truth for move correctness. LLM is used only for natural language reasoning and concept categorization — never for generating or evaluating chess lines.
- Phase boundaries are detected programmatically, not by fixed move number: opening ends when both sides complete development (castled + minor pieces developed), endgame begins when queens are traded or material drops below a threshold.
- Clock time data (if present in PGN) can flag time-pressure moves — useful context for the LLM when explaining why a blunder occurred, and potentially worth discounting in weakness analysis.
- LLM prompts should include the full position FEN, the Stockfish top lines with evaluations, and the structured phase context — not raw PGN — to minimize hallucination risk.
