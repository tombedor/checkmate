from __future__ import annotations

import json
from pathlib import Path

from src import render


def test_lichess_move_anchor_for_white_and_black():
    assert render._lichess_move_anchor(1, "white") == 1
    assert render._lichess_move_anchor(1, "black") == 2
    assert render._lichess_move_anchor(15, "white") == 29
    assert render._lichess_move_anchor(15, "black") == 30


def test_render_html_writes_bundle(monkeypatch, tmp_path: Path):
    sample_challenges = [
        {
            "id": 99,
            "game_id": "abc123",
            "move_number": 3,
            "fen": "8/8/8/8/8/8/P7/8 w - - 0 1",
            "context": "Sample context",
            "concept": "general",
            "correct_move_uci": "a2a4",
            "user_color": "white",
            "white": "tbonez",
            "black": "opponent",
        }
    ]
    sample_focus = [{"theme": "Opening", "count": 1, "score": 2.0, "reason": "Sample"}]

    monkeypatch.setattr(render, "get_challenge_queue", lambda: sample_challenges)
    monkeypatch.setattr(render, "get_lichess_focus_recommendations", lambda: sample_focus)

    render.render_html(str(tmp_path / "study.html"))

    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "app.js").exists()
    assert (tmp_path / "styles.css").exists()
    assert (tmp_path / "study.html").exists()
    assert (tmp_path / "vendor" / "pgnv.js").exists()

    payload = json.loads((tmp_path / "study-data.json").read_text())
    assert payload["challenges"][0]["game_base_url"] == "https://lichess.org/abc123"
    assert payload["challenges"][0]["game_move_anchor"] == 5
    assert payload["challenges"][0]["game_url"] == "https://lichess.org/abc123#5"
    assert payload["challenges"][0]["correct_move_from"] == "a2"
    assert payload["challenges"][0]["correct_move_to"] == "a4"
    assert payload["challenges"][0]["correct_move_piece"] == "pawn"
    assert payload["challenges"][0]["correct_move_legal"] is True
    assert payload["challenges"][0]["correct_move_display"] == "a4 - pawn a2→a4"
    assert payload["concept_counts"] == {"general": 1}
    assert payload["lichess_focus"][0]["theme"] == "Opening"
    assert payload["lichess_focus"][0]["theme_url"] == "https://lichess.org/training/opening"
    assert payload["lichess_focus"][0]["theme_linkable"] is True
