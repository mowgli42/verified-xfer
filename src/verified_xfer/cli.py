"""CLI entry point — interactive by default when config is present."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from .config import (
    candidate_paths,
    format_config_summary,
    load_config,
    validate_folders,
)
from .core import retrieve, stage
from .ixdf_log import Status, setup_logging


def _print_config(status: Status, cfg: dict[str, Any], cfg_path, source_label: str) -> None:
    status.initialization("config ready — four folders")
    for line in format_config_summary(cfg, cfg_path, source_label):
        status.info(f"  CONFIG | {line}")


def _load_or_fail(status: Status, config_path: str | None) -> tuple[dict[str, Any], Any, str] | None:
    cfg, cfg_path, source_label = load_config(config_path)
    if not cfg:
        status.fail(
            "no config file found",
            "copy config.example.yaml to ./config.yaml (or system-wide) and run again",
        )
        status.next_step("Tip: verified-xfer --show-config-paths lists where we look.")
        status.info("Searched:")
        for label, path in candidate_paths(config_path):
            status.info(f"  {label}: {path}")
        return None

    folder_err = validate_folders(cfg)
    if folder_err:
        status.fail(folder_err, "see the four-folder section in config.example.yaml")
        return None

    return cfg, cfg_path, source_label


def _run_action(
    status: Status,
    cfg: dict[str, Any],
    action: str,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> int:
    if action == "stage":
        return stage(cfg, status, dry_run=dry_run, force=force)
    return retrieve(cfg, status, dry_run=dry_run)


def interactive_loop(
    status: Status,
    cfg: dict[str, Any],
    *,
    dry_run: bool = False,
    force: bool = False,
) -> int:
    """Simple menu: pick Stage / Retrieve, Enter, watch the scrolling log."""
    last_rc = 0
    while True:
        status.info("")
        status.info("Select an action, then press Enter:")
        status.info("  [1] Stage     — upload local files to the Linux folder")
        status.info("  [2] Retrieve  — pull results / logs back to this PC")
        status.info("  [3] Quit")
        try:
            choice = input("Choice [1]: ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            status.info("")
            status.next_step("Stopped. Run verified-xfer again when ready.")
            return last_rc

        if choice in {"3", "q", "Q", "quit"}:
            status.next_step("Done.")
            return last_rc

        if choice in {"1", "s", "S", "stage"}:
            action = "stage"
        elif choice in {"2", "r", "R", "retrieve"}:
            action = "retrieve"
        else:
            status.fail(f"unknown choice: {choice!r}", "enter 1, 2, or 3")
            continue

        status.info("")
        status.initialization(f"starting {action}")
        last_rc = _run_action(status, cfg, action, dry_run=dry_run, force=force)
        status.info("")
        if last_rc == 0:
            status.next_step("Finished. Pick another action, or 3 to quit.")
        else:
            status.next_step("That run had problems — scroll up for FAIL lines, or try again.")


def launch_web(*, host: str = "127.0.0.1", port: int = 8765) -> int:
    """Start the local operator UI (same select → Run → scrolling log)."""
    try:
        import uvicorn
    except ImportError:
        print(
            "FAIL | web extras not installed  → pip install -e \".[web]\"",
            file=sys.stderr,
        )
        return 1

    print(f"NEXT | Opening operator UI at http://{host}:{port}")
    print("NEXT | Select Stage or Retrieve, click Run, watch the live log.")
    uvicorn.run(
        "verified_xfer.web.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verified-xfer",
        description=(
            "Verified file stage/retrieve. "
            "With a default config present, just run: verified-xfer"
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["stage", "retrieve", "web"],
        help="Optional. Omit for the interactive menu. Use 'web' for the browser UI.",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Config path (default: search cwd → user → system-wide)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--force", action="store_true", help="Allow overwriting on stage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument(
        "--show-config-paths",
        action="store_true",
        help="Print config search order and exit",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Web UI host (with 'web')")
    parser.add_argument("--port", type=int, default=8765, help="Web UI port (with 'web')")
    args = parser.parse_args(argv)

    log = setup_logging(args.verbose)
    status = Status(log)

    if args.show_config_paths:
        status.info("CONFIG SEARCH ORDER (first existing file wins)")
        for label, path in candidate_paths(args.config):
            exists = "EXISTS" if path.is_file() else "missing"
            status.info(f"  [{exists:7}] {label}: {path}")
        return 0

    if args.command == "web":
        return launch_web(host=args.host, port=args.port)

    loaded = _load_or_fail(status, args.config)
    if not loaded:
        return 1
    cfg, cfg_path, source_label = loaded
    _print_config(status, cfg, cfg_path, source_label)

    if args.command in {"stage", "retrieve"}:
        return _run_action(
            status,
            cfg,
            args.command,
            dry_run=args.dry_run,
            force=args.force,
        )

    # Default: interactive menu for non-technical operators
    status.next_step("Config found. Choose Stage or Retrieve below.")
    return interactive_loop(status, cfg, dry_run=args.dry_run, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
