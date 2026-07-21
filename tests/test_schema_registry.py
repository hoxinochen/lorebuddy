from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lorebuddy.registry import RegistryError, SchemaRegistry


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_registry_loads_all_m1a_schemas() -> None:
    registry = SchemaRegistry.from_project_root(PROJECT_ROOT)
    entries = registry.list_entries()
    assert len(entries) == 8
    assert {entry.status for entry in entries} == {"active", "experimental"}
    assert all(entry.profile == "m1-profile@0.1.0" for entry in entries)


def test_registry_rejects_duplicate_schema_id(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yaml"
    entry = {
        "schema_id": "core.duplicate@0.1.0",
        "version": "0.1.0",
        "path": "duplicate.schema.json",
        "status": "active",
        "profile": "m1-profile@0.1.0",
        "description": "duplicate",
    }
    registry_path.write_text(
        yaml.safe_dump(
            {
                "registry_version": "0.1.0",
                "profile": "m1-profile@0.1.0",
                "schemas": [entry, entry],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    with pytest.raises(RegistryError, match="重复 Schema ID"):
        SchemaRegistry(registry_path)


def test_registry_rejects_missing_schema_file(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yaml"
    payload = {
        "registry_version": "0.1.0",
        "profile": "m1-profile@0.1.0",
        "schemas": [
            {
                "schema_id": "core.missing@0.1.0",
                "version": "0.1.0",
                "path": "missing.schema.json",
                "status": "active",
                "profile": "m1-profile@0.1.0",
                "description": "missing",
            }
        ]
    }
    registry_path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with pytest.raises(RegistryError, match="Schema 文件不存在"):
        SchemaRegistry(registry_path)


def test_registry_rejects_unknown_top_level_field(tmp_path: Path) -> None:
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "registry_version": "0.1.0",
                "profile": "m1-profile@0.1.0",
                "schemas": [],
                "typo": True,
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RegistryError, match="顶层字段错误"):
        SchemaRegistry(registry_path)
