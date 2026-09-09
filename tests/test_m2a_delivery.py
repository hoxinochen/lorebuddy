from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from lorebuddy.validation.m2a_delivery import validate_m2a_delivery


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")


def _refresh_delivery_digests(root: Path) -> None:
    manifest_path = root / "m2a-delivery-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["delivery_files"]:
        path = root / item["relative_path"]
        item["sha256"] = _sha256(path)
        item["file_size_bytes"] = path.stat().st_size
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _delivery(tmp_path: Path) -> tuple[Path, Path]:
    upstream = tmp_path / "publisher-manifest.jsonl"
    m1_records = [
        {
            "entry_id": "urn:uuid:00000000-0000-0000-0000-000000000001",
            "artifact_id": "urn:uuid:11111111-1111-1111-1111-111111111111",
            "publisher_profile": "m1c3.obsidian-baseline@0.1.0",
            "source_path": "book/entry.htm",
            "output_path": "Notes/book/entry.md",
        },
        {
            "entry_id": "urn:uuid:00000000-0000-0000-0000-000000000002",
            "artifact_id": "urn:uuid:11111111-1111-1111-1111-111111111111",
            "publisher_profile": "m1c3.obsidian-baseline@0.1.0",
            "source_path": "meta.htm",
            "output_path": "Notes/meta.md",
        },
    ]
    _write_jsonl(upstream, m1_records)
    root = tmp_path / "delivery"
    root.mkdir()
    _write_jsonl(
        root / "entry-to-book-mapping.m2a.jsonl",
        [
            {
                "entry_id": m1_records[0]["entry_id"],
                "book_id": "book-2024",
                "source_path": m1_records[0]["source_path"],
                "output_path": m1_records[0]["output_path"],
                "mapping_basis": "source_path_top_level_root",
                "mapping_status": "deterministic",
                "source_identity_status": "claimed",
            }
        ],
    )
    _write_jsonl(
        root / "review-queue.jsonl",
        [
            {
                "entry_id": m1_records[1]["entry_id"],
                "source_path": m1_records[1]["source_path"],
                "output_path": m1_records[1]["output_path"],
                "reason": "system_divider_or_meta",
            }
        ],
    )
    (root / "book-catalog.yaml").write_text("- id: book-2024\n  name_zh: 测试书\n", encoding="utf-8")
    (root / "ruleset-profiles.yaml").write_text(
        "profiles:\n- id: strict\n  name: 测试\n  description: 仅选择书籍\n  active_books:\n  - book-2024\n  fallback_books: []\n",
        encoding="utf-8",
    )
    files = []
    for name, kind in (
        ("entry-to-book-mapping.m2a.jsonl", "mapping"),
        ("review-queue.jsonl", "review_queue"),
        ("book-catalog.yaml", "book_catalog"),
        ("ruleset-profiles.yaml", "ruleset_profiles"),
    ):
        path = root / name
        files.append(
            {
                "relative_path": name,
                "file_type": kind,
                "sha256": _sha256(path),
                "file_size_bytes": path.stat().st_size,
                "record_count": 1 if path.suffix == ".jsonl" else 0,
            }
        )
    (root / "m2a-delivery-manifest.json").write_text(
        json.dumps(
            {
                "generator_version": "fixture@1",
                "reproducible_command": "python3 generate.py",
                "upstream_input": {
                    "logical_identity": m1_records[0]["artifact_id"],
                    "profile": m1_records[0]["publisher_profile"],
                    "sha256": _sha256(upstream),
                    "entry_total_count": len(m1_records),
                },
                "delivery_files": files,
            }
        ),
        encoding="utf-8",
    )
    return root, upstream


def test_m2a_delivery_accepts_a_closed_claimed_catalog(tmp_path: Path) -> None:
    root, upstream = _delivery(tmp_path)
    assert validate_m2a_delivery(root, upstream)["valid"]


def test_m2a_delivery_rejects_unreviewed_catalog_status_and_profile_semantics(tmp_path: Path) -> None:
    root, upstream = _delivery(tmp_path)
    (root / "book-catalog.yaml").write_text(
        "- id: book-2024\n  name_zh: 测试书\n  authority: official-current\n", encoding="utf-8"
    )
    profiles = yaml.safe_load((root / "ruleset-profiles.yaml").read_text(encoding="utf-8"))
    profiles["profiles"][0]["version_precedence"] = ["2024"]
    (root / "ruleset-profiles.yaml").write_text(yaml.safe_dump(profiles, allow_unicode=True), encoding="utf-8")
    _refresh_delivery_digests(root)
    result = validate_m2a_delivery(root, upstream)
    assert not result["valid"]
    assert {error["code"] for error in result["errors"]} >= {
        "CATALOG_UNREVIEWED_STATUS",
        "PROFILE_SEMANTIC_FIELD",
    }
