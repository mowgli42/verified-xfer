"""IxDF / Nielsen visibility-of-system-status logging helpers.

Operators are often not software engineers. Every important step must answer:
  - what is happening / about to happen
  - what just succeeded or failed
  - concrete paths, sizes, short hashes (file fingerprints)
  - next safe action on error (plain language after →)

Graham-bell note: Status can also push each line into an in-memory list so the
web UI can stream a scrolling log without re-implementing the message format.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Callable


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
    """Thin wrapper that emits consistently formatted status lines.

    Optional `on_line` callback receives the same human-readable message that
    was logged (without timestamp/level prefix). Used by the FastAPI web UI
    to feed a scrolling log pane.
    """

    def __init__(self, log: logging.Logger, on_line: Callable[[str], None] | None = None):
        self.log = log
        self.on_line = on_line
        self.lines: list[str] = []

    def _emit(self, level: int, message: str) -> None:
        self.log.log(level, message)
        self.lines.append(message)
        if self.on_line:
            try:
                self.on_line(message)
            except Exception:
                pass  # never let UI capture break the transfer

    def initialization(self, msg: str, **kv: Any) -> None:
        extra = "  ".join(f"{k}={v}" for k, v in kv.items())
        self._emit(logging.INFO, f"INITIALIZATION | {msg}{f'  {extra}' if extra else ''}")

    # Alias kept so older call sites / notes stay readable during transition.
    preflight = initialization

    def file_info(self, name: str, size: int, sha: str) -> None:
        self._emit(
            logging.INFO,
            f"FILE       | {name}  size={size}  checksum={short_hash(sha)}",
        )

    def transfer(self, direction: str, path: str) -> None:
        self._emit(logging.INFO, f"TRANSFER   | {direction} {path}")

    def verify(self, ok: bool, detail: str) -> None:
        tag = "VERIFY     | OK  " if ok else "VERIFY     | FAIL"
        self._emit(logging.INFO, f"{tag} {detail}")

    def success(self, msg: str) -> None:
        self._emit(logging.INFO, f"SUCCESS    | {msg}")

    def fail(self, msg: str, hint: str = "") -> None:
        self._emit(logging.ERROR, f"FAIL       | {msg}{f'  → {hint}' if hint else ''}")

    def next_step(self, msg: str) -> None:
        """Plain-language guidance for non-technical operators."""
        self._emit(logging.INFO, f"NEXT       | {msg}")

    def summary(self, ok: int, total: int, action: str) -> None:
        status = "OK" if ok == total else "PARTIAL"
        self._emit(logging.INFO, f"SUMMARY    | {status}  {ok}/{total} files {action}")
        if ok == total and total > 0:
            self.next_step(f"All {total} file(s) {action}. Safe to continue.")
        elif total == 0:
            self.next_step("No files found. Check the folder path in your config.")
        else:
            self.next_step(
                f"{total - ok} file(s) need attention. Scroll up for FAIL lines and the → hints."
            )

    def info(self, msg: str) -> None:
        self._emit(logging.INFO, msg)
