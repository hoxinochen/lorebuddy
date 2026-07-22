"""M1-B Source 层跨 Record 与原始字节语义校验。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lorebuddy.acquisition.inventory import enumerate_regular_files, sha256_file
from lorebuddy.acquisition.report import file_digest
from lorebuddy.registry import SchemaRegistry
from lorebuddy.validation.schema_validator import SchemaValidator


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path.name}:{number}: Record 必须是对象")
            records.append(value)
    return records


def validate_acquisition(artifact_dir: Path, *, project_root: Path | None = None) -> dict[str, Any]:
    root = artifact_dir.resolve(strict=True)
    project = (project_root or Path.cwd()).resolve()
    errors: list[dict[str, str]] = []
    try:
        registry = SchemaRegistry.from_project_root(project)
        validator = SchemaValidator(registry)
        package = _load_json(root / "inventory" / "package.json")
        artifact = _load_json(root / "inventory" / "artifact.json")
        entries = _load_jsonl(root / "inventory" / "entries.jsonl")
        path_maps = _load_jsonl(root / "inventory" / "path-map.jsonl")
        duplicate_report = _load_json(root / "inventory" / "duplicate-report.json")
        acquisition_report = _load_json(root / "inventory" / "acquisition-report.json")
        ownership = _load_json(root / ".lorebuddy-acquisition.json")
        backend_log = _load_json(root / "logs" / "backend-execution.json")
    except Exception as exc:
        return {
            "schema": "m1b.acquisition-validation-report@0.1.0",
            "valid": False,
            "errors": [{"code": "LOAD_ERROR", "message": str(exc)}],
            "summary": {"artifact_count": 0, "entry_count": 0, "saved_file_count": 0},
        }
    for record, schema_id, label in (
        (package, "core.package-manifest@0.1.0", "package"),
        (artifact, "core.source-artifact@0.1.0", "artifact"),
        (duplicate_report, "m1b.duplicate-report@0.1.0", "duplicate-report"),
        (acquisition_report, "m1b.acquisition-report@0.1.0", "acquisition-report"),
        (ownership, "m1b.acquisition-workdir@0.1.0", "ownership"),
        (backend_log, "m1b.backend-execution@0.1.0", "backend-log"),
    ):
        result = validator.validate_data(record, schema_id)
        for issue in result.errors:
            errors.append({"code": "SCHEMA", "message": f"{label}{issue.path}: {issue.message}"})
    artifact_path = root / artifact.get("extensions", {}).get("m1b-acquisition", {}).get("preserved_path", "")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        errors.append({"code": "MISSING_ARTIFACT_BYTES", "message": str(artifact_path)})
    else:
        artifact_size, artifact_digest = sha256_file(artifact_path)
        if artifact_size != artifact.get("size"):
            errors.append({"code": "ARTIFACT_SIZE_MISMATCH", "message": str(artifact_path)})
        if f"sha256:{artifact_digest}" != artifact.get("digest"):
            errors.append({"code": "ARTIFACT_DIGEST_MISMATCH", "message": str(artifact_path)})
    entry_ids: set[str] = set()
    storage_paths: set[str] = set()
    normalized: dict[str, list[str]] = {}
    for entry in entries:
        result = validator.validate_data(entry, "core.source-entry@0.1.0")
        for issue in result.errors:
            errors.append({"code": "SCHEMA", "message": f"entry{issue.path}: {issue.message}"})
        if entry.get("id") in entry_ids:
            errors.append({"code": "DUPLICATE_ENTRY_ID", "message": str(entry.get("id"))})
        entry_ids.add(entry.get("id"))
        if entry.get("artifact_id") != artifact.get("id"):
            errors.append({"code": "ARTIFACT_REFERENCE", "message": str(entry.get("id"))})
        storage = entry.get("storage_path", "")
        if storage in storage_paths:
            errors.append({"code": "DUPLICATE_STORAGE_PATH", "message": storage})
        storage_paths.add(storage)
        ext = entry.get("extensions", {}).get("m1b-acquisition", {})
        normalized.setdefault(ext.get("normalized_path", ""), []).append(entry.get("id", ""))
        saved = (root / "extracted" / storage).resolve()
        if not saved.is_relative_to((root / "extracted").resolve()):
            errors.append({"code": "PATH_ESCAPE", "message": storage})
            continue
        if not saved.is_file() or saved.is_symlink():
            errors.append({"code": "MISSING_SAVED_ENTRY", "message": storage})
            continue
        size, digest = sha256_file(saved)
        if size != entry.get("size"):
            errors.append({"code": "SIZE_MISMATCH", "message": storage})
        if f"sha256:{digest}" != entry.get("digest"):
            errors.append({"code": "DIGEST_MISMATCH", "message": storage})
    for value, ids in normalized.items():
        if len(ids) > 1:
            related = [entry for entry in entries if entry["id"] in ids]
            if not all(entry["extensions"]["m1b-acquisition"].get("conflict_kind") for entry in related):
                errors.append({"code": "UNRECORDED_NORMALIZED_COLLISION", "message": value})
    path_map_by_id: dict[str, dict[str, Any]] = {}
    for mapping in path_maps:
        result = validator.validate_data(mapping, "m1b.source-path-map-record@0.1.0")
        for issue in result.errors:
            errors.append({"code": "SCHEMA", "message": f"path-map{issue.path}: {issue.message}"})
        entry_id = mapping.get("entry_id", "")
        if entry_id in path_map_by_id:
            errors.append({"code": "DUPLICATE_PATH_MAP", "message": entry_id})
        path_map_by_id[entry_id] = mapping
    if set(path_map_by_id) != entry_ids:
        errors.append({"code": "PATH_MAP_CLOSURE", "message": "Path Map 与 Entry ID 集合不一致"})
    for entry in entries:
        mapping = path_map_by_id.get(entry["id"])
        if mapping is None:
            continue
        extension = entry["extensions"]["m1b-acquisition"]
        expected = {
            "schema": "m1b.source-path-map-record@0.1.0",
            "entry_id": entry["id"],
            "original_path": entry["original_path"],
            "normalized_path": extension["normalized_path"],
            "preserved_path": entry["storage_path"],
            "path_status": extension["path_status"],
            "safety_remapped": extension["safety_remapped"],
        }
        if mapping != expected:
            errors.append({"code": "PATH_MAP_PROJECTION", "message": entry["id"]})
    actual, rejected = enumerate_regular_files(root / "extracted")
    actual_storage = {item.original_path for item in actual}
    if actual_storage != storage_paths:
        errors.append({"code": "INVENTORY_CLOSURE", "message": f"actual={len(actual_storage)} inventory={len(storage_paths)}"})
    if rejected:
        errors.append({"code": "NON_REGULAR_PRESERVED", "message": str(rejected)})
    summary = acquisition_report.get("summary", {})
    if summary.get("entry_count") != len(entries):
        errors.append({"code": "SUMMARY_COUNT", "message": "entry_count 不一致"})
    if summary.get("total_bytes") != sum(entry.get("size", 0) for entry in entries):
        errors.append({"code": "SUMMARY_BYTES", "message": "total_bytes 不一致"})
    expected_inventory_files = acquisition_report.get("inventory_files", {})
    for name, expected_digest in expected_inventory_files.items():
        candidate = root / "inventory" / name
        if not candidate.is_file() or file_digest(candidate) != expected_digest:
            errors.append({"code": "INVENTORY_FILE_DIGEST", "message": name})
    duplicate_summary = duplicate_report.get("summary", {})
    if duplicate_summary.get("byte_identical_groups") != len(duplicate_report.get("byte_identical_groups", [])):
        errors.append({"code": "DUPLICATE_SUMMARY", "message": "byte_identical_groups 不一致"})
    if duplicate_summary.get("same_name_different_content_groups") != len(duplicate_report.get("same_name_different_content_groups", [])):
        errors.append({"code": "DUPLICATE_SUMMARY", "message": "same_name_different_content_groups 不一致"})
    if duplicate_summary.get("path_conflict_entries") != sum(len(ids) for ids in duplicate_report.get("path_conflicts", {}).values()):
        errors.append({"code": "DUPLICATE_SUMMARY", "message": "path_conflict_entries 不一致"})
    report = {
        "schema": "m1b.acquisition-validation-report@0.1.0",
        "valid": not errors,
        "errors": errors,
        "summary": {"artifact_count": 1, "entry_count": len(entries), "saved_file_count": len(actual_storage)},
    }
    self_result = validator.validate_data(report, "m1b.acquisition-validation-report@0.1.0")
    if not self_result.valid:
        report["valid"] = False
        report["errors"].extend(
            {"code": "VALIDATION_REPORT_SCHEMA", "message": f"{issue.path}: {issue.message}"}
            for issue in self_result.errors
        )
    return report
