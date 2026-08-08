"""Config discovery: explicit path → cwd → user → system-wide.

On Windows the system-wide location is %PROGRAMDATA%\\verified-xfer\\config.yaml
so a lab machine can ship one shared config that every operator picks up.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml


def _windows_programdata() -> Path | None:
    pd = os.environ.get("PROGRAMDATA")
    if pd:
        return Path(pd) / "verified-xfer" / "config.yaml"
    return None


def _windows_appdata() -> Path | None:
    ad = os.environ.get("APPDATA")
    if ad:
        return Path(ad) / "verified-xfer" / "config.yaml"
    return None


def _xdg_config_home() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "verified-xfer" / "config.yaml"
    return Path.home() / ".config" / "verified-xfer" / "config.yaml"


def candidate_paths(explicit: str | None = None) -> list[tuple[str, Path]]:
    """Return ordered (label, path) pairs that will be checked."""
    candidates: list[tuple[str, Path]] = []

    if explicit:
        candidates.append(("explicit --config", Path(explicit)))

    candidates.append(("cwd ./config.yaml", Path.cwd() / "config.yaml"))

    # User-level
    if sys.platform == "win32":
        user = _windows_appdata()
        if user:
            candidates.append(("user %APPDATA%", user))
    else:
        candidates.append(("user XDG/config", _xdg_config_home()))

    # System-wide (machine-wide on Windows)
    if sys.platform == "win32":
        syswide = _windows_programdata()
        if syswide:
            candidates.append(("system %PROGRAMDATA%", syswide))
    else:
        candidates.append(("system /etc", Path("/etc/verified-xfer/config.yaml")))

    return candidates


def find_config(explicit: str | None = None) -> tuple[Path, str] | None:
    """Return (path, label) of the first existing config, or None."""
    for label, path in candidate_paths(explicit):
        if path.is_file():
            return path, label
    return None


def load_config(explicit: str | None = None) -> tuple[dict[str, Any], Path, str]:
    """Load and return (cfg, path_used, source_label). Raises SystemExit-style errors via return of empty."""
    found = find_config(explicit)
    if not found:
        return {}, Path(), ""
    path, label = found
    with path.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg, path, label


def redact_for_log(cfg: dict[str, Any]) -> dict[str, Any]:
    """Return a copy safe to print: hide passwords / private keys content."""
    safe = dict(cfg)
    sftp = safe.get("sftp")
    if isinstance(sftp, dict):
        sftp = dict(sftp)
        if "password" in sftp and sftp["password"]:
            sftp["password"] = "***"
        if "key_filename" in sftp:
            # keep the path, just note it
            pass
        safe["sftp"] = sftp
    return safe


def format_config_summary(cfg: dict[str, Any], path: Path, label: str) -> list[str]:
    """Human-readable lines describing the effective config for the log."""
    safe = redact_for_log(cfg)
    lines = [
        f"source={label}",
        f"path={path}",
        f"backend={safe.get('backend', 'local')}",
        f"source_dir={safe.get('source_dir', '—')}",
        f"staging_dir={safe.get('staging_dir', '—')}",
        f"results_dir={safe.get('results_dir', '—')}",
        f"retrieve_to={safe.get('retrieve_to', '—')}",
    ]
    if safe.get("backend") == "sftp" and isinstance(safe.get("sftp"), dict):
        s = safe["sftp"]
        lines.append(f"sftp.host={s.get('host', '—')}")
        lines.append(f"sftp.user={s.get('username', '—')}")
        lines.append(f"sftp.key={s.get('key_filename', '—')}")
    return lines
