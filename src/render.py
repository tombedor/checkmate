import json
import shutil
from pathlib import Path

from src.study_plan import describe_uci_move, get_challenge_queue, get_lichess_focus_recommendations


WEB_DIR = Path(__file__).parent / "web"
PGN_VIEWER_BUNDLE = Path(__file__).resolve().parents[1] / "node_modules" / "@mliebelt" / "pgn-viewer" / "lib" / "dist.js"
LICHESS_THEME_SLUGS = {
    "Healthy mix": "mix",
    "Opening": "opening",
    "Middlegame": "middlegame",
    "Endgame": "endgame",
    "Rook endgame": "rookEndgame",
    "Bishop endgame": "bishopEndgame",
    "Pawn endgame": "pawnEndgame",
    "Knight endgame": "knightEndgame",
    "Queen endgame": "queenEndgame",
    "Queen and Rook": "queenRookEndgame",
    "Advanced pawn": "advancedPawn",
    "Attacking f2 or f7": "attackingF2F7",
    "Capture the defender": "capturingDefender",
    "Discovered attack": "discoveredAttack",
    "Double check": "doubleCheck",
    "Exposed king": "exposedKing",
    "Fork": "fork",
    "Hanging piece": "hangingPiece",
    "Kingside attack": "kingsideAttack",
    "Pin": "pin",
    "Queenside attack": "queensideAttack",
    "Sacrifice": "sacrifice",
    "Skewer": "skewer",
    "Trapped piece": "trappedPiece",
    "Attraction": "attraction",
    "Clearance": "clearance",
    "Discovered check": "discoveredCheck",
    "Defensive move": "defensiveMove",
    "Deflection": "deflection",
    "Interference": "interference",
    "Intermezzo": "intermezzo",
    "Quiet move": "quietMove",
    "X-Ray attack": "xRayAttack",
    "Zugzwang": "zugzwang",
    "Checkmate": "mate",
    "Mate in 1": "mateIn1",
    "Mate in 2": "mateIn2",
    "Mate in 3": "mateIn3",
    "Mate in 4": "mateIn4",
    "Mate in 5 or more": "mateIn5",
    "Anastasia's mate": "anastasiasMate",
    "Arabian mate": "arabianMate",
    "Back rank mate": "backRankMate",
    "Boden's mate": "bodensMate",
    "Double bishop mate": "doubleBishopMate",
    "Dovetail mate": "dovetailMate",
    "Epaulette mate": "epauletteMate",
    "Hook mate": "hookMate",
    "Kill box mate": "killBoxMate",
    "Morphy's mate": "morphysMate",
    "Opera mate": "operaMate",
    "Pillsbury's mate": "pillsburysMate",
    "Smothered mate": "smotheredMate",
    "Triangle mate": "triangleMate",
    "Vuković mate": "vukovicMate",
    "Castling": "castling",
    "En passant rights": "enPassant",
    "Promotion": "promotion",
    "Underpromotion": "underPromotion",
}


def _build_concept_counts(challenges: list[dict]) -> dict[str, int]:
    concept_counts: dict[str, int] = {}
    for challenge in challenges:
        concept = challenge.get("concept") or "general"
        concept_counts[concept] = concept_counts.get(concept, 0) + 1
    return concept_counts


def _lichess_move_anchor(move_number: int | None, user_color: str | None) -> int | None:
    if not move_number or move_number < 1:
        return None
    if user_color == "black":
        return move_number * 2
    return (move_number * 2) - 1


def _augment_challenges(challenges: list[dict]) -> list[dict]:
    augmented = []
    for challenge in challenges:
        row = dict(challenge)
        game_id = row.get("game_id", "")
        base_game_url = f"https://lichess.org/{game_id}" if game_id else "https://lichess.org/"
        row["game_base_url"] = base_game_url
        row["game_move_anchor"] = _lichess_move_anchor(row.get("move_number"), row.get("user_color"))
        row["game_url"] = (
            f"{base_game_url}#{row['game_move_anchor']}"
            if game_id and row["game_move_anchor"] is not None
            else base_game_url
        )
        best_move = describe_uci_move(row.get("fen", ""), row.get("correct_move_uci", ""))
        row["correct_move_san"] = best_move["san"] if best_move["is_legal"] else row.get("correct_move_san", "")
        row["correct_move_from"] = best_move["from_square"]
        row["correct_move_to"] = best_move["to_square"]
        row["correct_move_piece"] = best_move["piece"]
        row["correct_move_legal"] = best_move["is_legal"]
        row["correct_move_display"] = best_move["display"]
        augmented.append(row)
    return augmented


def _augment_focus_items(items: list[dict]) -> list[dict]:
    augmented = []
    for item in items:
        row = dict(item)
        slug = LICHESS_THEME_SLUGS.get(row.get("theme", ""))
        row["theme_url"] = f"https://lichess.org/training/{slug}" if slug else "https://lichess.org/training/themes"
        row["theme_linkable"] = bool(slug)
        augmented.append(row)
    return augmented


def render_html(output_path: str = "output/study.html"):
    """Generate the hosted study app files into the output directory."""
    output_dir = Path(output_path).resolve().parent
    output_dir.mkdir(parents=True, exist_ok=True)

    challenges = _augment_challenges(get_challenge_queue())
    payload = {
        "challenges": challenges,
        "concept_counts": _build_concept_counts(challenges),
        "lichess_focus": _augment_focus_items(get_lichess_focus_recommendations()),
    }

    (output_dir / "study-data.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    for name in ("index.html", "app.js", "styles.css"):
        shutil.copyfile(WEB_DIR / name, output_dir / name)

    vendor_dir = output_dir / "vendor"
    vendor_dir.mkdir(exist_ok=True)
    if not PGN_VIEWER_BUNDLE.exists():
        raise FileNotFoundError(
            "Missing PGN viewer bundle. Run `npm install` to install @mliebelt/pgn-viewer."
        )
    shutil.copyfile(PGN_VIEWER_BUNDLE, vendor_dir / "pgnv.js")

    # Backward compatibility for previous links/bookmarks.
    shutil.copyfile(output_dir / "index.html", output_dir / "study.html")

    print(f"Rendered {len(challenges)} challenges to {output_dir / 'index.html'}")
