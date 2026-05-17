from __future__ import annotations

import contextlib
import json
import re
import shutil
import sqlite3
import socket
import threading
from functools import partial
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

from serve import StudyHandler


def _free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture()
def sample_output_dir(tmp_path: Path) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    web_dir = repo_root / "src" / "web"
    vendor_dir = repo_root / "node_modules" / "@mliebelt" / "pgn-viewer" / "lib"

    for name in ("index.html", "app.js", "styles.css"):
        shutil.copyfile(web_dir / name, tmp_path / name)
    (tmp_path / "vendor").mkdir()
    shutil.copyfile(vendor_dir / "dist.js", tmp_path / "vendor" / "pgnv.js")

    sample_data = {
        "challenges": [
            {
                "id": 1,
                "game_id": "whitegame1",
                "game_url": "https://lichess.org/whitegame1#77",
                "move_number": 39,
                "fen": "1Q6/3kb3/p2p1p2/1b1PpPp1/3qP1P1/8/1P2N2P/6K1 w - - 5 39",
                "context": "Move 39, you're playing white in an Indian Defense (A45). You played Kf1.",
                "concept": "Tactical blindness - missing a forcing capture",
                "user_move_san": "Kf1",
                "correct_move_san": "Nxd4",
                "correct_move_uci": "e2d4",
                "correct_move_from": "e2",
                "correct_move_to": "d4",
                "correct_move_piece": "knight",
                "correct_move_legal": True,
                "correct_move_display": "Nxd4 - knight e2→d4",
                "explanation": "Nxd4 removes the enemy queen and wins material immediately.",
                "phase": "middlegame",
                "eval_delta_cp": 2547,
                "priority": 50.94,
                "times_seen": 0,
                "times_correct": 0,
                "next_review": None,
                "user_color": "white",
                "opening": "Indian Defense",
                "eco": "A45",
                "white": "tbonez",
                "black": "opponent",
                "pgn": '[Event "Study"]\n[Site "https://lichess.org/whitegame1"]\n[Date "2026.05.01"]\n[White "tbonez"]\n[Black "opponent"]\n[Result "1-0"]\n\n1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. d4 exd4 1-0',
            },
            {
                "id": 2,
                "game_id": "blackgame2",
                "game_url": "https://lichess.org/blackgame2#26",
                "move_number": 13,
                "fen": "r1bq1r1k/ppp2pbn/2np4/3Np2Q/2B1P3/P2P1N1P/1PP2PP1/R3K2R b KQ - 4 13",
                "context": "Move 13, you're playing black in a Philidor Defense (C41). You played Ne7.",
                "concept": "Tactical activation: counterattacking with tempo",
                "user_move_san": "Ne7",
                "correct_move_san": "Nd4",
                "correct_move_uci": "c6d4",
                "correct_move_from": "c6",
                "correct_move_to": "d4",
                "correct_move_piece": "knight",
                "correct_move_legal": True,
                "correct_move_display": "Nd4 - knight c6→d4",
                "explanation": "Nd4 attacks with tempo and creates counterplay.",
                "phase": "middlegame",
                "eval_delta_cp": 2187,
                "priority": 43.74,
                "times_seen": 0,
                "times_correct": 0,
                "next_review": None,
                "user_color": "black",
                "opening": "Philidor Defense",
                "eco": "C41",
                "white": "opponent",
                "black": "tbonez",
                "pgn": '[Event "Study"]\n[Site "https://lichess.org/blackgame2"]\n[Date "2026.05.02"]\n[White "opponent"]\n[Black "tbonez"]\n[Result "0-1"]\n\n1. e4 e5 2. Nf3 d6 3. d4 exd4 0-1',
            },
        ],
        "concept_counts": {
            "Tactical blindness - missing a forcing capture": 1,
            "Tactical activation: counterattacking with tempo": 1,
        },
        "lichess_focus": [
            {
                "theme": "Checkmate",
                "count": 2,
                "score": 90.0,
                "reason": "Checks and forcing moves show up repeatedly",
                "theme_url": "https://lichess.org/training/mate",
                "theme_linkable": True,
            }
        ],
    }

    (tmp_path / "study-data.json").write_text(json.dumps(sample_data), encoding="utf-8")
    shutil.copyfile(tmp_path / "index.html", tmp_path / "study.html")

    db_path = tmp_path / "chess_tutor.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE challenges (
            id INTEGER PRIMARY KEY,
            times_seen INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            next_review TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO challenges (id, times_seen, times_correct, next_review) VALUES (?, 0, 0, NULL)",
        [(1,), (2,)],
    )
    conn.commit()
    conn.close()
    return tmp_path


@pytest.fixture()
def live_server(sample_output_dir: Path):
    port = _free_port()
    handler = partial(
        StudyHandler,
        directory=str(sample_output_dir),
        db_path=str(sample_output_dir / "chess_tutor.db"),
    )
    httpd = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        httpd.shutdown()
        httpd.server_close()


@pytest.fixture()
def page(live_server: str):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1400})
        page.goto(live_server, wait_until="networkidle")
        yield page
        browser.close()


def _center(locator):
    box = locator.bounding_box()
    assert box is not None
    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def test_study_ui_drag_submit_and_game_link(page):
    expect(page.locator("h1")).to_have_text("Study Board")
    expect(page.locator("#board .square")).to_have_count(64)
    expect(page.locator("#game-link")).to_have_attribute("href", "https://lichess.org/whitegame1#77")
    expect(page.locator("#challenge-link")).to_have_attribute("href", "#puzzle-1")
    expect(page.locator("#challenge-link")).to_have_text("Puzzle #1")
    expect(page.locator("#actual-move")).to_have_text("Kf1")
    expect(page.locator("#actual-move-banner")).to_have_text("Kf1")
    expect(page.locator("#player-clarifier")).to_have_text("You were white (tbonez) vs opponent.")
    expect(page.locator("#opening-pill")).to_have_text("Indian Defense (A45)")
    expect(page.locator("#best-move-clarifier")).to_contain_text("Nxd4 - knight e2→d4")
    expect(page.locator(".focus-card-link").first).to_have_attribute("href", "https://lichess.org/training/mate")
    expect(page.locator("#replay-viewer .pgnvjs")).to_be_visible()
    expect(page.locator("#replay-viewer")).to_contain_text("1.")

    source = page.locator('[data-square="e2"]')
    target = page.locator('[data-square="d4"]')
    sx, sy = _center(source)
    tx, ty = _center(target)

    page.mouse.move(sx, sy)
    page.mouse.down()
    page.mouse.move(tx, ty, steps=12)
    page.mouse.up()

    expect(page.locator("#instruction-text")).to_contain_text("Click Submit to confirm")

    page.locator("#btn-submit").click()
    expect(page.locator("#feedback-box")).to_be_visible()
    expect(page.locator("#btn-next")).to_be_visible()
    expect(page.locator("#move-comparison")).to_contain_text("Original game move: Kf1")
    expect(page.locator("#move-comparison")).to_contain_text("Best move: Nxd4 - knight e2→d4")


def test_study_ui_click_to_move_and_next(page):
    page.locator('[data-square="e2"]').click()
    expect(page.locator("#instruction-text")).to_contain_text("Selected e2")
    page.locator('[data-square="d4"]').click()
    expect(page.locator("#instruction-text")).to_contain_text("e2→d4")

    page.locator("#btn-submit").click()
    page.locator("#btn-next").click()

    expect(page.locator("#concept-badge")).to_contain_text("Tactical activation")
    expect(page.locator("#game-link")).to_have_attribute("href", "https://lichess.org/blackgame2#26")
    expect(page.locator("#challenge-link")).to_have_attribute("href", "#puzzle-2")
    expect(page.locator("#player-clarifier")).to_have_text("You were black (tbonez) vs opponent.")
    expect(page).to_have_url(re.compile(r"#puzzle-2$"))


def test_study_ui_black_orientation_after_next(page):
    page.locator('[data-square="e2"]').click()
    page.locator('[data-square="d4"]').click()
    page.locator("#btn-submit").click()
    page.locator("#btn-next").click()

    first_square = page.locator("#board .square").first
    expect(first_square).to_have_attribute("data-square", "h1")
    expect(first_square.locator(".square-label.rank")).to_have_text("1")


def test_study_ui_hides_completed_puzzles(page):
    page.locator('[data-square="e2"]').click()
    page.locator('[data-square="d4"]').click()
    page.locator("#btn-submit").click()
    expect(page.locator("#stat-streak")).to_have_text("1")
    page.locator("#btn-next").click()
    expect(page.locator("#stat-total")).to_have_text("1")
    stored = page.evaluate("JSON.parse(localStorage.getItem('chess_progress'))")
    assert stored["1"]["times_seen"] == 1
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="networkidle")
    expect(page.locator("#stat-total")).to_have_text("1")
    expect(page.locator("#concept-badge")).to_contain_text("Tactical activation")


def test_study_ui_weakness_filter_and_replay_controls(page):
    page.locator('button:has(.concept-name:text("Tactical activation: counterattacking with tempo"))').click()
    expect(page.locator("#stat-total")).to_have_text("1")
    expect(page.locator("#concept-badge")).to_contain_text("Tactical activation")
    expect(page.locator("#clear-concept-filter")).to_be_visible()

    expect(page.locator("#replay-viewer .pgnvjs")).to_be_visible()
    expect(page.locator("#replay-viewer")).to_contain_text("1.")
    expect(page.locator("#replay-viewer")).to_contain_text("e4")


def test_study_ui_deep_links_to_specific_puzzle(page, live_server):
    page.goto(f"{live_server}#puzzle-2", wait_until="networkidle")

    expect(page.locator("#challenge-link")).to_have_text("Puzzle #2")
    expect(page.locator("#game-link")).to_have_attribute("href", "https://lichess.org/blackgame2#26")
    expect(page.locator("#concept-badge")).to_contain_text("Tactical activation")
    expect(page.locator("#progress-text")).to_have_text("2 / 2")
