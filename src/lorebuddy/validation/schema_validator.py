"""JSON / YAML 文档的 Schema 验证。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from lorebuddy.registry import RegistryError, SchemaRegistry

from .result import ValidationIssue, ValidationResult


class DocumentLoadError(ValueError):
    """输入文档不是可接受的 JSON / YAML。"""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise DocumentLoadError(f"重复 YAML Key：{key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DocumentLoadError(f"重复 JSON Key：{key}")
        result[key] = value
    return result


def load_document(path: Path | str) -> Any:
    document_path = Path(path)
    if document_path.suffix.lower() not in {".json", ".yaml", ".yml"}:
        raise DocumentLoadError(f"不支持的文档格式：{document_path.suffix}")
    try:
        text = document_path.read_text(encoding="utf-8")
        if document_path.suffix.lower() == ".json":
            return json.loads(text, object_pairs_hook=_json_object)
        return yaml.load(text, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise DocumentLoadError(f"文档无法读取：{document_path}: {exc}") from exc


def _pointer(parts: list[Any]) -> str:
    if not parts:
        return "/"
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


class SchemaValidator:
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry

    def validate_data(
        self, data: Any, schema_id: str, *, file: str | None = None
    ) -> ValidationResult:
        try:
            schema = self.registry.load_schema(schema_id)
        except RegistryError as exc:
            issue = ValidationIssue(path="/", code="UNKNOWN_SCHEMA", message=str(exc))
            return ValidationResult(False, schema_id, (issue,), file, "Schema 无法解析")

        validator = Draft202012Validator(schema)
        raw_errors = sorted(
            validator.iter_errors(data),
            key=lambda error: (list(error.absolute_path), error.validator or ""),
        )
        errors = tuple(
            ValidationIssue(
                path=_pointer(list(error.absolute_path)),
                code=f"SCHEMA_{str(error.validator).upper()}",
                message=error.message,
                validator=str(error.validator) if error.validator else None,
            )
            for error in raw_errors
        )
        valid = not errors
        summary = "验证通过" if valid else f"验证失败：{len(errors)} 个错误"
        return ValidationResult(valid, schema_id, errors, file, summary)

    def validate_file(self, schema_id: str, path: Path | str) -> ValidationResult:
        document_path = Path(path)
        try:
            data = load_document(document_path)
        except DocumentLoadError as exc:
            issue = ValidationIssue(path="/", code="DOCUMENT_LOAD_ERROR", message=str(exc))
            return ValidationResult(
                False, schema_id, (issue,), str(document_path), "文档加载失败"
            )
        return self.validate_data(data, schema_id, file=str(document_path))
