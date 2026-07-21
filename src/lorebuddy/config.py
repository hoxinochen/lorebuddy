"""设备本地配置读取；M1-A 不访问配置指向的 Vault。"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping


class ConfigError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ObsidianConfig:
    vault_root: Path
    test_publish_subdirectory: str
    publish_subdirectory: str


@dataclass(frozen=True, slots=True)
class BuildConfig:
    staging_root: str


@dataclass(frozen=True, slots=True)
class AppConfig:
    obsidian: ObsidianConfig
    build: BuildConfig


def _safe_relative(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{field} 必须是非空相对路径")
    if "\\" in value or ":" in value or "\x00" in value:
        raise ConfigError(f"{field} 包含不允许的跨平台路径字符")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ConfigError(f"{field} 必须是无路径穿越的相对路径")
    return path.as_posix()


def load_config(
    project_root: Path | str,
    *,
    environ: Mapping[str, str] | None = None,
    config_path: Path | str | None = None,
) -> AppConfig:
    root = Path(project_root)
    path = Path(config_path) if config_path else root / "config.local.toml"
    if not path.is_file():
        raise ConfigError(f"本地配置不存在：{path.name}")
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"本地配置无法读取：{exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigError("本地配置顶层必须是 TOML Table")
    obsidian = payload.get("obsidian")
    build = payload.get("build")
    if not isinstance(obsidian, dict) or not isinstance(build, dict):
        raise ConfigError("配置必须包含 [obsidian] 与 [build]")

    env = os.environ if environ is None else environ
    vault_value = env.get("LOREBUDDY_OBSIDIAN_VAULT", obsidian.get("vault_root"))
    if not isinstance(vault_value, str) or not vault_value:
        raise ConfigError("obsidian.vault_root 未配置")
    vault_root = Path(vault_value).expanduser()
    if not vault_root.is_absolute():
        raise ConfigError("obsidian.vault_root 必须是绝对路径")

    return AppConfig(
        obsidian=ObsidianConfig(
            vault_root=vault_root,
            test_publish_subdirectory=_safe_relative(
                obsidian.get("test_publish_subdirectory"),
                "obsidian.test_publish_subdirectory",
            ),
            publish_subdirectory=_safe_relative(
                obsidian.get("publish_subdirectory"), "obsidian.publish_subdirectory"
            ),
        ),
        build=BuildConfig(
            staging_root=_safe_relative(build.get("staging_root"), "build.staging_root")
        ),
    )
