"""Minimal backends: local filesystem and SFTP."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Protocol

from .hashutil import file_sha256, file_size


class Backend(Protocol):
    def ensure_dir(self, remote_path: str) -> None: ...
    def put(self, local: Path, remote: str) -> None: ...
    def get(self, remote: str, local: Path) -> None: ...
    def list_files(self, remote_dir: str) -> list[str]: ...
    def size(self, remote: str) -> int: ...
    def sha256(self, remote: str) -> str: ...


class LocalBackend:
    """Treat remote paths as ordinary filesystem paths (NFS/SMB mounts, same host)."""

    def ensure_dir(self, remote_path: str) -> None:
        Path(remote_path).mkdir(parents=True, exist_ok=True)

    def put(self, local: Path, remote: str) -> None:
        dest = Path(remote)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local, dest)

    def get(self, remote: str, local: Path) -> None:
        local.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(remote, local)

    def list_files(self, remote_dir: str) -> list[str]:
        p = Path(remote_dir)
        if not p.is_dir():
            return []
        return sorted(f.name for f in p.iterdir() if f.is_file())

    def size(self, remote: str) -> int:
        return file_size(Path(remote))

    def sha256(self, remote: str) -> str:
        return file_sha256(Path(remote))


class SFTPBackend:
    """SFTP via paramiko. Hash is obtained by a temporary download (simple & correct)."""

    def __init__(self, host: str, port: int, username: str, key_filename: str | None = None, password: str | None = None):
        try:
            import paramiko
        except ImportError as e:
            raise SystemExit("SFTP backend requires paramiko.  pip install 'verified-xfer[sftp]'") from e

        self._paramiko = paramiko
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connect_kwargs: dict = {"hostname": host, "port": port, "username": username}
        if key_filename:
            connect_kwargs["key_filename"] = str(Path(key_filename).expanduser())
        if password:
            connect_kwargs["password"] = password
        self.client.connect(**connect_kwargs)
        self.sftp = self.client.open_sftp()

    def close(self) -> None:
        self.sftp.close()
        self.client.close()

    def ensure_dir(self, remote_path: str) -> None:
        # naive but sufficient: try mkdir -p style
        parts = Path(remote_path).parts
        current = ""
        for part in parts:
            current = f"{current}/{part}" if current else part
            if not current:
                continue
            try:
                self.sftp.stat(current)
            except FileNotFoundError:
                self.sftp.mkdir(current)

    def put(self, local: Path, remote: str) -> None:
        self.ensure_dir(str(Path(remote).parent))
        self.sftp.put(str(local), remote)

    def get(self, remote: str, local: Path) -> None:
        local.parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(remote, str(local))

    def list_files(self, remote_dir: str) -> list[str]:
        try:
            return sorted(f.filename for f in self.sftp.listdir_attr(remote_dir) if not f.st_mode & 0o040000)
        except FileNotFoundError:
            return []

    def size(self, remote: str) -> int:
        return self.sftp.stat(remote).st_size

    def sha256(self, remote: str) -> str:
        # Simple correct approach: download to temp and hash
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            self.get(remote, tmp_path)
            return file_sha256(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)
