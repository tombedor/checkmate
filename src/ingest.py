import io
import re
from contextlib import nullcontext

import chess.pgn
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from src.db import get_conn


def _parse_clock(comment: str) -> float | None:
    """Extract clock seconds from a PGN comment containing [%clk H:MM:SS]."""
    m = re.search(r'\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]', comment)
    if not m:
        return None
    h, mins, secs = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mins * 60 + secs


def _derive_user_result(result: str, user_color: str) -> str:
    if result == '1/2-1/2':
        return 'draw'
    if (result == '1-0' and user_color == 'white') or (result == '0-1' and user_color == 'black'):
        return 'win'
    return 'loss'


def _iter_games(content: str):
    """Yield parsed PGN games from a string buffer."""
    pgn_io = io.StringIO(content)
    while True:
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            break
        yield game


def _count_games(content: str) -> int:
    """Count readable PGN games in a file."""
    return sum(1 for _ in _iter_games(content))


def infer_username_from_pgn(pgn_path: str) -> str:
    """Infer the user's account when exactly one player appears in every game."""
    candidates: set[str] | None = None

    with open(pgn_path, 'r', encoding='utf-8') as f:
        content = f.read()

    seen_games = 0
    for game in _iter_games(content):
        white = (game.headers.get('White', '') or '').strip()
        black = (game.headers.get('Black', '') or '').strip()
        players = {name for name in (white, black) if name}
        if not players:
            continue

        seen_games += 1
        if candidates is None:
            candidates = players
        else:
            candidates &= players

    if not seen_games:
        raise ValueError("Could not infer username: no readable games found in the PGN.")
    if not candidates:
        raise ValueError("Could not infer username: no single player appears in every game.")
    if len(candidates) > 1:
        names = ", ".join(sorted(candidates))
        raise ValueError(
            f"Could not infer username: multiple players appear in every game ({names}). "
            "Pass --username explicitly."
        )

    return next(iter(candidates))


def ingest_pgn(pgn_path: str, username: str | None = None) -> tuple[int, str, dict]:
    """Insert all games involving username. If omitted, infer it from the PGN. Returns count, resolved username, and summary stats."""
    if not username:
        username = infer_username_from_pgn(pgn_path)

    conn = get_conn()
    cur = conn.cursor()

    # Gather existing ids
    existing = {row[0] for row in cur.execute("SELECT id FROM games")}

    count = 0
    matched_games = 0
    skipped_existing = 0
    skipped_missing_id = 0
    skipped_other_player = 0
    with open(pgn_path, 'r', encoding='utf-8') as f:
        content = f.read()

    total_games = _count_games(content)
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total} games"),
        TimeElapsedColumn(),
    )
    progress_cm = progress if total_games else nullcontext()

    with progress_cm:
        task_id = progress.add_task("Ingesting PGN", total=total_games) if total_games else None
        for game in _iter_games(content):
            headers = game.headers

            # Determine game id
            game_id = headers.get('GameId', '')
            if not game_id:
                site = headers.get('Site', '')
                game_id = site.rstrip('/').split('/')[-1]
            if not game_id:
                skipped_missing_id += 1
                if task_id is not None:
                    progress.advance(task_id)
                continue

            if game_id in existing:
                skipped_existing += 1
                if task_id is not None:
                    progress.advance(task_id)
                continue

            white = headers.get('White', '')
            black = headers.get('Black', '')

            # Only include games where username is a player
            if username.lower() not in (white.lower(), black.lower()):
                skipped_other_player += 1
                if task_id is not None:
                    progress.advance(task_id)
                continue

            matched_games += 1
            user_color = 'white' if white.lower() == username.lower() else 'black'

            result = headers.get('Result', '*')
            user_result = _derive_user_result(result, user_color)

            try:
                white_elo = int(headers.get('WhiteElo', 0))
            except ValueError:
                white_elo = None
            try:
                black_elo = int(headers.get('BlackElo', 0))
            except ValueError:
                black_elo = None

            # Re-export PGN string for storage
            exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
            pgn_str = game.accept(exporter)

            cur.execute(
                """INSERT OR IGNORE INTO games
                   (id, date, white, black, user_color, white_elo, black_elo,
                    result, user_result, time_control, eco, opening, pgn)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    game_id,
                    headers.get('Date', ''),
                    white,
                    black,
                    user_color,
                    white_elo,
                    black_elo,
                    result,
                    user_result,
                    headers.get('TimeControl', ''),
                    headers.get('ECO', ''),
                    headers.get('Opening', ''),
                    pgn_str,
                )
            )
            existing.add(game_id)
            count += 1

            if task_id is not None:
                progress.advance(task_id)

    conn.commit()
    conn.close()
    return count, username, {
        "total_games": total_games,
        "matched_games": matched_games,
        "skipped_existing": skipped_existing,
        "skipped_missing_id": skipped_missing_id,
        "skipped_other_player": skipped_other_player,
    }
