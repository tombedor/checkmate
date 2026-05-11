import io
import json
import os

import anthropic
import chess
import chess.pgn
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from src.db import get_conn

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are an expert chess coach analyzing games to create educational study material.
Your goal is to identify the most instructive moments where the player made mistakes,
explain WHY the better move is superior in plain language, and categorize the type of error.
Focus on teaching concepts, not just listing mistakes. Be concise but insightful."""


def _uci_to_san(fen: str, uci: str) -> str:
    """Convert a UCI move string to SAN notation given a FEN position."""
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(uci)
        return board.san(move)
    except Exception:
        return uci


def analyze_games_llm(limit: int = 100):
    """Run LLM analysis on games that have positions but no game_analysis entry."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    conn = get_conn()
    cur = conn.cursor()

    # Games that have positions analyzed but no game_analysis yet
    rows = cur.execute("""
        SELECT g.id, g.white, g.black, g.user_color, g.white_elo, g.black_elo,
               g.result, g.user_result, g.time_control, g.eco, g.opening, g.pgn
        FROM games g
        WHERE EXISTS (SELECT 1 FROM positions p WHERE p.game_id = g.id)
          AND NOT EXISTS (SELECT 1 FROM game_analysis ga WHERE ga.game_id = g.id)
        ORDER BY g.instructiveness_score DESC NULLS LAST, g.date DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()

    if not rows:
        print("No games to analyze with LLM.")
        return

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} games"),
        TimeElapsedColumn(),
    )

    with progress:
        task_id = progress.add_task("LLM analysis", total=len(rows))
        for row in rows:
            game_id = row['id']
            user_color = row['user_color']
            opening = row['opening'] or 'Unknown Opening'
            eco = row['eco'] or ''
            user_result = row['user_result']
            time_control = row['time_control'] or '?'

            white = row['white']
            black = row['black']
            white_elo = row['white_elo'] or '?'
            black_elo = row['black_elo'] or '?'

            if user_color == 'white':
                username = white
                user_elo = white_elo
                opp_elo = black_elo
            else:
                username = black
                user_elo = black_elo
                opp_elo = white_elo

            # Fetch user's positions with eval deltas
            conn = get_conn()
            cur = conn.cursor()
            positions = cur.execute("""
                SELECT ply, move_number, side, fen, move_san, move_uci,
                       eval_cp, user_eval_delta_cp, best_move_uci, best_eval_cp, phase
                FROM positions
                WHERE game_id = ?
                  AND side = ?
                  AND user_eval_delta_cp IS NOT NULL
                ORDER BY ABS(user_eval_delta_cp) DESC
                LIMIT 5
            """, (game_id, user_color)).fetchall()
            conn.close()

            if not positions:
                # Insert minimal game_analysis entry
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "INSERT OR IGNORE INTO game_analysis (game_id, llm_summary) VALUES (?, ?)",
                    (game_id, "No significant mistakes found.")
                )
                conn.commit()
                conn.close()
                progress.update(task_id, advance=1, description=f"LLM analysis [{game_id}]")
                continue

            # Build moments text
            moments_lines = []
            for pos in positions:
                move_num = pos['move_number']
                fen = pos['fen']
                move_san = pos['move_san']
                delta = pos['user_eval_delta_cp']
                best_uci = pos['best_move_uci']
                best_san = _uci_to_san(fen, best_uci) if best_uci else '?'
                phase = pos['phase']

                moments_lines.append(
                    f"Move {move_num} ({phase}): Played {move_san}, "
                    f"Engine recommends {best_san}, Cost: {delta} centipawns"
                )
                moments_lines.append(f"  FEN: {fen}")

            moments_text = "\n".join(moments_lines)

            prompt = f"""You are analyzing a chess game to create educational study material.

Game: {username} playing {user_color} ({user_elo}) vs opponent ({opp_elo})
Opening: {opening} ({eco}) | Result: {user_result} | Time control: {time_control}

Key moments (moves with largest evaluation drops for {username}):
{moments_text}

Each moment shows: move number, position FEN, what was played, what the engine recommends, centipawn cost.

Return JSON (no other text):
{{
  "summary": "<1-2 sentence game summary>",
  "turning_point_move": <int or null>,
  "turning_point_category": "<tactics|piece_coordination|king_safety|pawn_structure|endgame_technique|opening_error|time_pressure>",
  "phase_most_ground_lost": "<opening|middlegame|endgame>",
  "causal_root_move": <int or null>,
  "opening_deviation_move": <int or null>,
  "opening_principle_violated": "<str or null>",
  "key_moments": [
    {{
      "move_number": <int>,
      "user_move_san": "<str>",
      "better_move_san": "<str>",
      "concept": "<str>",
      "explanation": "<1-3 sentences: why the better move is better, in plain language>",
      "causal_connection": "<str or null: if this connects to an earlier mistake>"
    }}
  ]
}}

Include the 2-4 most instructive moments only. Focus on the why, not just listing mistakes."""

            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=1024,
                    system=[
                        {
                            "type": "text",
                            "text": SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )

                raw_text = response.content[0].text.strip()
                # Strip markdown code fences if present
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1]
                    raw_text = raw_text.rsplit("```", 1)[0].strip()

                # Parse JSON response
                try:
                    data = json.loads(raw_text)
                    llm_summary = data.get("summary", "")
                    turning_point_move = data.get("turning_point_move")
                    turning_point_category = data.get("turning_point_category")
                    phase_most_ground_lost = data.get("phase_most_ground_lost")
                    causal_root_move = data.get("causal_root_move")
                    opening_deviation_move = data.get("opening_deviation_move")
                    opening_principle_violated = data.get("opening_principle_violated")
                    key_moments = json.dumps(data.get("key_moments", []))
                except json.JSONDecodeError:
                    # Graceful fallback: store raw text in llm_summary
                    llm_summary = raw_text
                    turning_point_move = None
                    turning_point_category = None
                    phase_most_ground_lost = None
                    causal_root_move = None
                    opening_deviation_move = None
                    opening_principle_violated = None
                    key_moments = None

            except Exception as e:
                progress.console.print(f"[red]{game_id} LLM error:[/red] {e}")
                llm_summary = f"Error during analysis: {e}"
                turning_point_move = None
                turning_point_category = None
                phase_most_ground_lost = None
                causal_root_move = None
                opening_deviation_move = None
                opening_principle_violated = None
                key_moments = None

            # Store result
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                INSERT OR IGNORE INTO game_analysis
                (game_id, opening_deviation_move, opening_principle_violated,
                 phase_most_ground_lost, turning_point_move, turning_point_category,
                 causal_root_move, llm_summary, key_moments)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                game_id, opening_deviation_move, opening_principle_violated,
                phase_most_ground_lost, turning_point_move, turning_point_category,
                causal_root_move, llm_summary, key_moments,
            ))
            conn.commit()
            conn.close()

            progress.update(task_id, advance=1, description=f"LLM analysis [{game_id}]")
