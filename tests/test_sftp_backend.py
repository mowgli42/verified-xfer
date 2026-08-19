"""Mocked SFTPBackend tests — no live SSH host required."""

from __future__ import annotations

import stat
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from verified_xfer.backends import SFTPBackend
from verified_xfer.hashutil import file_sha256


class _Attr:
    def __init__(self, filename: str, is_dir: bool = False, size: int = 0):
        self.filename = filename
        self.st_mode = stat.S_IFDIR | 0o755 if is_dir else stat.S_IFREG | 0o644
        self.st_size = size


class FakeSFTP:
    """In-memory SFTP that speaks the paramiko methods SFTPBackend uses."""

    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}
        self.dirs: set[str] = set()

    def _norm(self, path: str) -> str:
        return path.replace("\\", "/").rstrip("/") or "/"

    def stat(self, path: str):
        path = self._norm(path)
        if path in self.dirs or path == "/":
            return _Attr(path, is_dir=True)
        if path in self.files:
            return _Attr(path, size=len(self.files[path]))
        raise FileNotFoundError(path)

    def mkdir(self, path: str) -> None:
        self.dirs.add(self._norm(path))

    def put(self, local: str, remote: str) -> None:
        self.files[self._norm(remote)] = Path(local).read_bytes()

    def get(self, remote: str, local: str) -> None:
        Path(local).write_bytes(self.files[self._norm(remote)])

    def listdir_attr(self, remote_dir: str):
        prefix = self._norm(remote_dir).rstrip("/") + "/"
        out = []
        for path, data in self.files.items():
            if path.startswith(prefix):
                rest = path[len(prefix) :]
                if rest and "/" not in rest:
                    out.append(_Attr(rest, size=len(data)))
        for d in self.dirs:
            if d.startswith(prefix):
                rest = d[len(prefix) :]
                if rest and "/" not in rest:
                    out.append(_Attr(rest, is_dir=True))
        return out

    def close(self) -> None:
        pass


def _backend(fake: FakeSFTP) -> SFTPBackend:
    client = MagicMock()
    client.open_sftp.return_value = fake
    fake_paramiko = MagicMock()
    fake_paramiko.SSHClient.return_value = client
    fake_paramiko.AutoAddPolicy.return_value = object()
    with patch.dict("sys.modules", {"paramiko": fake_paramiko}):
        be = SFTPBackend(host="lab.example", port=22, username="op", password="x")
    be.sftp = fake
    be.client = client
    return be


def test_sftp_put_get_roundtrip_and_hash():
    fake = FakeSFTP()
    be = _backend(fake)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        src = tmp / "payload.bin"
        src.write_bytes(b"sftp-bytes-42")
        be.ensure_dir("staging")
        be.put(src, "staging/payload.bin")
        assert fake.files["staging/payload.bin"] == b"sftp-bytes-42"
        assert be.size("staging/payload.bin") == 13
        assert be.sha256("staging/payload.bin") == file_sha256(src)
        dest = tmp / "out.bin"
        be.get("staging/payload.bin", dest)
        assert dest.read_bytes() == b"sftp-bytes-42"
        assert be.list_files("staging") == ["payload.bin"]
    be.close()


def test_sftp_list_empty_missing_dir():
    fake = FakeSFTP()
    be = _backend(fake)
    assert be.list_files("missing") == []


def test_sftp_requires_paramiko(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def blocked(name, *args, **kwargs):
        if name == "paramiko":
            raise ImportError("no paramiko")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked)
    with pytest.raises(SystemExit, match="paramiko"):
        SFTPBackend(host="h", port=22, username="u")
