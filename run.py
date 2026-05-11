#!/usr/bin/env python3
"""Chess tutor pipeline entry point."""

import argparse
import shutil
import sys


def _print_pipeline_status(label: str, stats: dict):
    print(
        f"{label}: "
        f"{stats['games']} games imported, "
        f"{stats['stockfish_games']} stockfish-analyzed, "
        f"{stats['llm_games']} llm-summarized, "
        f"{stats['challenge_games']} games with challenges "
        f"({stats['challenge_count']} total challenges)"
    )


def _resolve_stockfish(stockfish_arg: str) -> str:
    """Resolve a Stockfish executable path and fail with a clear message if missing."""
    resolved = shutil.which(stockfish_arg)
    if resolved:
        return resolved

    print(
        "Error: Stockfish executable not found.\n"
        f"Tried: {stockfish_arg}\n"
        "Install it with `brew install stockfish`, or pass an explicit path via "
        "`--stockfish /path/to/stockfish`.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="AI Chess Tutor Pipeline")
    parser.add_argument("--pgn", required=True, help="Path to Lichess PGN export")
    parser.add_argument("--username", help="Lichess username; if omitted, infer from the PGN when possible")
    parser.add_argument("--games", type=int, default=100, help="Max games to analyze (default: 100)")
    parser.add_argument("--stockfish", default="stockfish", help="Stockfish binary path (default: stockfish)")
    args = parser.parse_args()
    stockfish_path = _resolve_stockfish(args.stockfish)

    from src.db import get_pipeline_status, init_db
    from src.ingest import ingest_pgn
    from src.engine import analyze_games
    from src.scorer import score_games
    from src.llm import analyze_games_llm
    from src.study_plan import generate_challenges
    from src.render import render_html

    # 1. Init DB
    print("Initializing database...")
    init_db()
    _print_pipeline_status("Current DB status", get_pipeline_status())

    # 2. Ingest PGN
    if args.username:
        print(f"Ingesting {args.pgn} for user {args.username}...")
    else:
        print(f"Ingesting {args.pgn} and inferring user from PGN headers...")
    n, resolved_username, ingest_stats = ingest_pgn(args.pgn, args.username)
    print(f"Using username: {resolved_username}")
    print(
        f"Ingested {n} new games "
        f"({ingest_stats['skipped_existing']} already imported, "
        f"{ingest_stats['total_games']} readable total)"
    )
    _print_pipeline_status("After ingest", get_pipeline_status())

    # 3. Stockfish analysis
    print(f"Running Stockfish analysis with {stockfish_path} (up to {args.games} games)...")
    analyze_games(stockfish_path=stockfish_path, limit=args.games)
    _print_pipeline_status("After Stockfish", get_pipeline_status())

    # 4. Score by instructiveness (Stockfish data only, fast)
    print("Scoring games by instructiveness...")
    score_games()

    # 5. LLM analysis (ordered by instructiveness score)
    print(f"Running LLM analysis (up to {args.games} games)...")
    analyze_games_llm(limit=args.games)
    _print_pipeline_status("After LLM", get_pipeline_status())

    # 6. Generate challenges
    print("Generating challenges...")
    generate_challenges()
    _print_pipeline_status("After challenge generation", get_pipeline_status())

    # 7. Render HTML
    print("Rendering study HTML...")
    render_html()

    print("Study file ready: output/study.html")


if __name__ == "__main__":
    main()
