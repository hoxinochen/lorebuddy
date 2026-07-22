"""Entry 重复与冲突的确定性报告。"""

from __future__ import annotations

from collections import defaultdict
from pathlib import PurePosixPath
from typing import Any


def build_duplicate_report(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_digest: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    path_conflicts: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        by_digest[entry["digest"]].append(entry)
        by_name[PurePosixPath(entry["original_path"]).name.casefold()].append(entry)
        ext = entry.get("extensions", {}).get("m1b-acquisition", {})
        if ext.get("conflict_kind"):
            path_conflicts[ext["conflict_kind"]].append(entry["id"])
    same_content = [
        {"digest": digest, "entry_ids": sorted(item["id"] for item in items), "paths": sorted(item["original_path"] for item in items)}
        for digest, items in by_digest.items() if len(items) > 1
    ]
    same_name_different = []
    for name, items in by_name.items():
        digests = {item["digest"] for item in items}
        if len(items) > 1 and len(digests) > 1:
            same_name_different.append({"filename_key": name, "entry_ids": sorted(item["id"] for item in items)})
    same_content.sort(key=lambda group: group["digest"])
    same_name_different.sort(key=lambda group: group["filename_key"])
    return {
        "schema": "m1b.duplicate-report@0.1.0",
        "byte_identical_groups": same_content,
        "same_name_different_content_groups": same_name_different,
        "path_conflicts": {key: sorted(value) for key, value in sorted(path_conflicts.items())},
        "summary": {
            "byte_identical_groups": len(same_content),
            "same_name_different_content_groups": len(same_name_different),
            "path_conflict_entries": sum(len(value) for value in path_conflicts.values()),
        },
    }
