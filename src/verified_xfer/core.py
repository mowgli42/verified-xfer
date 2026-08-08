"""Stage and retrieve orchestration with heavy verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .backends import Backend, LocalBackend, SFTPBackend
from .hashutil import file_sha256, file_size
from .ixdf_log import Status


def load_backend(cfg: dict[str, Any]) -> Backend:
    kind = cfg.get("backend", "local").lower()
    if kind == "local":
        return LocalBackend()
    if kind == "sftp":
        s = cfg.get("sftp") or {}
        return SFTPBackend(
            host=s["host"],
            port=int(s.get("port", 22)),
            username=s["username"],
            key_filename=s.get("key_filename"),
            password=s.get("password"),
        )
    raise SystemExit(f"Unknown backend: {kind!r}. Use 'local' or 'sftp'.")


def stage(cfg: dict[str, Any], status: Status, *, dry_run: bool = False, force: bool = False) -> int:
    source = Path(cfg["source_dir"])
    staging = cfg["staging_dir"].rstrip("/")
    backend = load_backend(cfg)

    if not source.is_dir():
        status.fail(
            f"source folder not found: {source}",
            "open config.yaml and fix source_dir (use forward slashes on Windows)",
        )
        return 1

    files = sorted(p for p in source.iterdir() if p.is_file())
    if not files:
        status.initialization("no files found in local upload folder", path=str(source))
        status.summary(0, 0, "staged")
        return 0

    status.initialization(
        f"{len(files)} file(s) to upload",
        local_source=str(source),
        linux_upload=staging,
    )
    local_meta: list[tuple[Path, int, str]] = []
    for p in files:
        sz = file_size(p)
        sha = file_sha256(p)
        status.file_info(p.name, sz, sha)
        local_meta.append((p, sz, sha))

    if dry_run:
        status.info("DRY-RUN    | no files will be written")
        for p, _, _ in local_meta:
            status.transfer("would →", f"{staging}/{p.name}")
        status.summary(len(files), len(files), "would be staged (dry-run)")
        return 0

    backend.ensure_dir(staging)
    ok = 0
    for p, expected_size, expected_sha in local_meta:
        remote = f"{staging}/{p.name}"
        status.transfer("→", remote)
        try:
            if not force:
                try:
                    existing = backend.list_files(staging)
                    if p.name in existing:
                        status.fail(
                            f"a file named {p.name} is already in the staging folder",
                            "move/rename it, or re-run with --force to replace it",
                        )
                        continue
                except Exception:
                    pass
            backend.put(p, remote)
            remote_size = backend.size(remote)
            remote_sha = backend.sha256(remote)
            size_ok = remote_size == expected_size
            hash_ok = remote_sha == expected_sha
            if size_ok and hash_ok:
                status.verify(True, f"size={remote_size} checksum={expected_sha[:12]}…")
                status.success(f"{p.name} copied and checked at {remote}")
                ok += 1
            else:
                detail = f"size {'OK' if size_ok else 'MISMATCH'}  hash {'OK' if hash_ok else 'MISMATCH'}"
                status.verify(False, detail)
                status.fail(
                    f"check failed for {p.name} — copy may be incomplete or in the wrong folder",
                    "delete that remote file and run stage again",
                )
        except Exception as exc:
            status.fail(
                f"could not copy or check {p.name}: {exc}",
                "confirm you can open the share folder and have write permission",
            )

    status.summary(ok, len(files), "staged")
    if hasattr(backend, "close"):
        backend.close()  # type: ignore
    return 0 if ok == len(files) else 1


def retrieve(cfg: dict[str, Any], status: Status, *, dry_run: bool = False) -> int:
    results = cfg["results_dir"].rstrip("/")
    dest = Path(cfg["retrieve_to"])
    backend = load_backend(cfg)

    status.initialization("listing linux logs/results folder", linux_logs=results)
    try:
        names = backend.list_files(results)
    except Exception as exc:
        status.fail(
            f"cannot open linux logs/results folder: {exc}",
            "confirm results_dir in config.yaml (separate from staging_dir) and that the share is mounted",
        )
        return 1

    if not names:
        status.initialization("linux logs/results folder is empty — nothing to retrieve")
        status.summary(0, 0, "retrieved")
        return 0

    status.initialization(
        f"{len(names)} file(s) to retrieve",
        linux_logs=results,
        local_retrieve=str(dest),
    )
    if dry_run:
        for name in names:
            status.transfer("would ←", f"{results}/{name}")
        status.summary(len(names), len(names), "would be retrieved (dry-run)")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name in names:
        remote = f"{results}/{name}"
        local = dest / name
        status.transfer("←", remote)
        try:
            backend.get(remote, local)
            remote_size = backend.size(remote)
            local_size = file_size(local)
            local_sha = file_sha256(local)
            if local_size == remote_size:
                status.verify(True, f"size={local_size} checksum={local_sha[:12]}…")
                status.success(f"{name} saved to {local}")
                ok += 1
            else:
                status.verify(False, f"size mismatch local={local_size} remote={remote_size}")
                status.fail(f"size check failed for {name}", "run retrieve again")
        except Exception as exc:
            status.fail(
                f"could not retrieve {name}: {exc}",
                "check folder permissions and free disk space",
            )

    status.summary(ok, len(names), "retrieved")
    if hasattr(backend, "close"):
        backend.close()  # type: ignore
    return 0 if ok == len(names) else 1
