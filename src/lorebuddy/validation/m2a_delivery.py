"""M2-A 外部 Book Catalog 交付的独立接纳校验。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


REQUIRED_MAPPING_FIELDS = {
    "entry_id",
    "source_path",
    "output_path",
    "book_id",
    "mapping_basis",
    "mapping_status",
    "source_identity_status",
}
ALLOWED_MAPPING_BASIS = {
    "source_path_top_level_root",
    "normalized_source_path_prefix",
    "explicit_exception_rule",
}
ALLOWED_PROFILE_FIELDS = {"id", "name", "description", "active_books", "fallback_books"}
PROHIBITED_CATALOG_STATUS_FIELDS = {
    "authority",
    "rights",
    "rights_status",
    "adoption_status",
    "terminal_adoption_status",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: record 必须是对象")
        records.append(value)
    return records


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def validate_m2a_delivery(delivery_dir: Path | str, m1_manifest_path: Path | str) -> dict[str, Any]:
    """验证 M2-A 候选交付，不修改外部工作区或 M1 输出。"""

    root = Path(delivery_dir)
    manifest_path = Path(m1_manifest_path)
    errors: list[dict[str, str]] = []
    summary: dict[str, int] = {"m1_entries": 0, "mapping_entries": 0, "review_entries": 0}
    try:
        delivery_manifest = _load_json(root / "m2a-delivery-manifest.json")
        m1_entries = _load_jsonl(manifest_path)
        mapping = _load_jsonl(root / "entry-to-book-mapping.m2a.jsonl")
        review_queue = _load_jsonl(root / "review-queue.jsonl")
        catalog = _load_yaml(root / "book-catalog.yaml")
        profiles_document = _load_yaml(root / "ruleset-profiles.yaml")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, yaml.YAMLError) as exc:
        return {
            "schema": "m2a.external-delivery-validation-report@0.1.0",
            "valid": False,
            "errors": [{"code": "LOAD_ERROR", "message": str(exc)}],
            "summary": summary,
        }

    summary.update(
        m1_entries=len(m1_entries), mapping_entries=len(mapping), review_entries=len(review_queue)
    )
    upstream = delivery_manifest.get("upstream_input", {})
    if not isinstance(upstream, dict):
        _error(errors, "UPSTREAM_INPUT", "upstream_input 必须是对象")
        upstream = {}
    actual_manifest_digest = _sha256(manifest_path)
    actual_artifact_ids = {entry.get("artifact_id") for entry in m1_entries}
    actual_profiles = {entry.get("publisher_profile") for entry in m1_entries}
    if upstream.get("sha256") != actual_manifest_digest:
        _error(errors, "UPSTREAM_MANIFEST_DIGEST", "声明的 M1-C3 Manifest 摘要不匹配")
    if upstream.get("entry_total_count") != len(m1_entries):
        _error(errors, "UPSTREAM_ENTRY_COUNT", "声明的 M1-C3 Entry 数量不匹配")
    if upstream.get("logical_identity") not in actual_artifact_ids or len(actual_artifact_ids) != 1:
        _error(errors, "UPSTREAM_LOGICAL_ID", "M1-C3 Logical Identity 不匹配或不唯一")
    if upstream.get("profile") not in actual_profiles or len(actual_profiles) != 1:
        _error(errors, "UPSTREAM_PROFILE", "M1-C3 Publisher Profile 不匹配或不唯一")
    if not delivery_manifest.get("generator_version"):
        _error(errors, "GENERATOR_VERSION", "缺少 generator_version")
    if not delivery_manifest.get("reproducible_command"):
        _error(errors, "REPRODUCIBLE_COMMAND", "缺少 reproducible_command")

    declared_files = delivery_manifest.get("delivery_files", [])
    if not isinstance(declared_files, list):
        _error(errors, "DELIVERY_FILES", "delivery_files 必须是数组")
        declared_files = []
    declared_paths = {item.get("relative_path") for item in declared_files if isinstance(item, dict)}
    for required in {"entry-to-book-mapping.m2a.jsonl", "review-queue.jsonl", "book-catalog.yaml", "ruleset-profiles.yaml"}:
        if required not in declared_paths:
            _error(errors, "DELIVERY_FILE_MISSING", f"未登记必须交付文件：{required}")
    for item in declared_files:
        if not isinstance(item, dict):
            _error(errors, "DELIVERY_FILE_RECORD", "delivery_files 含非对象记录")
            continue
        relative_path = item.get("relative_path")
        if not isinstance(relative_path, str) or not relative_path or Path(relative_path).is_absolute():
            _error(errors, "DELIVERY_FILE_PATH", "交付文件路径非法")
            continue
        candidate = root / relative_path
        if not candidate.is_file():
            _error(errors, "DELIVERY_FILE_NOT_FOUND", relative_path)
            continue
        if item.get("sha256") != _sha256(candidate):
            _error(errors, "DELIVERY_FILE_DIGEST", relative_path)
        if item.get("file_size_bytes") != candidate.stat().st_size:
            _error(errors, "DELIVERY_FILE_SIZE", relative_path)
        if candidate.suffix == ".jsonl" and item.get("record_count") != len(_load_jsonl(candidate)):
            _error(errors, "DELIVERY_FILE_COUNT", relative_path)

    m1_by_id = {entry.get("entry_id"): entry for entry in m1_entries}
    if len(m1_by_id) != len(m1_entries):
        _error(errors, "M1_DUPLICATE_ENTRY_ID", "M1-C3 Manifest 的 entry_id 不唯一")
    mapping_ids = [entry.get("entry_id") for entry in mapping]
    review_ids = [entry.get("entry_id") for entry in review_queue]
    if len(set(mapping_ids)) != len(mapping_ids):
        _error(errors, "MAPPING_DUPLICATE_ENTRY_ID", "映射表中有重复 entry_id")
    if len(set(review_ids)) != len(review_ids):
        _error(errors, "REVIEW_DUPLICATE_ENTRY_ID", "Review Queue 中有重复 entry_id")
    if set(mapping_ids) & set(review_ids):
        _error(errors, "ENTRY_SET_NOT_DISJOINT", "映射表与 Review Queue 不互斥")
    if set(mapping_ids) | set(review_ids) != set(m1_by_id):
        _error(errors, "ENTRY_SET_NOT_CLOSED", "映射表与 Review Queue 未与 M1-C3 Manifest 闭合")
    for number, entry in enumerate(mapping, 1):
        missing = REQUIRED_MAPPING_FIELDS - set(entry)
        if missing:
            _error(errors, "MAPPING_REQUIRED_FIELD", f"mapping:{number} 缺少 {sorted(missing)}")
            continue
        m1_entry = m1_by_id.get(entry["entry_id"])
        if not m1_entry:
            continue
        for field in ("source_path", "output_path"):
            if entry[field] != m1_entry.get(field):
                _error(errors, "MAPPING_PATH_MISMATCH", f"mapping:{number}:{field}")
        if entry["mapping_basis"] not in ALLOWED_MAPPING_BASIS:
            _error(errors, "MAPPING_BASIS", f"mapping:{number}:{entry['mapping_basis']}")
        if entry["mapping_status"] != "deterministic":
            _error(errors, "MAPPING_STATUS", f"mapping:{number}:{entry['mapping_status']}")
        if entry["source_identity_status"] not in {"claimed", "unknown", "inferred"}:
            _error(errors, "SOURCE_IDENTITY_STATUS", f"mapping:{number}:{entry['source_identity_status']}")
    for number, entry in enumerate(review_queue, 1):
        m1_entry = m1_by_id.get(entry.get("entry_id"))
        if not m1_entry:
            continue
        for field in ("source_path", "output_path"):
            if entry.get(field) != m1_entry.get(field):
                _error(errors, "REVIEW_PATH_MISMATCH", f"review:{number}:{field}")

    if not isinstance(catalog, list):
        _error(errors, "CATALOG_FORMAT", "book-catalog.yaml 根必须是书籍数组")
        catalog = []
    catalog_ids: set[str] = set()
    for number, book in enumerate(catalog, 1):
        if not isinstance(book, dict) or not isinstance(book.get("id"), str):
            _error(errors, "CATALOG_RECORD", f"book:{number} 缺少 id")
            continue
        if book["id"] in catalog_ids:
            _error(errors, "CATALOG_DUPLICATE_BOOK_ID", book["id"])
        catalog_ids.add(book["id"])
        for field in PROHIBITED_CATALOG_STATUS_FIELDS & set(book):
            _error(errors, "CATALOG_UNREVIEWED_STATUS", f"book:{number}:{field}")
    unknown_books = {entry.get("book_id") for entry in mapping} - catalog_ids
    if unknown_books:
        _error(errors, "MAPPING_UNKNOWN_BOOK", str(sorted(unknown_books)))

    if not isinstance(profiles_document, dict) or not isinstance(profiles_document.get("profiles"), list):
        _error(errors, "PROFILE_FORMAT", "ruleset-profiles.yaml 必须含 profiles 数组")
        profiles: list[Any] = []
    else:
        profiles = profiles_document["profiles"]
    profile_ids: set[str] = set()
    for number, profile in enumerate(profiles, 1):
        if not isinstance(profile, dict):
            _error(errors, "PROFILE_RECORD", f"profile:{number} 必须是对象")
            continue
        if not isinstance(profile.get("id"), str):
            _error(errors, "PROFILE_ID", f"profile:{number} 缺少 id")
        elif profile["id"] in profile_ids:
            _error(errors, "PROFILE_DUPLICATE_ID", profile["id"])
        else:
            profile_ids.add(profile["id"])
        extras = set(profile) - ALLOWED_PROFILE_FIELDS
        if extras:
            _error(errors, "PROFILE_SEMANTIC_FIELD", f"profile:{number}:{sorted(extras)}")
        active = profile.get("active_books")
        fallback = profile.get("fallback_books")
        if not isinstance(active, list) or not isinstance(fallback, list):
            _error(errors, "PROFILE_BOOK_LIST", f"profile:{number}")
            continue
        if set(active) & set(fallback):
            _error(errors, "PROFILE_BOOK_OVERLAP", f"profile:{number}")
        unknown = (set(active) | set(fallback)) - catalog_ids
        if unknown:
            _error(errors, "PROFILE_UNKNOWN_BOOK", f"profile:{number}:{sorted(unknown)}")

    return {
        "schema": "m2a.external-delivery-validation-report@0.1.0",
        "valid": not errors,
        "errors": errors,
        "summary": summary,
    }
