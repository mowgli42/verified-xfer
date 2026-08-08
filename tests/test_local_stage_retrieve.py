"""Smoke tests that mirror the core Gherkin scenarios using LocalBackend."""

from __future__ import annotations

import tempfile
from pathlib import Path

from verified_xfer.core import retrieve, stage
from verified_xfer.ixdf_log import Status, setup_logging


def _cfg(tmp: Path) -> dict:
    src = tmp / "source"
    staging = tmp / "staging"
    results = tmp / "results"
    dest = tmp / "retrieved"
    src.mkdir()
    staging.mkdir()
    results.mkdir()
    (src / "input.bin").write_bytes(b"hello-test-data-42")
    (src / "config.yaml").write_text("key: value\n")
    return {
        "backend": "local",
        "source_dir": str(src),
        "staging_dir": str(staging),
        "results_dir": str(results),
        "retrieve_to": str(dest),
    }


def test_stage_and_retrieve_roundtrip():
    log = setup_logging(verbose=False)
    status = Status(log)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cfg = _cfg(tmp)

        rc = stage(cfg, status, dry_run=False, force=False)
        assert rc == 0
        staged = list((tmp / "staging").iterdir())
        assert len(staged) == 2
        assert (tmp / "staging" / "input.bin").read_bytes() == b"hello-test-data-42"

        (tmp / "results" / "output.bin").write_bytes(b"result-data")
        (tmp / "results" / "test.log").write_text("PASS\n")

        rc = retrieve(cfg, status, dry_run=False)
        assert rc == 0
        retrieved = list((tmp / "retrieved").iterdir())
        assert len(retrieved) == 2
        assert (tmp / "retrieved" / "output.bin").read_bytes() == b"result-data"
        assert (tmp / "retrieved" / "test.log").read_text() == "PASS\n"


def test_dry_run_writes_nothing():
    log = setup_logging(verbose=False)
    status = Status(log)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cfg = _cfg(tmp)
        rc = stage(cfg, status, dry_run=True)
        assert rc == 0
        assert list((tmp / "staging").iterdir()) == []


def test_staging_and_results_must_differ():
    from verified_xfer.config import validate_folders

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cfg = _cfg(tmp)
        assert validate_folders(cfg) is None
        cfg["results_dir"] = cfg["staging_dir"]
        err = validate_folders(cfg)
        assert err is not None
        assert "different folders" in err
