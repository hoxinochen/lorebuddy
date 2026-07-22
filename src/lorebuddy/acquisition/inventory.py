"""独立枚举解包结果并保存原始 Entry 字节。"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lorebuddy.ids import stable_id

from .media_types import detect_encoding, detect_media_type
from .paths import plan_paths


class InventoryError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EnumeratedEntry:
    original_path: str
    source_path: Path


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def enumerate_regular_files(root: Path) -> tuple[list[EnumeratedEntry], list[dict[str, str]]]:
    root = root.resolve(strict=True)
    entries: list[EnumeratedEntry] = []
    rejected: list[dict[str, str]] = []
    stack = [root]
    while stack:
        directory = stack.pop()
        with os.scandir(directory) as iterator:
            children = sorted(iterator, key=lambda item: os.fsencode(item.name))
        for child in reversed(children):
            path = Path(child.path)
            relative = path.relative_to(root).as_posix()
            mode = child.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                rejected.append({"path": relative, "reason": "symbolic-link"})
            elif stat.S_ISDIR(mode):
                stack.append(path)
            elif stat.S_ISREG(mode):
                entries.append(EnumeratedEntry(relative, path))
            else:
                rejected.append({"path": relative, "reason": "non-regular-file"})
    entries.sort(key=lambda item: item.original_path.encode("utf-8", "surrogatepass"))
    rejected.sort(key=lambda item: (item["path"], item["reason"]))
    return entries, rejected


def preserve_entries(
    candidates: list[EnumeratedEntry], artifact_id: str, destination_root: Path
) -> list[dict[str, Any]]:
    decisions = plan_paths([candidate.original_path for candidate in candidates])
    records: list[dict[str, Any]] = []
    for candidate, decision in zip(candidates, decisions, strict=True):
        source_mode = candidate.source_path.lstat().st_mode
        if not stat.S_ISREG(source_mode):
            raise InventoryError(f"拒绝非普通文件：{candidate.original_path}")
        destination = (destination_root / decision.preserved_path).resolve()
        if not destination.is_relative_to(destination_root.resolve()):
            raise InventoryError(f"保存路径逃逸：{decision.preserved_path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise InventoryError(f"保存路径发生未规划覆盖：{decision.preserved_path}")
        shutil.copyfile(candidate.source_path, destination, follow_symlinks=False)
        source_size, source_digest = sha256_file(candidate.source_path)
        saved_size, saved_digest = sha256_file(destination)
        if (source_size, source_digest) != (saved_size, saved_digest):
            raise InventoryError(f"原始字节保存校验失败：{candidate.original_path}")
        with candidate.source_path.open("rb") as stream:
            prefix = stream.read(65536)
        media = detect_media_type(candidate.original_path, prefix)
        encoding = detect_encoding(prefix, media.detected_media_type)
        identity_path = decision.normalized_path
        if decision.conflict_kind:
            identity_path += "\x00" + decision.preserved_path
        entry_id = stable_id("source-entry", f"{artifact_id}\x00m1b-v1\x00{identity_path}")
        charset_status = "not-applicable" if encoding.confidence == "not-applicable" else (
            "mismatch" if encoding.conflict else "unknown"
        )
        extension = {
            "entry_kind": "regular-file",
            "normalized_path": decision.normalized_path,
            "preserved_path": decision.preserved_path,
            "path_status": decision.path_status,
            "safety_remapped": decision.safety_remapped,
            "conflict_kind": decision.conflict_kind,
            "declared_media_type": media.declared_media_type,
            "detected_media_type": media.detected_media_type,
            "media_type_confidence": media.confidence,
            "declared_encoding": encoding.declared_encoding,
            "detected_encoding_candidate": encoding.detected_encoding_candidate,
            "encoding_confidence": encoding.confidence,
            "encoding_conflict": encoding.conflict,
            "encoding_evidence": list(encoding.evidence),
            "duplicate_status": "pending",
            "source_order": None,
            "warnings": list(decision.warnings),
            "errors": [],
        }
        records.append({
            "schema": "core.source-entry@0.1.0",
            "id": entry_id,
            "artifact_id": artifact_id,
            "original_path": candidate.original_path,
            "storage_path": decision.preserved_path,
            "size": saved_size,
            "digest": f"sha256:{saved_digest}",
            "media_type": media.detected_media_type,
            "charset": {
                "declared": encoding.declared_encoding,
                "detected": encoding.detected_encoding_candidate,
                "status": charset_status,
            },
            "extraction_status": "extracted",
            "lifecycle": {"status": "draft", "revision": 1},
            "extensions": {"m1b-acquisition": extension},
        })
    records.sort(key=lambda item: item["storage_path"].encode("utf-8"))
    return records


def mark_duplicates(records: list[dict[str, Any]]) -> None:
    digests = Counter(record["digest"] for record in records)
    names = Counter(Path(record["original_path"]).name.casefold() for record in records)
    for record in records:
        extension = record["extensions"]["m1b-acquisition"]
        flags: list[str] = []
        if digests[record["digest"]] > 1:
            flags.append("byte-identical")
        if names[Path(record["original_path"]).name.casefold()] > 1:
            flags.append("filename-collision")
        if extension["conflict_kind"]:
            flags.append(extension["conflict_kind"])
        extension["duplicate_status"] = ",".join(sorted(set(flags))) if flags else "unique"


def summarize_inventory(records: list[dict[str, Any]], rejected: list[dict[str, str]]) -> dict[str, Any]:
    media = Counter(record["media_type"] for record in records)
    encodings = Counter(
        record["extensions"]["m1b-acquisition"]["detected_encoding_candidate"] or "unknown"
        for record in records
    )
    return {
        "entry_count": len(records),
        "total_bytes": sum(record["size"] for record in records),
        "extracted_count": sum(record["extraction_status"] == "extracted" for record in records),
        "failed_count": sum(record["extraction_status"] == "failed" for record in records),
        "skipped_count": len(rejected),
        "zero_byte_count": sum(record["size"] == 0 for record in records),
        "path_anomaly_count": sum(record["extensions"]["m1b-acquisition"]["path_status"] != "safe" for record in records),
        "unknown_media_type_count": sum(record["extensions"]["m1b-acquisition"]["media_type_confidence"] == "unknown" for record in records),
        "media_types": dict(sorted(media.items())),
        "encoding_candidates": dict(sorted(encodings.items())),
        "rejected_non_regular": rejected,
    }
