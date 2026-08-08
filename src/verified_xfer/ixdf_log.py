"""IxDF / Nielsen visibility-of-system-status logging helpers.

Operators are often not software engineers. Every important step must answer:
  - what is happening / about to happen
  - what just succeeded or failed
  - concrete paths, sizes, short hashes (file fingerprints)
  - next safe action on error (plain language after →)
"""

from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("verified_xfer")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)
    return logger


def short_hash(h: str) -> str:
    return h[:12] + "…" if len(h) > 12 else h


class Status:
    """Thin wrapper that emits consistently formatted status lines."""

    def __init__(self, log: logging.Logger):
        self.log = log

    def initialization(self, msg: str, **kv: Any) -> None:
        extra = "  ".join(f"{k}={v}" for k, v in kv.items())
        self.log.info("INITIALIZATION | %s%s", msg, f"  {extra}" if extra else "")

    # Alias kept so older call sites / notes stay readable during transition.
    preflight = initialization

    def file_info(self, name: str, size: int, sha: str) -> None:
        self.log.info(
            "FILE       | %s  size=%d  checksum=%s",
            name,
            size,
            short_hash(sha),
        )

    def transfer(self, direction: str, path: str) -> None:
        self.log.info("TRANSFER   | %s %s", direction, path)

    def verify(self, ok: bool, detail: str) -> None:
        tag = "VERIFY     | OK  " if ok else "VERIFY     | FAIL"
        self.log.info("%s %s", tag, detail)

    def success(self, msg: str) -> None:
        self.log.info("SUCCESS    | %s", msg)

    def fail(self, msg: str, hint: str = "") -> None:
        self.log.error("FAIL       | %s%s", msg, f"  → {hint}" if hint else "")

    def next_step(self, msg: str) -> None:
        """Plain-language guidance for non-technical operators."""
        self.log.info("NEXT       | %s", msg)

    def summary(self, ok: int, total: int, action: str) -> None:
        status = "OK" if ok == total else "PARTIAL"
        self.log.info("SUMMARY    | %s  %d/%d files %s", status, ok, total, action)
        if ok == total and total > 0:
            self.next_step(f"All {total} file(s) {action}. Safe to continue.")
        elif total == 0:
            self.next_step("No files found. Check the folder path in your config.")
        else:
            self.next_step(
                f"{total - ok} file(s) need attention. Scroll up for FAIL lines and the → hints."
            )

    def info(self, msg: str) -> None:
        self.log.info("%s", msg)
