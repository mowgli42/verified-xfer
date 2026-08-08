"""CLI entry point."""

from __future__ import annotations

import argparse
import sys

from .config import candidate_paths, format_config_summary, load_config, validate_folders
from .core import retrieve, stage
from .ixdf_log import Status, setup_logging


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verified-xfer",
        description=(
            "Upload test files from a local folder to a Linux folder, "
            "then retrieve logs/results from a separate Linux folder."
        ),
    )
    parser.add_argument("command", choices=["stage", "retrieve"], help="Action to perform")
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Explicit config path (otherwise searches cwd → user → system-wide)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without writing")
    parser.add_argument("--force", action="store_true", help="Allow overwriting existing remote files (stage only)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Debug logging")
    parser.add_argument(
        "--show-config-paths",
        action="store_true",
        help="Print the search order for config files and exit",
    )
    args = parser.parse_args(argv)

    log = setup_logging(args.verbose)
    status = Status(log)

    if args.show_config_paths:
        status.info("CONFIG SEARCH ORDER (first existing file wins)")
        for label, path in candidate_paths(args.config):
            exists = "EXISTS" if path.is_file() else "missing"
            status.info(f"  [{exists:7}] {label}: {path}")
        return 0

    cfg, cfg_path, source_label = load_config(args.config)

    if not cfg:
        status.fail(
            "no config file found",
            "copy config.example.yaml to a search location, then re-run",
        )
        status.next_step("Run with --show-config-paths to see exactly where we look.")
        status.info("Searched:")
        for label, path in candidate_paths(args.config):
            status.info(f"  {label}: {path}")
        return 1

    # Always show the effective config early (IxDF visibility)
    status.initialization("effective configuration — four folders")
    for line in format_config_summary(cfg, cfg_path, source_label):
        status.info(f"  CONFIG | {line}")

    folder_err = validate_folders(cfg)
    if folder_err:
        status.fail(folder_err, "see the four-folder section in config.example.yaml")
        return 1

    if args.command == "stage":
        return stage(cfg, status, dry_run=args.dry_run, force=args.force)
    return retrieve(cfg, status, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
