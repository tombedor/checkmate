#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_FIELDS = [
    "id",
    "game_id",
    "game_url",
    "move_number",
    "user_color",
    "user_move_san",
    "correct_move_san",
    "correct_move_uci",
    "correct_move_display",
    "correct_move_from",
    "correct_move_to",
    "correct_move_piece",
    "correct_move_legal",
    "concept",
    "opening",
    "eco",
    "context",
    "explanation",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect one generated puzzle from output/study-data.json")
    parser.add_argument("puzzle_id", type=int, help="Challenge/puzzle id")
    parser.add_argument(
        "--data",
        default="output/study-data.json",
        help="Path to rendered study data JSON (default: output/study-data.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full challenge JSON object instead of a curated summary",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Missing study data file: {data_path}", file=sys.stderr)
        return 1

    payload = json.loads(data_path.read_text(encoding="utf-8"))
    for challenge in payload.get("challenges", []):
        if challenge.get("id") == args.puzzle_id:
            if args.json:
                print(json.dumps(challenge, indent=2, ensure_ascii=False))
            else:
                for field in DEFAULT_FIELDS:
                    print(f"{field}: {challenge.get(field)}")
            return 0

    print(f"Puzzle {args.puzzle_id} not found in {data_path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
