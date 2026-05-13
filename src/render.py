import json
import shutil
from pathlib import Path

from src.study_plan import get_challenge_queue, get_lichess_focus_recommendations


WEB_DIR = Path(__file__).parent / "web"


def _build_concept_counts(challenges: list[dict]) -> dict[str, int]:
    concept_counts: dict[str, int] = {}
    for challenge in challenges:
        concept = challenge.get("concept") or "general"
        concept_counts[concept] = concept_counts.get(concept, 0) + 1
    return concept_counts


def _augment_challenges(challenges: list[dict]) -> list[dict]:
    augmented = []
    for challenge in challenges:
        row = dict(challenge)
        game_id = row.get("game_id", "")
        row["game_url"] = f"https://lichess.org/{game_id}" if game_id else "https://lichess.org/"
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
        "lichess_focus": get_lichess_focus_recommendations(),
    }

    (output_dir / "study-data.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    for name in ("index.html", "app.js", "styles.css"):
        shutil.copyfile(WEB_DIR / name, output_dir / name)

    # Backward compatibility for previous links/bookmarks.
    shutil.copyfile(output_dir / "index.html", output_dir / "study.html")

    print(f"Rendered {len(challenges)} challenges to {output_dir / 'index.html'}")
