"""Stdlib-only size and SHA-256 helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path


def file_size(path: Path) -> int:
    return path.stat().st_size


def file_sha256(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
