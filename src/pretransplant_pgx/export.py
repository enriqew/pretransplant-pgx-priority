"""Export priority scores to static JSON artefacts for the portfolio dashboard."""
from __future__ import annotations

import json
import dataclasses
from pathlib import Path

from .priority_score import compute_priorities

DEFAULT_PGX_PATH = Path(__file__).parents[2] / "data" / "raw"
DEFAULT_OUT_PATH = Path(__file__).parents[2] / "data" / "exports" / "genotyping-priority.json"


def _find_latest_snapshot(raw_dir: Path, prefix: str) -> Path | None:
    """Return the most recent snapshot subdirectory matching prefix."""
    candidates = sorted(
        [d for d in raw_dir.iterdir() if d.is_dir() and d.name.startswith(prefix)],
        reverse=True,
    )
    return candidates[0] if candidates else None


def run(
    pgx_path: Path | None = None,
    waitlist_path: Path | None = None,
    out_path: Path | None = None,
) -> None:
    raw_dir = pgx_path or DEFAULT_PGX_PATH
    out_file = out_path or DEFAULT_OUT_PATH

    pgx_snap = _find_latest_snapshot(raw_dir, "pgx_artifacts")
    waitlist_snap = _find_latest_snapshot(raw_dir, "waitlist_artifacts")

    if pgx_snap is None or waitlist_snap is None:
        raise FileNotFoundError(
            "Raw snapshots not found. Run `make ingest` first.\n"
            f"  pgx_artifacts:     {'found' if pgx_snap else 'MISSING'}\n"
            f"  waitlist_artifacts: {'found' if waitlist_snap else 'MISSING'}"
        )

    actionability_file = pgx_snap / "actionability_ranking.json"
    waitlist_file = waitlist_snap / "world-waitlist.json"

    actionability = json.loads(actionability_file.read_text())
    waitlist = json.loads(waitlist_file.read_text())

    entries = compute_priorities(actionability, waitlist)
    payload = [dataclasses.asdict(e) for e in entries]

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Exported {len(payload)} priority entries → {out_file}")


if __name__ == "__main__":
    run()
