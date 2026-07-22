"""确定性 JSON / JSONL 产物写出与语义摘要。"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        for value in values:
            stream.write(canonical_bytes(value))


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_inventory_digest(inventory_dir: Path) -> str:
    names = (
        "package.json", "artifact.json", "entries.jsonl", "path-map.jsonl",
        "duplicate-report.json",
    )
    digest = hashlib.sha256()
    for name in names:
        path = inventory_dir / name
        digest.update(name.encode("utf-8") + b"\x00")
        digest.update(path.read_bytes())
    return digest.hexdigest()
