import subprocess
from pathlib import Path

import pytest

from lorebuddy.acquisition.chm_backend import (
    BackendError,
    BackendUnavailableError,
    SevenZipBackend,
)


def test_missing_backend_has_clear_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(BackendUnavailableError, match="未找到"):
        SevenZipBackend()


def test_backend_timeout_is_reported(tmp_path: Path, monkeypatch):
    executable = tmp_path / "7zz"
    executable.write_bytes(b"tool")
    source = tmp_path / "source.chm"
    source.write_bytes(b"chm")
    backend = SevenZipBackend(str(executable))
    monkeypatch.setattr(backend, "info", lambda: None)
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs.get("timeout"))
    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(BackendError, match="超时"):
        backend.extract(source, tmp_path / "build" / "staging", 0.01)


def test_backend_nonzero_exit_is_reported(tmp_path: Path, monkeypatch):
    executable = tmp_path / "7zz"
    executable.write_bytes(b"tool")
    source = tmp_path / "source.chm"
    source.write_bytes(b"chm")
    backend = SevenZipBackend(str(executable))
    monkeypatch.setattr(backend, "info", lambda: None)
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 2, "", "bad"))
    with pytest.raises(BackendError, match="exit=2"):
        backend.extract(source, tmp_path / "build" / "staging", 1)
