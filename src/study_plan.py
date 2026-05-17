import json

import chess

from src.db import get_conn


LICHESS_THEME_RULES = [
    ("Advanced pawn", ("advanced pawn", "passed pawn", "deep pawn", "promote soon")),
    ("Attacking f2 or f7", ("f2", "f7", "fried liver")),
    ("Capture the defender", ("remove the defender", "removing the defender", "capture the defender")),
    ("Checkmate", ("checkmate", "mate", "mating net", "mate threat")),
    ("Mate in 1", ("mate in 1", "mate in one", "one-move mate")),
    ("Mate in 2", ("mate in 2", "mate in two")),
    ("Mate in 3", ("mate in 3", "mate in three")),
    ("Mate in 4", ("mate in 4", "mate in four")),
    ("Mate in 5 or more", ("mate in 5", "mate in five", "long mating sequence")),
    ("Back rank mate", ("back rank mate", "back-rank mate", "back rank")),
    ("Smothered mate", ("smothered mate",)),
    ("Anastasia's mate", ("anastasia", "anastasia's mate")),
    ("Arabian mate", ("arabian mate",)),
    ("Boden's mate", ("boden", "boden's mate")),
    ("Double bishop mate", ("double bishop mate",)),
    ("Dovetail mate", ("dovetail mate",)),
    ("Epaulette mate", ("epaulette mate",)),
    ("Hook mate", ("hook mate",)),
    ("Kill box mate", ("kill box mate",)),
    ("Morphy's mate", ("morphy", "morphy's mate")),
    ("Opera mate", ("opera mate",)),
    ("Pillsbury's mate", ("pillsbury", "pillsbury's mate")),
    ("Smothered mate", ("smothered mate",)),
    ("Triangle mate", ("triangle mate",)),
    ("Vuković mate", ("vuković", "vukovic mate", "vuković mate")),
    ("Kingside attack", ("kingside attack", "exposed king", "king attack", "attack the king")),
    ("Queenside attack", ("queenside attack",)),
    ("Fork", ("fork", "double attack")),
    ("Pin", ("pin", "pinned")),
    ("Skewer", ("skewer",)),
    ("Discovered attack", ("discovered attack", "discovered check")),
    ("Discovered check", ("discovered check",)),
    ("Double check", ("double check",)),
    ("Hanging piece", ("hanging", "undefended", "loose piece", "free to capture")),
    ("Trapped piece", ("trapped piece", "unable to escape", "no escape squares")),
    ("Deflection", ("deflection", "distract", "distracting")),
    ("Attraction", ("attraction", "lure", "drag the king", "dragging")),
    ("Interference", ("interference", "interpose", "blocking line")),
    ("Clearance", ("clearance", "clear a square", "clear the file", "clear the diagonal")),
    ("Sacrifice", ("sacrifice", "give up material")),
    ("Defensive move", ("defensive", "defense", "prophyl", "only move", "avoid losing")),
    ("Intermezzo", ("intermezzo", "zwischenzug", "in between move")),
    ("Quiet move", ("quiet move",)),
    ("X-Ray attack", ("x-ray", "x ray")),
    ("Zugzwang", ("zugzwang",)),
    ("Castling", ("castle", "castling")),
    ("En passant rights", ("en passant",)),
    ("Promotion", ("promotion", "promote", "passed pawn", "underpromotion")),
    ("Underpromotion", ("underpromotion", "promote to a knight", "promote to bishop", "promote to rook")),
]


def _uci_to_san(fen: str, uci: str) -> str:
    """Convert UCI move to SAN given a FEN position."""
    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(uci)
        return board.san(move)
    except Exception:
        return uci


def _piece_name(piece_type: int | None) -> str | None:
    if piece_type is None:
        return None
    return {
        chess.PAWN: "pawn",
        chess.KNIGHT: "knight",
        chess.BISHOP: "bishop",
        chess.ROOK: "rook",
        chess.QUEEN: "queen",
        chess.KING: "king",
    }.get(piece_type)


def describe_uci_move(fen: str, uci: str) -> dict:
    """Return verified move metadata for a UCI move in a FEN position."""
    details = {
        "uci": uci,
        "san": uci or "?",
        "from_square": None,
        "to_square": None,
        "piece": None,
        "is_legal": False,
        "display": uci or "?",
    }
    if not fen or not uci:
        return details

    try:
        board = chess.Board(fen)
        move = chess.Move.from_uci(uci)
    except Exception:
        return details

    details["from_square"] = chess.square_name(move.from_square)
    details["to_square"] = chess.square_name(move.to_square)
    piece = board.piece_at(move.from_square)
    details["piece"] = _piece_name(piece.piece_type if piece else None)

    if move not in board.legal_moves:
        return details

    san = board.san(move)
    details["san"] = san
    details["is_legal"] = True
    if details["piece"] and details["from_square"] and details["to_square"]:
        details["display"] = f"{san} - {details['piece']} {details['from_square']}→{details['to_square']}"
    else:
        details["display"] = san
    return details


def _phase_priority(phase: str) -> float:
    return {'opening': 3.0, 'middlegame': 2.0, 'endgame': 1.0}.get(phase or 'middlegame', 1.0)


def _theme_matches(text: str) -> list[str]:
    matches: list[str] = []
    haystack = (text or "").lower()
    for theme, keywords in LICHESS_THEME_RULES:
        if any(keyword in haystack for keyword in keywords):
            matches.append(theme)
    return matches


def get_lichess_focus_recommendations(limit: int = 5) -> list[dict]:
    """Rank Lichess puzzle themes based on extracted challenge concepts."""
    challenges = get_challenge_queue()
    theme_scores: dict[str, dict] = {}

    for challenge in challenges:
        concept = challenge.get('concept') or ''
        explanation = challenge.get('explanation') or ''
        context = challenge.get('context') or ''
        phase = challenge.get('phase') or 'middlegame'
        weight = float(challenge.get('priority') or 1.0)

        text = " ".join((concept, explanation, context))
        themes = _theme_matches(text)

        if phase == 'opening':
            themes.append("Opening")
        elif phase == 'endgame':
            themes.append("Endgame")
        else:
            themes.append("Middlegame")

        if "forcing" in text.lower() or "check" in text.lower():
            themes.append("Checkmate")

        if not themes:
            themes.append("Healthy mix")

        for theme in dict.fromkeys(themes):
            if theme not in theme_scores:
                theme_scores[theme] = {
                    "theme": theme,
                    "score": 0.0,
                    "count": 0,
                    "examples": [],
                }
            entry = theme_scores[theme]
            entry["score"] += weight
            entry["count"] += 1
            if concept and concept not in entry["examples"] and len(entry["examples"]) < 2:
                entry["examples"].append(concept)

    ranked = sorted(
        theme_scores.values(),
        key=lambda item: (item["score"], item["count"]),
        reverse=True,
    )

    recommendations = []
    for entry in ranked[:limit]:
        examples = "; ".join(entry["examples"]) if entry["examples"] else "Repeated mistakes in this theme"
        recommendations.append({
            "theme": entry["theme"],
            "count": entry["count"],
            "score": round(entry["score"], 2),
            "reason": examples,
        })

    return recommendations


def generate_challenges():
    """Generate challenge records from game_analysis key_moments. Skip already-generated challenges."""
    conn = get_conn()
    cur = conn.cursor()

    # Games already in challenges
    existing_game_ids = {row[0] for row in cur.execute("SELECT DISTINCT game_id FROM challenges")}

    # Fetch game_analysis rows with key_moments
    rows = cur.execute("""
        SELECT ga.game_id, ga.key_moments,
               g.user_color, g.opening, g.eco
        FROM game_analysis ga
        JOIN games g ON g.id = ga.game_id
        WHERE ga.key_moments IS NOT NULL
    """).fetchall()

    conn.close()

    count = 0
    for row in rows:
        game_id = row['game_id']
        if game_id in existing_game_ids:
            continue

        user_color = row['user_color']
        opening = row['opening'] or 'Unknown Opening'
        eco = row['eco'] or ''

        try:
            key_moments = json.loads(row['key_moments'])
        except (json.JSONDecodeError, TypeError):
            continue

        if not key_moments:
            continue

        for moment in key_moments:
            move_number = moment.get('move_number')
            if move_number is None:
                continue

            user_move_san = moment.get('user_move_san', '')
            better_move_san = moment.get('better_move_san', '')
            concept = moment.get('concept', 'general')
            explanation = moment.get('explanation', '')
            causal_connection = moment.get('causal_connection', '')

            # Find matching position row
            conn = get_conn()
            cur2 = conn.cursor()
            pos_row = cur2.execute("""
                SELECT fen, move_san, best_move_uci, user_eval_delta_cp, phase
                FROM positions
                WHERE game_id = ? AND move_number = ? AND side = ?
                LIMIT 1
            """, (game_id, move_number, user_color)).fetchone()
            conn.close()

            if not pos_row:
                continue

            fen = pos_row['fen']
            phase = pos_row['phase'] or 'middlegame'
            eval_delta = pos_row['user_eval_delta_cp'] or 0
            best_move_uci = pos_row['best_move_uci'] or ''

            # Convert best_move_uci to SAN
            correct_move_san = better_move_san
            if best_move_uci:
                san_from_uci = _uci_to_san(fen, best_move_uci)
                if san_from_uci != best_move_uci:
                    correct_move_san = san_from_uci

            # Build context string
            context = (
                f"Move {move_number}, you're playing {user_color} in a {opening}"
                f"{' (' + eco + ')' if eco else ''}. "
                f"You played {user_move_san}."
            )
            if causal_connection:
                context += f" Note: {causal_connection}"

            # Priority: phase multiplier × magnitude
            priority = _phase_priority(phase) * (abs(eval_delta) / 100.0)

            conn = get_conn()
            cur3 = conn.cursor()
            cur3.execute("""
                INSERT INTO challenges
                (game_id, move_number, fen, context, concept, user_move_san,
                 correct_move_san, correct_move_uci, explanation, phase,
                 eval_delta_cp, priority)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                game_id, move_number, fen, context, concept, user_move_san,
                correct_move_san, best_move_uci, explanation, phase,
                abs(eval_delta), priority,
            ))
            conn.commit()
            conn.close()
            count += 1

        existing_game_ids.add(game_id)

    print(f"Generated {count} challenges.")


def get_challenge_queue() -> list[dict]:
    """Return challenges ordered by priority desc, then next_review, as list of dicts."""
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT challenges.id, challenges.game_id, challenges.move_number, challenges.fen,
               challenges.context, challenges.concept, challenges.user_move_san,
               challenges.correct_move_san, challenges.correct_move_uci,
               challenges.explanation, challenges.phase, challenges.eval_delta_cp,
               challenges.priority, challenges.times_seen, challenges.times_correct,
               challenges.next_review, g.user_color, g.opening, g.eco, g.pgn,
               g.white, g.black
        FROM challenges
        JOIN games g ON g.id = challenges.game_id
        ORDER BY priority DESC, next_review ASC NULLS FIRST
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
