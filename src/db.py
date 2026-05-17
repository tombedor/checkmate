import os
import sqlite3

DB_PATH = "output/chess_tutor.db"


def get_conn() -> sqlite3.Connection:
    os.makedirs("output", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs("output", exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS games (
            id TEXT PRIMARY KEY,
            date TEXT,
            white TEXT,
            black TEXT,
            user_color TEXT,
            white_elo INTEGER,
            black_elo INTEGER,
            result TEXT,
            user_result TEXT,
            time_control TEXT,
            eco TEXT,
            opening TEXT,
            pgn TEXT
        );

        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            ply INTEGER,
            move_number INTEGER,
            side TEXT,
            fen TEXT,
            move_san TEXT,
            move_uci TEXT,
            eval_cp INTEGER,
            user_eval_delta_cp INTEGER,
            best_move_uci TEXT,
            best_eval_cp INTEGER,
            top_lines TEXT,
            clock_seconds REAL,
            phase TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        );

        CREATE TABLE IF NOT EXISTS game_analysis (
            game_id TEXT PRIMARY KEY,
            opening_deviation_move INTEGER,
            opening_principle_violated TEXT,
            phase_most_ground_lost TEXT,
            turning_point_move INTEGER,
            turning_point_category TEXT,
            causal_root_move INTEGER,
            llm_summary TEXT,
            key_moments TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        );

        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT,
            move_number INTEGER,
            fen TEXT,
            context TEXT,
            concept TEXT,
            concept_detail TEXT,
            user_move_san TEXT,
            correct_move_san TEXT,
            correct_move_uci TEXT,
            explanation TEXT,
            next_step TEXT,
            phase TEXT,
            eval_delta_cp INTEGER,
            priority REAL DEFAULT 1.0,
            times_seen INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            next_review TEXT,
            root_cause_move INTEGER,
            FOREIGN KEY (game_id) REFERENCES games(id)
        );
    """)
    # Add columns for existing databases (safe to run multiple times)
    try:
        cur.execute("ALTER TABLE challenges ADD COLUMN concept_detail TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE challenges ADD COLUMN next_step TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE challenges ADD COLUMN root_cause_move INTEGER")
    except Exception:
        pass
    conn.commit()
    conn.close()


def get_pipeline_status() -> dict:
    """Return aggregate counts for each pipeline stage."""
    conn = get_conn()
    cur = conn.cursor()

    total_games = cur.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    stockfish_games = cur.execute("SELECT COUNT(DISTINCT game_id) FROM positions").fetchone()[0]
    llm_games = cur.execute("SELECT COUNT(*) FROM game_analysis").fetchone()[0]
    challenge_games = cur.execute("SELECT COUNT(DISTINCT game_id) FROM challenges").fetchone()[0]
    challenge_count = cur.execute("SELECT COUNT(*) FROM challenges").fetchone()[0]

    conn.close()
    return {
        "games": total_games,
        "stockfish_games": stockfish_games,
        "llm_games": llm_games,
        "challenge_games": challenge_games,
        "challenge_count": challenge_count,
    }
