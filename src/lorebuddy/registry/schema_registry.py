"""版本化 JSON Schema Registry。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


ALLOWED_STATUSES = frozenset({"active", "experimental", "deprecated"})
REGISTRY_VERSION = "0.1.0"
REGISTRY_PROFILE = "m1-profile@0.1.0"


class RegistryError(RuntimeError):
    """Registry 或其引用的 Schema 不完整、不一致。"""


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    schema_id: str
    version: str
    path: str
    status: str
    profile: str
    description: str


class SchemaRegistry:
    """加载并验证一个机器可读 Schema Registry。"""

    def __init__(self, registry_path: Path | str):
        self.registry_path = Path(registry_path).resolve()
        self.schema_root = self.registry_path.parent
        self._entries = self._load_registry()
        self._schemas: dict[str, dict[str, Any]] = {}
        self._verify_all_entries()

    @classmethod
    def from_project_root(cls, project_root: Path | str) -> "SchemaRegistry":
        return cls(Path(project_root) / "schemas" / "registry.yaml")

    def _load_registry(self) -> dict[str, RegistryEntry]:
        if not self.registry_path.is_file():
            raise RegistryError(f"Registry 文件不存在：{self.registry_path}")
        try:
            payload = yaml.safe_load(self.registry_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise RegistryError(f"Registry 无法读取：{exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("schemas"), list):
            raise RegistryError("Registry 顶层必须包含 schemas 数组")
        expected_top_level = {"registry_version", "profile", "schemas"}
        if set(payload) != expected_top_level:
            raise RegistryError(
                f"Registry 顶层字段错误：expected={sorted(expected_top_level)}, "
                f"actual={sorted(payload)}"
            )
        if payload["registry_version"] != REGISTRY_VERSION:
            raise RegistryError(f"不支持的 Registry 版本：{payload['registry_version']}")
        if payload["profile"] != REGISTRY_PROFILE:
            raise RegistryError(f"不支持的 Registry Profile：{payload['profile']}")

        entries: dict[str, RegistryEntry] = {}
        required = {"schema_id", "version", "path", "status", "profile", "description"}
        for index, raw in enumerate(payload["schemas"]):
            if not isinstance(raw, dict):
                raise RegistryError(f"Registry schemas[{index}] 必须是对象")
            missing = required - raw.keys()
            unknown = raw.keys() - required
            if missing or unknown:
                raise RegistryError(
                    f"Registry schemas[{index}] 字段错误：missing={sorted(missing)}, "
                    f"unknown={sorted(unknown)}"
                )
            entry = RegistryEntry(**raw)
            if entry.schema_id in entries:
                raise RegistryError(f"重复 Schema ID：{entry.schema_id}")
            if entry.status not in ALLOWED_STATUSES:
                raise RegistryError(f"不支持的 Registry 状态：{entry.status}")
            if entry.profile != payload["profile"]:
                raise RegistryError(f"Schema Profile 与 Registry 不一致：{entry.schema_id}")
            entries[entry.schema_id] = entry
        if not entries:
            raise RegistryError("Registry 至少需要一个 Schema")
        return entries

    def _schema_path(self, entry: RegistryEntry) -> Path:
        candidate = (self.schema_root / entry.path).resolve()
        if not candidate.is_relative_to(self.schema_root):
            raise RegistryError(f"Schema 路径逃逸 Registry 目录：{entry.path}")
        if not candidate.is_file():
            raise RegistryError(f"Schema 文件不存在：{entry.path}")
        return candidate

    def _verify_all_entries(self) -> None:
        for schema_id in self._entries:
            self.load_schema(schema_id)

    def list_entries(self) -> tuple[RegistryEntry, ...]:
        return tuple(self._entries[key] for key in sorted(self._entries))

    def get_entry(self, schema_id: str) -> RegistryEntry:
        try:
            return self._entries[schema_id]
        except KeyError as exc:
            raise RegistryError(f"未知 Schema ID：{schema_id}") from exc

    def load_schema(self, schema_id: str) -> dict[str, Any]:
        if schema_id in self._schemas:
            return self._schemas[schema_id]
        entry = self.get_entry(schema_id)
        path = self._schema_path(entry)
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RegistryError(f"Schema 无法读取：{entry.path}: {exc}") from exc
        if not isinstance(schema, dict):
            raise RegistryError(f"Schema 顶层必须是对象：{entry.path}")
        if schema.get("$id") != entry.schema_id:
            raise RegistryError(
                f"Schema ID 不一致：registry={entry.schema_id}, file={schema.get('$id')}"
            )
        if schema.get("x-lorebuddy-version") != entry.version:
            raise RegistryError(f"Schema 版本不一致：{entry.schema_id}")
        if schema.get("x-lorebuddy-profile") != entry.profile:
            raise RegistryError(f"Schema Profile 不一致：{entry.schema_id}")
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise RegistryError(f"非法 JSON Schema：{entry.schema_id}: {exc.message}") from exc
        self._schemas[schema_id] = schema
        return schema
