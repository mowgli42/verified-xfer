"""CLI interactive / one-shot behaviour."""

from __future__ import annotations

import tempfile
from pathlib import Path

from verified_xfer.cli import interactive_loop, main
from verified_xfer.ixdf_log import Status, setup_logging


def _write_cfg(tmp: Path) -> Path:
    src = tmp / "source"
    staging = tmp / "staging"
    results = tmp / "results"
    dest = tmp / "retrieved"
    for d in (src, staging, results, dest):
        d.mkdir()
    (src / "a.txt").write_text("hi\n")
    cfg = tmp / "config.yaml"
    cfg.write_text(
        "\n".join(
            [
                "backend: local",
                f"source_dir: {src}",
                f"staging_dir: {staging}",
                f"results_dir: {results}",
                f"retrieve_to: {dest}",
                "",
            ]
        )
    )
    return cfg


def test_one_shot_stage_still_works():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cfg = _write_cfg(tmp)
        rc = main(["stage", "-c", str(cfg), "--dry-run"])
        assert rc == 0


def test_interactive_stage_then_quit(monkeypatch):
    answers = iter(["1", "3"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cfg_path = _write_cfg(tmp)
        # Load via main interactive path using monkeypatched input after config load
        # Drive interactive_loop directly with loaded cfg
        from verified_xfer.config import load_config

        cfg, _, _ = load_config(str(cfg_path))
        log = setup_logging(False)
        status = Status(log)
        rc = interactive_loop(status, cfg, dry_run=True)
        assert rc == 0
