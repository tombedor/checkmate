import io
import json
import re

import chess
import chess.engine
import chess.pgn
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from src.db import get_conn
from src.phase import detect_phase

MATE_SENTINEL = 2000


def _clamp(cp: int) -> int:
    return max(-MATE_SENTINEL, min(MATE_SENTINEL, cp))


def _score_to_cp(score: chess.engine.Score) -> int:
    """Convert engine Score to centipawns from White's perspective, clamped to ±2000."""
    if score.is_mate():
        mate = score.mate()
        return MATE_SENTINEL if mate > 0 else -MATE_SENTINEL
    return _clamp(score.score())


def _parse_clock(comment: str) -> float | None:
    m = re.search(r'\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]', comment)
    if not m:
        return None
    h, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mins * 60 + secs


def analyze_games(stockfish_path: str = 'stockfish', limit: int = 100):
    """Analyze up to `limit` most recent unanalyzed games. Stores results in positions table."""
    conn = get_conn()
    cur = conn.cursor()

    # Find games already analyzed
    analyzed = {row[0] for row in cur.execute("SELECT DISTINCT game_id FROM positions")}

    # Fetch up to `limit` most recent unanalyzed games
    rows = cur.execute(
        "SELECT id, pgn, user_color FROM games ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()

    to_analyze = [r for r in rows if r['id'] not in analyzed][:limit]

    if not to_analyze:
        print("No games to analyze.")
        return

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} games"),
        TimeElapsedColumn(),
    )

    with progress, chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        task_id = progress.add_task("Stockfish analysis", total=len(to_analyze))
        for row in to_analyze:
            game_id = row['id']
            user_color = row['user_color']
            pgn_str = row['pgn']

            try:
                game = chess.pgn.read_game(io.StringIO(pgn_str))
            except Exception as e:
                progress.console.print(f"[red]{game_id} parse error:[/red] {e}")
                progress.advance(task_id)
                continue

            board = game.board()
            positions = []
            node = game

            while node.variations:
                next_node = node.variations[0]
                move = next_node.move

                fen_before = board.fen()
                phase = detect_phase(board)
                move_number = board.fullmove_number
                side = 'white' if board.turn == chess.WHITE else 'black'
                clock = _parse_clock(next_node.comment)

                # Analyze position BEFORE the move
                try:
                    info_list = engine.analyse(
                        board,
                        chess.engine.Limit(time=0.1),
                        multipv=3
                    )
                except Exception as e:
                    progress.console.print(
                        f"[yellow]{game_id} engine error at ply {len(positions)}:[/yellow] {e}"
                    )
                    board.push(move)
                    node = next_node
                    continue

                # Extract eval (White's perspective)
                best_info = info_list[0]
                eval_cp = _score_to_cp(best_info['score'].white())

                best_move_uci = None
                best_eval_cp = None
                if 'pv' in best_info and best_info['pv']:
                    best_move_uci = best_info['pv'][0].uci()
                    best_eval_cp = eval_cp

                # Build top_lines
                top_lines = []
                for info in info_list:
                    if 'pv' not in info or not info['pv']:
                        continue
                    pv_sans = []
                    tmp_board = board.copy()
                    for pv_move in info['pv'][:5]:
                        try:
                            pv_sans.append(tmp_board.san(pv_move))
                            tmp_board.push(pv_move)
                        except Exception:
                            break
                    line_cp = _score_to_cp(info['score'].white())
                    top_lines.append({'pv': [m.uci() for m in info['pv'][:5]], 'cp': line_cp})

                move_san = board.san(move)
                move_uci = move.uci()

                positions.append({
                    'game_id': game_id,
                    'ply': len(positions),
                    'move_number': move_number,
                    'side': side,
                    'fen': fen_before,
                    'move_san': move_san,
                    'move_uci': move_uci,
                    'eval_cp': eval_cp,
                    'user_eval_delta_cp': None,  # computed below
                    'best_move_uci': best_move_uci,
                    'best_eval_cp': best_eval_cp,
                    'top_lines': json.dumps(top_lines),
                    'clock_seconds': clock,
                    'phase': phase,
                })

                board.push(move)
                node = next_node

            # Compute user_eval_delta_cp
            # We need the eval AFTER each move, which is the eval_cp of the next position
            for i, pos in enumerate(positions):
                if pos['side'] != user_color:
                    pos['user_eval_delta_cp'] = None
                    continue

                if i + 1 < len(positions):
                    next_eval = positions[i + 1]['eval_cp']
                else:
                    # Last position: no next eval available
                    pos['user_eval_delta_cp'] = None
                    continue

                curr_eval = pos['eval_cp']
                if user_color == 'white':
                    delta = next_eval - curr_eval
                else:
                    delta = -(next_eval - curr_eval)
                pos['user_eval_delta_cp'] = delta

            # Store in DB
            conn = get_conn()
            cur2 = conn.cursor()
            for pos in positions:
                cur2.execute(
                    """INSERT INTO positions
                       (game_id, ply, move_number, side, fen, move_san, move_uci,
                        eval_cp, user_eval_delta_cp, best_move_uci, best_eval_cp,
                        top_lines, clock_seconds, phase)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        pos['game_id'], pos['ply'], pos['move_number'], pos['side'],
                        pos['fen'], pos['move_san'], pos['move_uci'],
                        pos['eval_cp'], pos['user_eval_delta_cp'],
                        pos['best_move_uci'], pos['best_eval_cp'],
                        pos['top_lines'], pos['clock_seconds'], pos['phase'],
                    )
                )
            conn.commit()
            conn.close()
            progress.update(task_id, advance=1, description=f"Stockfish analysis [{game_id}]")
