#!/usr/bin/env python3
"""Serve the generated study UI over localhost."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


class StudyHandler(SimpleHTTPRequestHandler):
    def __init__(
        self,
        *args,
        directory: str | None = None,
        db_path: str | None = None,
        **kwargs,
    ):
        self.db_path = db_path
        super().__init__(*args, directory=directory, **kwargs)

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _get_progress_rows(self) -> dict[str, dict]:
        if not self.db_path or not os.path.exists(self.db_path):
            return {}

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT id, times_seen, times_correct, next_review
                FROM challenges
                WHERE times_seen > 0 OR times_correct > 0 OR next_review IS NOT NULL
                """
            ).fetchall()
        finally:
            conn.close()

        return {
            str(row["id"]): {
                "times_seen": row["times_seen"],
                "times_correct": row["times_correct"],
                "next_review": row["next_review"],
            }
            for row in rows
        }

    def _record_progress(self, challenge_id: int, correct: bool) -> dict | None:
        if not self.db_path or not os.path.exists(self.db_path):
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute(
                """
                UPDATE challenges
                SET times_seen = COALESCE(times_seen, 0) + 1,
                    times_correct = COALESCE(times_correct, 0) + ?,
                    next_review = datetime('now')
                WHERE id = ?
                """,
                (1 if correct else 0, challenge_id),
            )
            conn.commit()
            row = conn.execute(
                """
                SELECT id, times_seen, times_correct, next_review
                FROM challenges
                WHERE id = ?
                """,
                (challenge_id,),
            ).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return {
            "times_seen": row["times_seen"],
            "times_correct": row["times_correct"],
            "next_review": row["next_review"],
        }

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/progress":
            self._send_json({"progress": self._get_progress_rows()})
            return

        if self.path in ("", "/"):
            self.path = "/index.html"
        elif self.path == "/study.html":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/progress":
            self.send_error(404, "Not Found")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json({"error": "Invalid Content-Length"}, status=400)
            return

        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        challenge_id = payload.get("challenge_id")
        correct = bool(payload.get("correct", False))
        if not isinstance(challenge_id, int):
            self._send_json({"error": "challenge_id must be an integer"}, status=400)
            return

        progress = self._record_progress(challenge_id, correct)
        if progress is None:
            self._send_json({"error": "Challenge not found"}, status=404)
            return

        self._send_json({"challenge_id": challenge_id, "progress": progress}, status=200)


def main():
    parser = argparse.ArgumentParser(description="Serve the generated study page locally")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    db_path = os.path.join(output_dir, "chess_tutor.db")
    handler = partial(StudyHandler, directory=output_dir, db_path=db_path)
    server = ThreadingHTTPServer((args.host, args.port), handler)

    print(f"Serving study UI at http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
