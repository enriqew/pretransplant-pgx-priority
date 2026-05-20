"""Shared utilities for ingest modules."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


def snapshot_dir(repo_root: Path, prefix: str, snapshot_date: str | None = None) -> Path:
    """Return (and create) a dated snapshot directory under data/raw/."""
    tag = snapshot_date or date.today().isoformat()
    out = repo_root / "data" / "raw" / f"{prefix}_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_meta(out_dir: Path, source: str, files: list[dict]) -> None:
    meta = {
        "source": source,
        "snapshot_date": out_dir.name.split("_")[-1],
        "files": files,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
