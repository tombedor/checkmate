from src.db import get_conn


def _score_game(positions: list, user_result: str) -> float:
    """
    Score a game's instructiveness from Stockfish data alone (0.0–1.0).

    High score = clear, specific mistake from an equal/winning position,
    with a concentrated failure mode. Useful for prioritising LLM analysis.
    """
    user_moves = [p for p in positions if p["user_eval_delta_cp"] is not None]
    if not user_moves:
        return 0.0

    mistakes = [p for p in user_moves if p["user_eval_delta_cp"] < -30]
    if not mistakes:
        return 0.05

    # 1. Largest single mistake (cap at 500 cp)
    max_cp = max(abs(p["user_eval_delta_cp"]) for p in mistakes)
    max_mistake_score = min(max_cp / 500.0, 1.0)

    # 2. Context quality: did the mistake come from a decent position?
    # eval_cp is White's perspective; convert to user's perspective for threshold
    context_score = 0.0
    for p in mistakes:
        eval_from_user = p["eval_cp"] if p["side"] == "white" else -p["eval_cp"]
        if eval_from_user > -150:  # user was roughly equal or better
            context_score = max(context_score, min(abs(p["user_eval_delta_cp"]) / 500.0, 1.0))

    # 3. Opening mistakes (explicitly higher weight — they compound)
    opening_loss = sum(abs(p["user_eval_delta_cp"]) for p in mistakes if p["phase"] == "opening")
    opening_score = min(opening_loss / 300.0, 1.0)

    # 4. Phase concentration — mistakes clustered in one phase are cleaner to learn from
    phase_losses: dict[str, float] = {}
    for p in mistakes:
        ph = p["phase"] or "middlegame"
        phase_losses[ph] = phase_losses.get(ph, 0) + abs(p["user_eval_delta_cp"])
    total_loss = sum(phase_losses.values())
    concentration = max(phase_losses.values()) / total_loss if total_loss > 0 else 0.0

    # 5. Result: losses slightly prioritised (more to learn), wins deprioritised
    result_weight = {"loss": 1.0, "draw": 0.6, "win": 0.3}.get(user_result, 0.5)

    score = (
        0.35 * max_mistake_score
        + 0.25 * context_score
        + 0.15 * opening_score
        + 0.15 * result_weight
        + 0.10 * concentration
    )
    return round(score, 4)


def score_games():
    """
    Score all Stockfish-analysed games by instructiveness.
    Adds instructiveness_score column to games table if missing, then updates all scored games.
    """
    conn = get_conn()

    # Add column if it doesn't exist yet
    try:
        conn.execute("ALTER TABLE games ADD COLUMN instructiveness_score REAL")
        conn.commit()
    except Exception:
        pass  # column already exists

    # Fetch all games that have positions
    game_rows = conn.execute("""
        SELECT DISTINCT g.id, g.user_color, g.user_result
        FROM games g
        WHERE EXISTS (SELECT 1 FROM positions p WHERE p.game_id = g.id)
          AND (g.instructiveness_score IS NULL)
    """).fetchall()
    conn.close()

    if not game_rows:
        print("All games already scored.")
        return

    print(f"Scoring {len(game_rows)} games...")
    updates = []

    for row in game_rows:
        game_id = row["id"]
        user_color = row["user_color"]
        user_result = row["user_result"]

        conn = get_conn()
        positions = conn.execute("""
            SELECT user_eval_delta_cp, eval_cp, phase, side
            FROM positions
            WHERE game_id = ?
        """, (game_id,)).fetchall()
        conn.close()

        pos_list = [dict(p) for p in positions]
        score = _score_game(pos_list, user_result)
        updates.append((score, game_id))

    conn = get_conn()
    conn.executemany("UPDATE games SET instructiveness_score = ? WHERE id = ?", updates)
    conn.commit()

    # Print distribution summary
    scores = [u[0] for u in updates]
    if scores:
        avg = sum(scores) / len(scores)
        top10 = sorted(scores, reverse=True)[:10]
        print(f"Scored {len(scores)} games. Avg={avg:.3f}, Top-10 min={top10[-1]:.3f}")
    conn.close()
