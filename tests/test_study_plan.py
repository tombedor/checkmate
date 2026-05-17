from __future__ import annotations

from src import study_plan


def test_lichess_focus_recommendations_cover_motif_advanced_and_mates(monkeypatch):
    sample = [
        {
            "concept": "Capture the defender to force a back rank mate",
            "explanation": "A quiet move first, then remove the defender and finish with back rank mate.",
            "context": "The position demanded a quiet move and a mating net on the back rank.",
            "phase": "middlegame",
            "priority": 12.5,
        }
    ]

    monkeypatch.setattr(study_plan, "get_challenge_queue", lambda: sample)
    recommendations = study_plan.get_lichess_focus_recommendations(limit=10)
    themes = {item["theme"] for item in recommendations}

    assert "Capture the defender" in themes
    assert "Quiet move" in themes
    assert "Back rank mate" in themes


def test_describe_uci_move_returns_verified_move_details():
    details = study_plan.describe_uci_move(
        "rq2r2k/p3bQpp/5n2/Pbp1pN2/8/2P5/P2P2PP/RNB2RK1 b - - 5 19",
        "e7f8",
    )

    assert details["is_legal"] is True
    assert details["san"] == "Bf8"
    assert details["from_square"] == "e7"
    assert details["to_square"] == "f8"
    assert details["piece"] == "bishop"
    assert details["display"] == "Bf8 - bishop e7→f8"
