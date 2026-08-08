"""CLI integration tests for config discovery scenarios."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "verified_xfer", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_show_config_paths():
    with tempfile.TemporaryDirectory() as td:
        proc = _run("stage", "--show-config-paths", cwd=Path(td))
        assert proc.returncode == 0
        assert "CONFIG SEARCH ORDER" in proc.stdout
        assert "missing" in proc.stdout or "EXISTS" in proc.stdout


def test_config_not_found():
    with tempfile.TemporaryDirectory() as td:
        proc = _run("stage", cwd=Path(td))
        assert proc.returncode == 1
        assert "FAIL" in proc.stdout or "FAIL" in proc.stderr
        combined = proc.stdout + proc.stderr
        assert "no config file found" in combined.lower() or "config" in combined.lower()
