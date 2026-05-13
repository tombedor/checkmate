from __future__ import annotations

import json
from pathlib import Path

from src import render


def test_render_html_writes_bundle(monkeypatch, tmp_path: Path):
    sample_challenges = [
        {
            "id": 99,
            "game_id": "abc123",
            "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
            "context": "Sample context",
            "concept": "general",
            "correct_move_uci": "a2a4",
            "user_color": "white",
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

    payload = json.loads((tmp_path / "study-data.json").read_text())
    assert payload["challenges"][0]["game_url"] == "https://lichess.org/abc123"
    assert payload["concept_counts"] == {"general": 1}
    assert payload["lichess_focus"] == sample_focus
