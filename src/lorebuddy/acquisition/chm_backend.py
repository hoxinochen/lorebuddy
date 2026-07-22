"""受控 CHM 解包后端；M1-B 只支持 7-Zip，不提供插件发现机制。"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol


class BackendError(RuntimeError):
    """CHM 后端执行失败。"""


class BackendUnavailableError(BackendError):
    """没有可用的 CHM 后端。"""


@dataclass(frozen=True, slots=True)
class BackendInfo:
    name: str
    version: str
    executable_name: str
    executable_sha256: str


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    backend: BackendInfo
    argv: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float

    def to_log(self) -> dict[str, object]:
        payload = asdict(self)
        payload["backend"] = asdict(self.backend)
        payload["schema"] = "m1b.backend-execution@0.1.0"
        return payload


class ChmBackend(Protocol):
    def info(self) -> BackendInfo: ...

    def extract(self, source: Path, output: Path, timeout: float) -> ExecutionResult: ...


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SevenZipBackend:
    """以参数列表调用 7zz/7z，并独立交给 Inventory 层枚举结果。"""

    def __init__(self, executable: str | None = None) -> None:
        selected = executable or shutil.which("7zz") or shutil.which("7z")
        if not selected:
            raise BackendUnavailableError(
                "未找到 7zz 或 7z。请安装官方 7-Zip CLI 或 Homebrew sevenzip；"
                "LoreBuddy 不会自动安装系统软件。"
            )
        self.executable = Path(selected).resolve()
        if not self.executable.is_file():
            raise BackendUnavailableError(f"7-Zip 可执行文件不存在：{selected}")
        self._info: BackendInfo | None = None

    def info(self) -> BackendInfo:
        if self._info is None:
            try:
                result = subprocess.run(
                    [str(self.executable), "i"],
                    shell=False,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise BackendUnavailableError(f"无法读取 7-Zip 版本：{exc}") from exc
            text = (result.stdout or result.stderr).strip().splitlines()
            version = next((line.strip() for line in text if "7-Zip" in line), "unknown")
            self._info = BackendInfo(
                name="7zip",
                version=version,
                executable_name=self.executable.name,
                executable_sha256=_file_sha256(self.executable),
            )
        return self._info

    def extract(self, source: Path, output: Path, timeout: float) -> ExecutionResult:
        source = source.resolve(strict=True)
        output = output.resolve()
        if output == source.parent or output.is_relative_to(source.parent) and output.parent == source.parent:
            raise BackendError("禁止在 CHM 原件所在目录直接解包")
        output.mkdir(parents=True, exist_ok=False)
        argv = (str(self.executable), "x", "-y", f"-o{output}", str(source))
        started = time.monotonic()
        try:
            result = subprocess.run(
                list(argv),
                shell=False,
                check=False,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise BackendError(f"7-Zip 解包超时（{timeout:g}s）") from exc
        except OSError as exc:
            raise BackendError(f"7-Zip 无法启动：{exc}") from exc
        execution = ExecutionResult(
            backend=self.info(),
            argv=argv,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_seconds=time.monotonic() - started,
        )
        if result.returncode != 0:
            raise BackendError(
                f"7-Zip 解包失败，exit={result.returncode}：{result.stderr.strip()}"
            )
        return execution
