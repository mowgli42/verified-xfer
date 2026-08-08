"""IxDF / Nielsen visibility-of-system-status logging helpers.

Every important step must answer:
  - what is happening / about to happen
  - what just succeeded or failed
  - concrete paths, sizes, short hashes
  - next safe action on error
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

    def preflight(self, msg: str, **kv: Any) -> None:
        extra = "  ".join(f"{k}={v}" for k, v in kv.items())
        self.log.info("PRE-FLIGHT | %s%s", msg, f"  {extra}" if extra else "")

    def file_info(self, name: str, size: int, sha: str) -> None:
        self.log.info("FILE       | %s  size=%d  sha256=%s", name, size, short_hash(sha))

    def transfer(self, direction: str, path: str) -> None:
        self.log.info("TRANSFER   | %s %s", direction, path)

    def verify(self, ok: bool, detail: str) -> None:
        tag = "VERIFY     | OK  " if ok else "VERIFY     | FAIL"
        self.log.info("%s %s", tag, detail)

    def success(self, msg: str) -> None:
        self.log.info("SUCCESS    | %s", msg)

    def fail(self, msg: str, hint: str = "") -> None:
        self.log.error("FAIL       | %s%s", msg, f"  → {hint}" if hint else "")

    def summary(self, ok: int, total: int, action: str) -> None:
        status = "OK" if ok == total else "PARTIAL"
        self.log.info("SUMMARY    | %s  %d/%d files %s", status, ok, total, action)

    def info(self, msg: str) -> None:
        self.log.info("%s", msg)
