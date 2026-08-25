from __future__ import annotations

import hashlib
import json
from pathlib import Path

from lorebuddy.cli import main
from lorebuddy.samples import m1c1


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _record(entry_id: str, source_path: str, storage_path: str, data: bytes, *, media_type="text/html", conflict=False):
    return {
        "schema": "core.source-entry@0.1.0",
        "id": entry_id,
        "artifact_id": m1c1.ARTIFACT_ID,
        "original_path": source_path,
        "storage_path": storage_path,
        "size": len(data),
        "digest": _digest(data),
        "media_type": media_type,
        "charset": {"declared": "gb2312" if conflict else "utf-8", "detected": "utf-8", "status": "mismatch" if conflict else "unknown"},
        "extraction_status": "extracted",
        "lifecycle": {"status": "draft", "revision": 1},
        "extensions": {"m1b-acquisition": {"declared_encoding": "gb2312" if conflict else "utf-8", "detected_encoding_candidate": "utf-8", "encoding_conflict": conflict}},
    }


def _artifact(tmp_path: Path, monkeypatch):
    root = tmp_path / "artifact"
    (root / "inventory").mkdir(parents=True)
    (root / "extracted" / "entries" / "book").mkdir(parents=True)
    ids = [f"urn:uuid:{index:08d}-0000-5000-8000-{index:012d}" for index in range(1, 6)]
    selections = []
    records = []
    for index, entry_id in enumerate(ids):
        anchor = ' id="part"' if index == 1 else ""
        extra = '<a href="page1.htm#part">内部</a><img src="image.png" alt="图">' if index == 0 else ""
        if index == 2:
            extra = '<a href="missing.htm">缺失目标</a>'
        data = f'<html><head><title>同名标题</title><style>x</style></head><body><h1{anchor}>标题{index}</h1><ul><li>项目</li></ul>{extra}</body></html>'.encode()
        storage = f"entries/book/page{index}.htm"
        (root / "extracted" / storage).write_bytes(data)
        records.append(_record(entry_id, f"book/page{index}.htm", storage, data, conflict=index == 0))
        selections.append((entry_id, ["fixture"]))
    asset_id = "urn:uuid:00000000-0000-5000-8000-999999999999"
    asset = b"\x89PNG\r\n\x1a\nfixture"
    (root / "extracted" / "entries/book/image.png").write_bytes(asset)
    records.append(_record(asset_id, "book/image.png", "entries/book/image.png", asset, media_type="image/png"))
    hhc_id = "urn:uuid:00000000-0000-5000-8000-888888888888"
    hhc = b'''<ul><li><object type="text/sitemap"><param name="Name" value="Book"><param name="Local" value="book/index.htm"></object><ul><li><object type="text/sitemap"><param name="Name" value="Chapter"><param name="Local" value="book/chapter.htm"></object><ul><li><object type="text/sitemap"><param name="Name" value="Page Zero"><param name="Local" value="book/page0.htm"></object></ul></ul></ul>'''
    (root / "extracted" / "entries" / "toc.hhc").write_bytes(hhc)
    records.append(_record(hhc_id, "toc.hhc", "entries/toc.hhc", hhc))
    (root / "inventory" / "artifact.json").write_text(json.dumps({"id": m1c1.ARTIFACT_ID}), encoding="utf-8")
    with (root / "inventory" / "entries.jsonl").open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    monkeypatch.setattr(m1c1, "SELECTIONS", tuple(selections))
    return root


def _files(root: Path):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_decode_conflict_uses_detected_candidate():
    record = {"id": "x", "extensions": {"m1b-acquisition": {"declared_encoding": "gb2312", "detected_encoding_candidate": "utf-8"}}}
    text, encoding, attempts = m1c1._decode(record, "中文".encode())
    assert text == "中文" and encoding == "utf-8" and attempts == ["utf-8"]


def test_sample_build_cli_metadata_links_assets_and_determinism(tmp_path: Path, project_root: Path, monkeypatch, capsys):
    artifact = _artifact(tmp_path, monkeypatch)
    first = tmp_path / "first"
    second = tmp_path / "second"
    assert main(["samples", "build", str(artifact), "--output", str(first), "--json"], project_root=project_root) == 0
    assert main(["samples", "build", str(artifact), "--output", str(second), "--json"], project_root=project_root) == 0
    assert _files(first) == _files(second)
    selection = json.loads((first / "sample-selection.json").read_text())
    assert len({sample["output_path"] for sample in selection["samples"]}) == 5
    page_zero = next(sample for sample in selection["samples"] if sample["source_path"] == "book/page0.htm")
    assert page_zero["navigation_paths"] == ["Book/Chapter/Page Zero"]
    first_note = first / selection["samples"][0]["output_path"]
    text = first_note.read_text()
    assert "artifact_id:" in text and "entry_id:" in text and "source_sha256:" in text and "navigation_paths:" in text
    assert 'source_path: "book/page0.htm"' in text
    assert '  - "Book/Chapter/Page Zero"' in text
    assert "../assets/" in text
    unresolved = json.loads((first / "reports/unresolved-links.json").read_text())
    assert any(item["reason"] == "target-not-found" for item in unresolved["items"])
    assert not any(item["raw_target"] == "page1.htm#part" for item in unresolved["items"])
    assert main(["samples", "validate", str(first), "--json"], project_root=project_root) == 0
    assert '"valid": true' in capsys.readouterr().out.lower()


def test_full_markdown_build_is_deterministic_and_isolates_page_failure(tmp_path: Path, project_root: Path, monkeypatch, capsys):
    artifact = _artifact(tmp_path, monkeypatch)
    broken_id = "urn:uuid:00000000-0000-5000-8000-777777777777"
    broken = b"\xff"
    broken_path = artifact / "extracted" / "entries" / "book" / "broken.htm"
    broken_path.write_bytes(broken)
    record = _record(broken_id, "book/broken.htm", "entries/book/broken.htm", broken)
    record["extensions"]["m1b-acquisition"]["detected_encoding_candidate"] = "utf-8"
    with (artifact / "inventory" / "entries.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    first = tmp_path / "full-first"
    second = tmp_path / "full-second"
    assert main(["markdown", "build", str(artifact), "--output", str(first), "--json"], project_root=project_root) == 0
    assert main(["markdown", "build", str(artifact), "--output", str(second), "--json"], project_root=project_root) == 0
    assert _files(first) == _files(second)
    report = json.loads((first / "reports" / "build-report.json").read_text())
    assert report["summary"]["html_success_count"] == 6
    assert report["summary"]["html_failed_count"] == 1
    manifest = [json.loads(line) for line in (first / "markdown-manifest.jsonl").read_text().splitlines()]
    assert len({item["entry_id"] for item in manifest}) == 6
    page_zero = next(item for item in manifest if item["source_path"] == "book/page0.htm")
    assert page_zero["navigation_paths"] == ["Book/Chapter/Page Zero"]
    navigation_tree = [
        json.loads(line)
        for line in (first / "reports/navigation-tree.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [node["title"] for node in navigation_tree] == [
        "Book",
        "Chapter",
        "Page Zero",
    ]
    assert [node["source_order"] for node in navigation_tree] == [0, 1, 2]
    assert navigation_tree[1]["parent_node_id"] == navigation_tree[0]["navigation_node_id"]
    assert navigation_tree[0]["target_status"] == "target-not-found"
    assert navigation_tree[2]["target_entry_id"] == page_zero["entry_id"]
    assert navigation_tree[2]["target_status"] == "resolved-entry"
    assert main(["markdown", "validate", str(first), "--json"], project_root=project_root) == 0

    note = first / page_zero["output_path"]
    note.write_text(note.read_text().replace('source_path: "book/page0.htm"', 'source_path: "Book/Chapter/Page Zero"'), encoding="utf-8")
    assert main(["markdown", "validate", str(first), "--json"], project_root=project_root) == 1
    assert "front_matter_mismatch" in capsys.readouterr().out.lower()
