from __future__ import annotations

from pathlib import Path

import pytest

from lorebuddy.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_schema_list_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["schemas", "list"], project_root=PROJECT_ROOT) == 0
    output = capsys.readouterr().out
    assert output.count("core.") == 8


def test_schema_validate_exit_codes(capsys: pytest.CaptureFixture[str]) -> None:
    valid = PROJECT_ROOT / "fixtures" / "m1a" / "valid" / "entry.json"
    invalid = PROJECT_ROOT / "fixtures" / "m1a" / "invalid" / "entry.json"
    schema_id = "core.source-entry@0.1.0"
    assert main(["schemas", "validate", schema_id, str(valid)], project_root=PROJECT_ROOT) == 0
    assert main(["schemas", "validate", schema_id, str(invalid)], project_root=PROJECT_ROOT) == 1
    assert '"path": "/storage_path"' in capsys.readouterr().out


def test_fixture_validate_command(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["fixtures", "validate"], project_root=PROJECT_ROOT) == 0
    assert "16 个" in capsys.readouterr().out


def test_config_check_does_not_access_vault(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    vault = tmp_path / "not-created-vault"
    (tmp_path / "config.local.toml").write_text(
        "\n".join(
            [
                "[obsidian]",
                f'vault_root = "{vault.as_posix()}"',
                'test_publish_subdirectory = "_LoreBuddy-M1"',
                'publish_subdirectory = "LoreBuddy"',
                "[build]",
                'staging_root = "build/obsidian-staging"',
            ]
        ),
        encoding="utf-8",
    )
    assert main(["config", "check"], project_root=tmp_path) == 0
    output = capsys.readouterr().out
    assert "未访问" in output
    assert str(vault) not in output
    assert not vault.exists()


@pytest.mark.parametrize("command", ["ingest", "unpack", "convert", "publish"])
def test_unimplemented_commands_do_not_exist(command: str) -> None:
    with pytest.raises(SystemExit) as exc:
        main([command], project_root=PROJECT_ROOT)
    assert exc.value.code == 2
