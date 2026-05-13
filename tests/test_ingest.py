from __future__ import annotations

from pathlib import Path

from src import db, ingest


SAMPLE_PGN = """[Event "Rated Blitz game"]
[Site "https://lichess.org/abcd1234"]
[Date "2026.05.01"]
[White "tbonez"]
[Black "opponent1"]
[Result "1-0"]
[WhiteElo "1800"]
[BlackElo "1820"]
[TimeControl "300+0"]
[ECO "C20"]
[Opening "King's Pawn Game"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 1-0

[Event "Rated Blitz game"]
[Site "https://lichess.org/efgh5678"]
[Date "2026.05.02"]
[White "opponent2"]
[Black "tbonez"]
[Result "0-1"]
[WhiteElo "1810"]
[BlackElo "1830"]
[TimeControl "300+0"]
[ECO "B01"]
[Opening "Scandinavian Defense"]

1. e4 d5 2. exd5 Qxd5 3. Nc3 Qa5 0-1
"""


def test_ingest_pgn_infers_username_and_reuses_existing(tmp_path: Path, monkeypatch):
    pgn_path = tmp_path / "sample.pgn"
    pgn_path.write_text(SAMPLE_PGN, encoding="utf-8")

    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()

    added, username, stats = ingest.ingest_pgn(str(pgn_path))
    assert username == "tbonez"
    assert added == 2
    assert stats["total_games"] == 2
    assert stats["skipped_existing"] == 0

    added_again, username_again, stats_again = ingest.ingest_pgn(str(pgn_path))
    assert username_again == "tbonez"
    assert added_again == 0
    assert stats_again["skipped_existing"] == 2
