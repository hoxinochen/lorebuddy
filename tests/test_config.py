from __future__ import annotations

import json
from pathlib import Path

import pytest

from lorebuddy.config import ConfigError, load_config


def _write_config(root: Path, vault: Path, *, staging: str = "build/obsidian-staging") -> None:
    (root / "config.local.toml").write_text(
        "\n".join(
            [
                "[obsidian]",
                f"vault_root = {json.dumps(vault.as_posix())}",
                'test_publish_subdirectory = "_LoreBuddy-M1"',
                'publish_subdirectory = "LoreBuddy"',
                "",
                "[build]",
                f"staging_root = {json.dumps(staging)}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_missing_local_config_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="本地配置不存在"):
        load_config(tmp_path, environ={})


def test_config_loads_without_accessing_vault(tmp_path: Path) -> None:
    vault = tmp_path / "not-created-vault"
    _write_config(tmp_path, vault)
    config = load_config(tmp_path, environ={})
    assert config.obsidian.vault_root == vault
    assert not vault.exists()
    assert config.build.staging_root == "build/obsidian-staging"


def test_environment_overrides_vault_without_access(tmp_path: Path) -> None:
    _write_config(tmp_path, tmp_path / "configured-vault")
    override = tmp_path / "environment-vault"
    config = load_config(tmp_path, environ={"LOREBUDDY_OBSIDIAN_VAULT": str(override)})
    assert config.obsidian.vault_root == override
    assert not override.exists()


def test_path_traversal_in_relative_config_is_rejected(tmp_path: Path) -> None:
    _write_config(tmp_path, tmp_path / "vault", staging="../escape")
    with pytest.raises(ConfigError, match="无路径穿越"):
        load_config(tmp_path, environ={})


def test_windows_style_relative_path_is_rejected(tmp_path: Path) -> None:
    _write_config(tmp_path, tmp_path / "vault", staging="C:\\temp\\staging")
    with pytest.raises(ConfigError, match="跨平台路径字符"):
        load_config(tmp_path, environ={})
