"""M1-B Acquire 编排：原件核验、受控解包、保存、Inventory 与验证。"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from lorebuddy.ids import stable_id

from .chm_backend import BackendError, ChmBackend, SevenZipBackend
from .duplicates import build_duplicate_report
from .inventory import (
    enumerate_regular_files,
    mark_duplicates,
    preserve_entries,
    sha256_file,
    summarize_inventory,
)
from .report import file_digest, semantic_inventory_digest, write_json, write_jsonl


EXPECTED_CHM_SHA256 = "836eea8912cf6c068687e99db4a1b4b6b915aeb2ef8af35cfb040803184686f2"
OWNERSHIP_SCHEMA = "m1b.acquisition-workdir@0.1.0"


class AcquisitionError(RuntimeError):
    pass


def inspect_artifact(source: Path) -> dict[str, Any]:
    source = source.resolve(strict=True)
    if not source.is_file() or source.is_symlink():
        raise AcquisitionError("CHM 原件必须是普通文件且不能是符号链接")
    size, digest = sha256_file(source)
    artifact_id = stable_id("source-artifact", f"chm\x00sha256:{digest}")
    return {
        "artifact_id": artifact_id,
        "filename": source.name,
        "size": size,
        "sha256": digest,
        "digest_matches_m0": digest == EXPECTED_CHM_SHA256,
    }


def _artifact_key(artifact_id: str) -> str:
    return uuid.UUID(artifact_id.removeprefix("urn:uuid:")).hex


def _package_record(package_id: str) -> dict[str, Any]:
    return {
        "schema": "core.package-manifest@0.1.0",
        "id": package_id,
        "namespace": "lorebuddy-local",
        "slug": "m1b-restricted-acquisition",
        "title": "LoreBuddy M1-B Restricted Acquisition",
        "package_version": "0.1.0-experimental",
        "visibility": "restricted",
        "language": "zh-Hans",
        "lifecycle": {"status": "draft", "revision": 1},
        "extensions": {"m1b-acquisition": {"purpose": "acquisition", "release_status": "experimental"}},
    }


def _assert_owned_or_absent(target: Path, artifact_id: str) -> None:
    if not target.exists():
        return
    marker = target / ".lorebuddy-acquisition.json"
    if not marker.is_file():
        raise AcquisitionError(f"拒绝替换没有 LoreBuddy Ownership Marker 的目录：{target}")
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError(f"Ownership Marker 无法读取：{target}") from exc
    if payload != {"schema": OWNERSHIP_SCHEMA, "artifact_id": artifact_id}:
        raise AcquisitionError(f"Ownership Marker 与 Artifact 不一致：{target}")


def _path_map(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "schema": "m1b.source-path-map-record@0.1.0",
            "entry_id": record["id"],
            "original_path": record["original_path"],
            "normalized_path": record["extensions"]["m1b-acquisition"]["normalized_path"],
            "preserved_path": record["storage_path"],
            "path_status": record["extensions"]["m1b-acquisition"]["path_status"],
            "safety_remapped": record["extensions"]["m1b-acquisition"]["safety_remapped"],
        }
        for record in records
    ]


def run_acquisition(
    source: Path,
    output_root: Path,
    *,
    backend: ChmBackend | None = None,
    timeout: float = 300.0,
    dry_run: bool = False,
    project_root: Path | None = None,
) -> dict[str, Any]:
    inspection = inspect_artifact(source)
    if not inspection["digest_matches_m0"]:
        raise AcquisitionError(
            f"CHM SHA-256 不一致：actual={inspection['sha256']} expected={EXPECTED_CHM_SHA256}"
        )
    backend = backend or SevenZipBackend()
    backend_info = backend.info()
    artifact_id = inspection["artifact_id"]
    target = output_root.resolve() / _artifact_key(artifact_id)
    if dry_run:
        return {**inspection, "backend": asdict(backend_info), "output": str(target), "dry_run": True}
    _assert_owned_or_absent(target, artifact_id)
    output_root.mkdir(parents=True, exist_ok=True)
    temporary = output_root.resolve() / f".{_artifact_key(artifact_id)}.building"
    if temporary.exists():
        marker = temporary / ".lorebuddy-acquisition.json"
        if not marker.is_file():
            raise AcquisitionError(f"拒绝清理未知临时目录：{temporary}")
        shutil.rmtree(temporary)
    temporary.mkdir()
    write_json(temporary / ".lorebuddy-acquisition.json", {"schema": OWNERSHIP_SCHEMA, "artifact_id": artifact_id})
    staging = temporary / "staging"
    extracted = temporary / "extracted"
    artifact_bytes = temporary / "artifact"
    inventory = temporary / "inventory"
    logs = temporary / "logs"
    extracted.mkdir()
    artifact_bytes.mkdir()
    inventory.mkdir()
    logs.mkdir()
    try:
        preserved_artifact = artifact_bytes / "original.chm"
        shutil.copyfile(source.resolve(strict=True), preserved_artifact, follow_symlinks=False)
        preserved_size, preserved_digest = sha256_file(preserved_artifact)
        if preserved_size != inspection["size"] or preserved_digest != inspection["sha256"]:
            raise AcquisitionError("CHM 原件副本重读摘要不一致")
        execution = backend.extract(source.resolve(strict=True), staging, timeout)
        write_json(logs / "backend-execution.json", execution.to_log())
        candidates, rejected = enumerate_regular_files(staging)
        if not candidates:
            raise AcquisitionError("后端成功退出但没有枚举到任何普通 Entry")
        records = preserve_entries(candidates, artifact_id, extracted)
        mark_duplicates(records)
        summary = summarize_inventory(records, rejected)
        duplicates = build_duplicate_report(records)
        package_id = stable_id("package", f"m1b-restricted-acquisition\x00{artifact_id}")
        package_record = _package_record(package_id)
        artifact_record = {
            "schema": "core.source-artifact@0.1.0",
            "id": artifact_id,
            "package_id": package_id,
            "original_filename": inspection["filename"],
            "size": inspection["size"],
            "digest": f"sha256:{inspection['sha256']}",
            "format": "chm",
            "acquisition": {"source_kind": "local-file", "source_label": "user-provided-workspace-input"},
            "access_status": "restricted",
            "lifecycle": {"status": "draft", "revision": 1},
            "extensions": {"m1b-acquisition": {"backend": asdict(backend_info), "source_identity": "digest-verified", "preserved_path": "artifact/original.chm"}},
        }
        write_json(inventory / "package.json", package_record)
        write_json(inventory / "artifact.json", artifact_record)
        write_jsonl(inventory / "entries.jsonl", records)
        write_jsonl(inventory / "path-map.jsonl", _path_map(records))
        write_json(inventory / "duplicate-report.json", duplicates)
        report = {
            "schema": "m1b.acquisition-report@0.1.0",
            "artifact_id": artifact_id,
            "artifact_digest": f"sha256:{inspection['sha256']}",
            "backend": asdict(backend_info),
            "summary": summary,
            "inventory_files": {},
            "deterministic_fields": "all fields in inventory/",
            "non_deterministic_fields": ["logs/backend-execution.json:duration_seconds"],
        }
        write_json(inventory / "acquisition-report.json", report)
        report["inventory_files"] = {
            name: file_digest(inventory / name)
            for name in ("package.json", "artifact.json", "entries.jsonl", "path-map.jsonl", "duplicate-report.json")
        }
        report["semantic_inventory_sha256"] = semantic_inventory_digest(inventory)
        write_json(inventory / "acquisition-report.json", report)
        from lorebuddy.validation.source_semantics import validate_acquisition

        validation = validate_acquisition(temporary, project_root=project_root)
        write_json(inventory / "validation-report.json", validation)
        if not validation["valid"]:
            raise AcquisitionError(f"摄取语义验证失败：{validation['errors'][:3]}")
        # staging 只是中间工作目录；原始证据已逐 Entry 重读校验后保存。
        shutil.rmtree(staging)
        staging.mkdir()
        backup = target.with_name(target.name + ".previous")
        if backup.exists():
            _assert_owned_or_absent(backup, artifact_id)
            shutil.rmtree(backup)
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(temporary, target)
        except OSError:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return load_acquisition_report(target)
    except (BackendError, OSError, ValueError) as exc:
        raise AcquisitionError(str(exc)) from exc


def load_acquisition_report(artifact_dir: Path) -> dict[str, Any]:
    try:
        return json.loads((artifact_dir / "inventory" / "acquisition-report.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError(f"无法读取 Acquisition Report：{exc}") from exc
