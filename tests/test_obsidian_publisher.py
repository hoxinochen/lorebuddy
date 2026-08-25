from __future__ import annotations

import hashlib
import json
from pathlib import Path

from lorebuddy.cli import main
from lorebuddy.publishing import (
    ObsidianPublisherError,
    dry_run_obsidian_baseline,
    publish_obsidian_baseline,
    validate_obsidian_baseline,
)
from lorebuddy.publishing.obsidian import _navigation_affinity


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
    )


def _jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def _note(
    *,
    artifact_id: str,
    entry_id: str,
    source_path: str,
    source_sha256: str,
    navigation_paths: list[str],
    body: str,
) -> bytes:
    navigation = (
        "navigation_paths:\n"
        + "".join(
            f"  - {json.dumps(path, ensure_ascii=False)}\n"
            for path in navigation_paths
        )
        if navigation_paths
        else "navigation_paths: []\n"
    )
    return (
        "---\n"
        f"artifact_id: {json.dumps(artifact_id)}\n"
        f"entry_id: {json.dumps(entry_id)}\n"
        f"source_path: {json.dumps(source_path, ensure_ascii=False)}\n"
        f"{navigation}"
        f"source_sha256: {json.dumps(source_sha256)}\n"
        'detected_encoding: "utf-8"\n'
        "---\n"
        f"{body}"
    ).encode("utf-8")


def _m1c2a_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "m1c2a"
    (root / "markdown").mkdir(parents=True)
    (root / "assets" / "aaaaaaaa").mkdir(parents=True)
    artifact_id = "urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408"
    first_id = "urn:uuid:11111111-1111-5111-8111-111111111111"
    second_id = "urn:uuid:22222222-2222-5222-8222-222222222222"
    hhc_id = "urn:uuid:99999999-9999-5999-8999-999999999999"
    first_source = "book/one.htm"
    second_source = "book/two.htm"
    first_source_digest = "sha256:" + "1" * 64
    second_source_digest = "sha256:" + "2" * 64
    first_path = "markdown/第一页--11111111.md"
    second_path = "markdown/第二页-(测试)--22222222.md"
    asset_path = "assets/aaaaaaaa/image file.png"
    asset = b"\x89PNG\r\n\x1a\nfixture"
    (root / asset_path).write_bytes(asset)
    first = _note(
        artifact_id=artifact_id,
        entry_id=first_id,
        source_path=first_source,
        source_sha256=first_source_digest,
        navigation_paths=["Book/Chapter/第一页", "Alternate/第一页"],
        body=(
            "# 第一页\n\n"
            "[已解析页面](第二页-(测试)--22222222.md#part)\n\n"
            "![图片](../assets/aaaaaaaa/image file.png)\n\n"
            "未解析目标\n"
        ),
    )
    second = _note(
        artifact_id=artifact_id,
        entry_id=second_id,
        source_path=second_source,
        source_sha256=second_source_digest,
        navigation_paths=["Book/Chapter/第二页"],
        body='# 第二页\n\n<a id="part"></a>\n\n正文\n',
    )
    (root / first_path).write_bytes(first)
    (root / second_path).write_bytes(second)
    manifest = [
        {
            "detected_encoding": "utf-8",
            "entry_id": first_id,
            "navigation_paths": ["Book/Chapter/第一页", "Alternate/第一页"],
            "output_path": first_path,
            "source_path": first_source,
            "source_sha256": first_source_digest,
        },
        {
            "detected_encoding": "utf-8",
            "entry_id": second_id,
            "navigation_paths": ["Book/Chapter/第二页"],
            "output_path": second_path,
            "source_path": second_source,
            "source_sha256": second_source_digest,
        },
    ]
    entries = [
        {
            "entry_id": first_id,
            "status": "success",
            "title": "第一页",
            "output_path": first_path,
        },
        {
            "entry_id": second_id,
            "status": "success",
            "title": "第二页",
            "output_path": second_path,
        },
    ]
    _json(
        root / ".lorebuddy-m1c2a.json",
        {
            "schema": "m1c2a.full-markdown-build@0.1.0",
            "artifact_id": artifact_id,
        },
    )
    (root / "README.md").write_text("# Fixture\n", encoding="utf-8")
    _jsonl(root / "markdown-manifest.jsonl", manifest)
    _jsonl(root / "reports/entries.jsonl", entries)
    _json(
        root / "reports/build-report.json",
        {
            "summary": {
                "html_success_count": 2,
                "html_failed_count": 0,
                "unresolved_reference_count": 1,
            }
        },
    )
    _json(root / "reports/encoding-report.json", {"summary": {}})
    _json(root / "reports/fidelity-report.json", {"summary": {}})
    _json(
        root / "reports/link-report.json",
        {
            "resolved": [
                {
                    "source_entry_id": first_id,
                    "raw_target": "two.htm#part",
                    "output_target": "第二页-(测试)--22222222.md#part",
                    "target_entry_id": second_id,
                    "resolution": "converted-page",
                }
            ],
            "unresolved": [
                {
                    "source_entry_id": first_id,
                    "kind": "link",
                    "raw_target": "missing.htm",
                    "resolved_source_path": "book/missing.htm",
                    "target_entry_id": None,
                    "reason": "target-not-found",
                }
            ],
            "summary": {"resolved_count": 1, "unresolved_count": 1},
        },
    )
    _json(
        root / "reports/asset-report.json",
        {
            "assets": [
                {
                    "entry_id": "urn:uuid:aaaaaaaa-aaaa-5aaa-8aaa-aaaaaaaaaaaa",
                    "output_path": asset_path,
                    "source_path": "book/image.png",
                    "source_sha256": _digest(asset),
                }
            ],
            "summary": {
                "image_reference_count": 1,
                "unique_copied_asset_count": 1,
                "missing_asset_count": 0,
            },
        },
    )
    navigation_nodes = [
        {
            "schema": "m1c2a.navigation-node@0.1.0",
            "navigation_node_id": f"urn:uuid:{number:08d}-0000-5000-8000-{number:012d}",
            "source_entry_id": hhc_id,
            "source_order": number - 1,
            "parent_node_id": parent,
            "sibling_order": sibling,
            "depth": depth,
            "title": title,
            "local": local,
            "navigation_path": path,
            "target_entry_id": target,
            "target_status": "resolved-entry" if target else "no-local",
        }
        for number, parent, sibling, depth, title, local, path, target in [
            (1, None, 0, 1, "Book", None, "Book", None),
            (
                2,
                "urn:uuid:00000001-0000-5000-8000-000000000001",
                0,
                2,
                "Chapter",
                None,
                "Book/Chapter",
                None,
            ),
            (
                3,
                "urn:uuid:00000002-0000-5000-8000-000000000002",
                0,
                3,
                "第一页",
                first_source,
                "Book/Chapter/第一页",
                first_id,
            ),
            (
                4,
                "urn:uuid:00000002-0000-5000-8000-000000000002",
                1,
                3,
                "第二页",
                second_source,
                "Book/Chapter/第二页",
                second_id,
            ),
            (5, None, 1, 1, "Alternate", None, "Alternate", None),
            (
                6,
                "urn:uuid:00000005-0000-5000-8000-000000000005",
                0,
                2,
                "第一页",
                first_source,
                "Alternate/第一页",
                first_id,
            ),
        ]
    ]
    _jsonl(root / "reports/navigation-tree.jsonl", navigation_nodes)
    _json(
        root / "reports/navigation-report.json",
        {
            "sources": [
                {
                    "entry_id": hhc_id,
                    "source_path": "toc.hhc",
                    "source_sha256": "sha256:" + "9" * 64,
                }
            ],
            "summary": {
                "entry_with_navigation_count": 2,
                "navigation_occurrence_count": 3,
                "entry_with_multiple_navigation_paths_count": 1,
                "navigation_node_count": 6,
                "pure_directory_node_count": 3,
                "resolved_target_node_count": 3,
                "missing_target_node_count": 0,
            },
        },
    )
    return root


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_publisher_dry_run_build_validation_and_determinism(tmp_path: Path) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    first = tmp_path / "first-vault"
    second = tmp_path / "second-vault"

    dry_run = dry_run_obsidian_baseline(build_root, first)
    assert dry_run["dry_run"] is True
    assert dry_run["changes"]["create_count"] > 0
    assert not first.exists()

    first_result = publish_obsidian_baseline(build_root, first)
    second_result = publish_obsidian_baseline(build_root, second)
    assert first_result["valid"] is True
    assert second_result["valid"] is True
    assert _files(first) == _files(second)

    manifest = [
        json.loads(line)
        for line in (first / ".lorebuddy/publisher-manifest.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    first_note = first / next(
        item["output_path"]
        for item in manifest
        if item["source_path"] == "book/one.htm"
    )
    text = first_note.read_text(encoding="utf-8")
    assert 'publisher_profile: "m1c3.obsidian-baseline@0.1.0"' in text
    assert first_note.relative_to(first).as_posix() == "Notes/Book/Chapter/第一页.md"
    assert "[已解析页面](第二页.md#part)" in text
    assert "![图片](<../../../Assets/aaaaaaaa/image file.png>)" in text
    assert "未解析目标" in text
    assert len(list((first / "Notes").rglob("*.md"))) == 2
    assert len(list((first / "Books").rglob("*.md"))) == 3
    chapter_index = (
        first / "Books/Book/Chapter/_目录.md"
    ).read_text(encoding="utf-8")
    assert chapter_index.index("第一页") < chapter_index.index("第二页")
    assert (first / "Books/Alternate/_目录.md").is_file()
    assert validate_obsidian_baseline(first)["valid"] is True


def test_note_paths_use_hierarchy_and_suffix_only_collisions(tmp_path: Path) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    manifest_path = build_root / "markdown-manifest.jsonl"
    manifest = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
    ]
    manifest[1]["navigation_paths"] = ["Book/Chapter/第一页"]
    _jsonl(manifest_path, manifest)
    entries_path = build_root / "reports/entries.jsonl"
    entries = [
        json.loads(line)
        for line in entries_path.read_text(encoding="utf-8").splitlines()
    ]
    entries[1]["title"] = "第一页"
    _jsonl(entries_path, entries)
    second_note = build_root / manifest[1]["output_path"]
    second_text = second_note.read_text(encoding="utf-8").replace(
        'navigation_paths:\n  - "Book/Chapter/第二页"\n',
        'navigation_paths:\n  - "Book/Chapter/第一页"\n',
    )
    second_note.write_text(second_text, encoding="utf-8")
    tree_path = build_root / "reports/navigation-tree.jsonl"
    tree = [
        json.loads(line) for line in tree_path.read_text(encoding="utf-8").splitlines()
    ]
    second_node = next(node for node in tree if node.get("target_entry_id") == manifest[1]["entry_id"])
    second_node["title"] = "第一页"
    second_node["navigation_path"] = "Book/Chapter/第一页"
    _jsonl(tree_path, tree)

    output = tmp_path / "vault"
    result = publish_obsidian_baseline(build_root, output)
    assert result["valid"] is True
    note_paths = sorted(
        path.relative_to(output).as_posix()
        for path in (output / "Notes").rglob("*.md")
    )
    assert note_paths == [
        "Notes/Book/Chapter/第一页--11111111.md",
        "Notes/Book/Chapter/第一页--22222222.md",
    ]
    report = json.loads(
        (output / ".lorebuddy/publish-report.json").read_text(encoding="utf-8")
    )
    assert report["summary"]["note_path_collision_count"] == 2


def test_primary_navigation_prefers_source_path_affinity_over_hhc_first() -> None:
    source_path = "第三方/拳斗士/拳斗士.htm"
    shortcut = ["本书速查", "职业速查", "拳斗士"]
    content_tree = ["拳斗士", "拳斗士"]
    assert _navigation_affinity(content_tree, source_path) > _navigation_affinity(
        shortcut, source_path
    )


def test_note_path_keeps_visible_dots_in_navigation_title(tmp_path: Path) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    manifest_path = build_root / "markdown-manifest.jsonl"
    manifest = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
    ]
    manifest[0]["navigation_paths"][0] = "Book/Version 1.2"
    _jsonl(manifest_path, manifest)
    first_note = build_root / manifest[0]["output_path"]
    first_text = first_note.read_text(encoding="utf-8").replace(
        '  - "Book/Chapter/第一页"\n',
        '  - "Book/Version 1.2"\n',
        1,
    )
    first_note.write_text(first_text, encoding="utf-8")
    tree_path = build_root / "reports/navigation-tree.jsonl"
    tree = [
        json.loads(line) for line in tree_path.read_text(encoding="utf-8").splitlines()
    ]
    first_node = next(
        node
        for node in tree
        if node.get("target_entry_id") == manifest[0]["entry_id"]
        and node["navigation_path"] == "Book/Chapter/第一页"
    )
    first_node["title"] = "Version 1.2"
    first_node["navigation_path"] = "Book/Version 1.2"
    first_node["parent_node_id"] = "urn:uuid:00000001-0000-5000-8000-000000000001"
    first_node["depth"] = 2
    first_node["sibling_order"] = 1
    second_node = next(
        node
        for node in tree
        if node.get("target_entry_id") == manifest[1]["entry_id"]
    )
    second_node["sibling_order"] = 0
    _jsonl(tree_path, tree)

    output = tmp_path / "vault"
    assert publish_obsidian_baseline(build_root, output)["valid"] is True
    assert (output / "Notes/Book/Version 1.2.md").is_file()


def test_unclassified_notes_remain_reachable_from_navigation(
    tmp_path: Path,
) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    manifest_path = build_root / "markdown-manifest.jsonl"
    manifest = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
    ]
    manifest[1]["navigation_paths"] = []
    _jsonl(manifest_path, manifest)
    second_note = build_root / manifest[1]["output_path"]
    second_text = second_note.read_text(encoding="utf-8").replace(
        'navigation_paths:\n  - "Book/Chapter/第二页"\n',
        "navigation_paths: []\n",
    )
    second_note.write_text(second_text, encoding="utf-8")
    tree_path = build_root / "reports/navigation-tree.jsonl"
    tree = [
        json.loads(line)
        for line in tree_path.read_text(encoding="utf-8").splitlines()
        if '"target_entry_id":"urn:uuid:22222222-2222-5222-8222-222222222222"'
        not in line
    ]
    _jsonl(tree_path, tree)
    navigation_report_path = build_root / "reports/navigation-report.json"
    navigation_report = json.loads(navigation_report_path.read_text(encoding="utf-8"))
    navigation_report["summary"].update(
        {
            "entry_with_navigation_count": 1,
            "navigation_occurrence_count": 2,
            "entry_with_multiple_navigation_paths_count": 1,
            "navigation_node_count": 5,
            "resolved_target_node_count": 2,
        }
    )
    _json(navigation_report_path, navigation_report)

    output = tmp_path / "vault"
    assert publish_obsidian_baseline(build_root, output)["valid"] is True
    assert (output / "Notes/_Unclassified/第二页.md").is_file()
    unclassified = (output / "Books/_Unclassified/_目录.md").read_text(
        encoding="utf-8"
    )
    assert "[第二页]" in unclassified


def test_publisher_refuses_unknown_output_and_validator_detects_missing_asset(
    tmp_path: Path,
) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "user.md").write_text("user", encoding="utf-8")
    try:
        publish_obsidian_baseline(build_root, unknown)
    except ObsidianPublisherError as exc:
        assert "拒绝覆盖" in str(exc)
    else:
        raise AssertionError("应拒绝覆盖未知目录")

    output = tmp_path / "vault"
    publish_obsidian_baseline(build_root, output)
    (output / "Assets/aaaaaaaa/image file.png").unlink()
    result = validate_obsidian_baseline(output)
    assert result["valid"] is False
    assert any(
        error["code"] in {"OWNERSHIP_CLOSURE", "MISSING_LOCAL_IMAGE"}
        for error in result["errors"]
    )


def test_obsidian_cli_dry_run_publish_validate_and_report(
    tmp_path: Path, project_root: Path, capsys
) -> None:
    build_root = _m1c2a_fixture(tmp_path)
    output = tmp_path / "vault"
    assert (
        main(
            [
                "obsidian",
                "publish",
                str(build_root),
                "--output",
                str(output),
                "--dry-run",
                "--json",
            ],
            project_root=project_root,
        )
        == 0
    )
    assert not output.exists()
    assert (
        main(
            [
                "obsidian",
                "publish",
                str(build_root),
                "--output",
                str(output),
                "--json",
            ],
            project_root=project_root,
        )
        == 0
    )
    assert (
        main(
            ["obsidian", "validate", str(output), "--json"],
            project_root=project_root,
        )
        == 0
    )
    assert (
        main(
            ["obsidian", "report", str(output), "--json"],
            project_root=project_root,
        )
        == 0
    )
    assert '"valid": true' in capsys.readouterr().out.lower()
