"""M1-C2A 全量 HTML → Markdown 构建、报告与语义 Validator。"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from .html_to_markdown import MarkdownRenderer, collect_anchors, first_text, parse_html, source_visible_segments
from .m1c1 import (
    ARTIFACT_ID,
    Resolver,
    _decode,
    _load_inventory,
    _load_navigation,
    _path_key,
    _readable_filename,
    _retention_ratio,
    _write_json,
    _yaml_string,
)


FULL_BUILD_SCHEMA = "m1c2a.full-markdown-build@0.1.0"
PRIVATE_PATH_PATTERN = re.compile(r"(?:/Users/[^/\s]+/|/home/[^/\s]+/)")
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
HTML_IMAGE_PATTERN = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)


class M1C2AError(RuntimeError):
    pass


def _jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def _safe_source_file(artifact_dir: Path, record: dict[str, Any]) -> Path:
    extracted = (artifact_dir / "extracted").resolve(strict=True)
    source = (extracted / record["storage_path"]).resolve(strict=True)
    if not source.is_relative_to(extracted) or not source.is_file() or source.is_symlink():
        raise M1C2AError(f"Source Entry 不是受控普通文件：{record['id']}")
    return source


def _source_bytes(artifact_dir: Path, record: dict[str, Any]) -> bytes:
    source = _safe_source_file(artifact_dir, record)
    raw = source.read_bytes()
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if len(raw) != record["size"] or digest != record["digest"]:
        raise M1C2AError(f"Source Entry 字节事实与 Inventory 不一致：{record['id']}")
    return raw


def _front_matter(record: dict[str, Any], navigation_paths: list[str], encoding: str) -> str:
    navigation_lines = (["navigation_paths:"] + [f"  - {_yaml_string(path)}" for path in navigation_paths]) if navigation_paths else ["navigation_paths: []"]
    return "\n".join([
        "---",
        f"artifact_id: {_yaml_string(ARTIFACT_ID)}",
        f"entry_id: {_yaml_string(record['id'])}",
        f"source_path: {_yaml_string(record['original_path'])}",
        *navigation_lines,
        f"source_sha256: {_yaml_string(record['digest'])}",
        f"detected_encoding: {_yaml_string(encoding)}",
        "---",
        "",
    ])


def _disambiguate_outputs(candidates: list[dict[str, Any]]) -> None:
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in candidates:
        by_name[item["output_path"].casefold()].append(item)
    for collided in by_name.values():
        if len(collided) < 2:
            continue
        for item in collided:
            suffix = item["entry_id"].removeprefix("urn:uuid:").replace("-", "")
            title = PurePosixPath(item["output_path"]).name.rsplit("--", 1)[0]
            item["output_path"] = f"markdown/{title}--{suffix}.md"
            item["warnings"].append("output-name-collision-used-full-entry-id")


def _preflight(artifact_dir: Path, entries: list[dict[str, Any]], navigation_by_path: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    terminal: list[dict[str, Any]] = []
    html_entries = sorted((entry for entry in entries if entry.get("media_type") == "text/html"), key=lambda entry: entry["id"])
    for record in html_entries:
        base = {
            "entry_id": record["id"],
            "source_path": record["original_path"],
            "source_sha256": record["digest"],
            "navigation_paths": navigation_by_path.get(_path_key(record["original_path"]), []),
            "warnings": [],
            "errors": [],
        }
        if record.get("extraction_status") != "extracted":
            terminal.append({**base, "status": "skipped", "stage": "preflight", "reason": "source-entry-not-extracted", "output_path": None})
            continue
        try:
            raw = _source_bytes(artifact_dir, record)
            text, encoding, attempts = _decode(record, raw)
            tree = parse_html(text)
            title = first_text(tree, "title") or first_text(tree, "h1") or first_text(tree, "h2") or PurePosixPath(record["original_path"]).stem
            candidates.append({
                **base,
                "record": record,
                "title": title,
                "encoding": encoding,
                "decode_attempts": attempts,
                "anchors": collect_anchors(tree),
                "output_path": f"markdown/{_readable_filename(title, record['id'])}",
            })
        except Exception as exc:
            terminal.append({**base, "status": "failed", "stage": "preflight", "reason": type(exc).__name__, "output_path": None, "errors": [str(exc)]})
    _disambiguate_outputs(candidates)
    return candidates, terminal


def _write_readme(target: Path, report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# LoreBuddy M1-C2A 全量 Markdown 构建",
        "",
        f"Artifact ID：`{ARTIFACT_ID}`",
        "",
        "本目录是确定性、可重建的发布层输入，不是 Knowledge Node、Library 或最终 Obsidian 目录。",
        "",
        "`source_path` 是物理 CHM Entry 路径及相对 Link/Image 解析基准；`navigation_paths` 是有序、可一对多的 HHC 导航路径。导航路径不参与正文复制。",
        "",
        "## 统计",
        "",
        f"- Inventory Entry：{summary['total_entry_count']}",
        f"- HTML Entry：{summary['html_entry_count']}",
        f"- 转换成功：{summary['html_success_count']}",
        f"- 转换失败：{summary['html_failed_count']}",
        f"- HTML 跳过：{summary['html_skipped_count']}",
        f"- 非 HTML 跳过：{summary['non_html_skipped_count']}",
        f"- 唯一资产：{summary['unique_asset_count']}",
        f"- Unresolved：{summary['unresolved_reference_count']}",
        "",
        "## 稳定输入接口",
        "",
        "- `markdown-manifest.jsonl`：后续 Publisher 的逐 Entry 输入清单。",
        "- `markdown/`：每个成功物理 Entry 恰好一份正文。",
        "- `assets/`：按资产 Entry ID 隔离的原始字节。",
        "- `reports/`：构建、编码、保真、链接、资产与导航报告。",
        "",
        "下一阶段优先实现不拆 Fragment 的 Obsidian Baseline Publisher，使用户尽快获得可直接打开、可浏览且图片和链接有效的完整 Vault；本阶段不实现 Publisher，也不规定最终 Vault 目录布局。",
        "",
    ]
    (target / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _build_in_owned_dir(artifact_dir: Path, target: Path) -> dict[str, Any]:
    entries = _load_inventory(artifact_dir)
    by_path = {_path_key(entry["original_path"]): entry for entry in entries}
    navigation_by_path, navigation_sources, navigation_nodes = _load_navigation(
        artifact_dir, entries
    )
    candidates, results = _preflight(artifact_dir, entries, navigation_by_path)
    outputs = {item["entry_id"]: PurePosixPath(item["output_path"]).name for item in candidates}
    ids_by_path = {_path_key(item["source_path"]): item["entry_id"] for item in candidates}
    anchors_by_id = {item["entry_id"]: item["anchors"] for item in candidates}
    encodings: list[dict[str, Any]] = []
    resolved_links: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    all_assets: list[dict[str, Any]] = []
    fidelity: list[dict[str, Any]] = []
    manifest: list[dict[str, Any]] = []

    for item in candidates:
        record = item["record"]
        try:
            raw = _source_bytes(artifact_dir, record)
            text, encoding, attempts = _decode(record, raw)
            tree = parse_html(text)
            resolver = Resolver(
                current=record,
                entries_by_path=by_path,
                selected_outputs=outputs,
                selected_ids_by_path=ids_by_path,
                artifact_dir=artifact_dir,
                output_root=target,
                anchors=collect_anchors(tree),
                target_anchors=anchors_by_id,
            )
            renderer = MarkdownRenderer(link_callback=resolver.link, image_callback=resolver.image)
            body = renderer.render(tree)
            markdown = _front_matter(record, item["navigation_paths"], encoding) + f"# {item['title']}\n\n" + body
            output = target / item["output_path"]
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(markdown, encoding="utf-8", newline="\n")
            segments = source_visible_segments(tree)
            ratio = _retention_ratio(segments, markdown)
            body_characters = len(re.sub(r"\s+", "", body))
            warnings = list(item["warnings"])
            if ratio < 0.98:
                warnings.append("retained-visible-text-ratio-below-0.98")
            if body_characters == 0:
                warnings.append("zero-body")
            elif body_characters < 80:
                warnings.append("extremely-short-body")
            result = {
                "entry_id": record["id"],
                "status": "success",
                "stage": "conversion",
                "title": item["title"],
                "source_path": record["original_path"],
                "navigation_paths": item["navigation_paths"],
                "source_sha256": record["digest"],
                "output_path": item["output_path"],
                "encoding": encoding,
                "markdown_bytes": len(markdown.encode("utf-8")),
                "body_characters": body_characters,
                "retained_visible_text_ratio": ratio,
                "stats": asdict(renderer.stats),
                "resolved_link_count": len(resolver.resolved_links),
                "unresolved_reference_count": len(resolver.unresolved),
                "image_reference_count": resolver.image_reference_count,
                "asset_count": len(resolver.assets),
                "warnings": warnings,
                "errors": [],
            }
            results.append(result)
            manifest.append({
                "entry_id": record["id"],
                "output_path": item["output_path"],
                "source_path": record["original_path"],
                "navigation_paths": item["navigation_paths"],
                "source_sha256": record["digest"],
                "detected_encoding": encoding,
            })
            extension = record["extensions"]["m1b-acquisition"]
            encodings.append({
                "entry_id": record["id"],
                "declared_encoding": extension.get("declared_encoding"),
                "detected_candidate": extension.get("detected_encoding_candidate"),
                "encoding_conflict": extension.get("encoding_conflict"),
                "used_encoding": encoding,
                "strict_decode_attempts": attempts,
            })
            fidelity.append({
                "entry_id": record["id"],
                "output_path": item["output_path"],
                "body_characters": body_characters,
                "retained_visible_text_ratio": ratio,
                "warnings": warnings,
            })
            resolved_links.extend(resolver.resolved_links)
            unresolved.extend(resolver.unresolved)
            all_assets.extend(resolver.assets)
        except Exception as exc:
            results.append({
                "entry_id": record["id"],
                "status": "failed",
                "stage": "conversion",
                "title": item["title"],
                "source_path": record["original_path"],
                "navigation_paths": item["navigation_paths"],
                "source_sha256": record["digest"],
                "output_path": None,
                "warnings": item["warnings"],
                "errors": [str(exc)],
                "reason": type(exc).__name__,
            })

    results.sort(key=lambda value: value["entry_id"])
    manifest.sort(key=lambda value: value["entry_id"])
    encodings.sort(key=lambda value: value["entry_id"])
    fidelity.sort(key=lambda value: value["entry_id"])
    resolved_links.sort(key=lambda value: (value["source_entry_id"], value["raw_target"], value["output_target"]))
    unresolved.sort(key=lambda value: (value["source_entry_id"], value["kind"], value["raw_target"], value["reason"]))
    unique_assets = {asset["entry_id"]: asset for asset in all_assets}
    assets = [unique_assets[key] for key in sorted(unique_assets)]
    success = [result for result in results if result["status"] == "success"]
    failed = [result for result in results if result["status"] == "failed"]
    skipped = [result for result in results if result["status"] == "skipped"]
    summary = {
        "total_entry_count": len(entries),
        "html_entry_count": sum(entry.get("media_type") == "text/html" for entry in entries),
        "html_success_count": len(success),
        "html_failed_count": len(failed),
        "html_skipped_count": len(skipped),
        "non_html_skipped_count": sum(entry.get("media_type") != "text/html" for entry in entries),
        "markdown_table_count": sum(result["stats"]["markdown_tables"] for result in success),
        "html_table_count": sum(result["stats"]["html_tables"] for result in success),
        "resolved_link_count": len(resolved_links),
        "unresolved_reference_count": len(unresolved),
        "image_reference_count": sum(result["image_reference_count"] for result in success),
        "unique_asset_count": len(assets),
        "warning_entry_count": sum(bool(result.get("warnings")) for result in results),
    }
    build_report = {
        "schema": "m1c2a.build-report@0.1.0",
        "artifact_id": ARTIFACT_ID,
        "summary": summary,
        "failure_reasons": dict(sorted(Counter(result.get("reason", "unknown") for result in failed).items())),
        "warning_reasons": dict(sorted(Counter(warning for result in results for warning in result.get("warnings", [])).items())),
    }
    _jsonl(target / "markdown-manifest.jsonl", manifest)
    _jsonl(target / "reports" / "entries.jsonl", results)
    _write_json(target / "reports" / "build-report.json", build_report)
    _write_json(target / "reports" / "encoding-report.json", {
        "schema": "m1c2a.encoding-report@0.1.0",
        "entries": encodings,
        "summary": {
            "used_encoding_distribution": dict(sorted(Counter(item["used_encoding"] for item in encodings).items())),
            "conflict_count": sum(item["encoding_conflict"] is True for item in encodings),
        },
    })
    _write_json(target / "reports" / "fidelity-report.json", {
        "schema": "m1c2a.fidelity-report@0.1.0",
        "entries": fidelity,
        "summary": {
            "below_0_98_count": sum(item["retained_visible_text_ratio"] < 0.98 for item in fidelity),
            "zero_body_count": sum(item["body_characters"] == 0 for item in fidelity),
            "extremely_short_body_count": sum(0 < item["body_characters"] < 80 for item in fidelity),
        },
    })
    _write_json(target / "reports" / "link-report.json", {
        "schema": "m1c2a.link-report@0.1.0",
        "resolved": resolved_links,
        "unresolved": unresolved,
        "summary": {
            "resolved_count": len(resolved_links),
            "unresolved_count": len(unresolved),
            "unresolved_reasons": dict(sorted(Counter(item["reason"] for item in unresolved).items())),
            "missing_anchor_count": sum(item["reason"] in {"missing-page-anchor", "missing-target-anchor"} for item in unresolved),
        },
    })
    _write_json(target / "reports" / "asset-report.json", {
        "schema": "m1c2a.asset-report@0.1.0",
        "assets": assets,
        "summary": {
            "image_reference_count": summary["image_reference_count"],
            "unique_copied_asset_count": len(assets),
            "missing_asset_count": sum(item["kind"] == "image" for item in unresolved),
        },
    })
    _write_json(target / "reports" / "navigation-report.json", {
        "schema": "m1c2a.navigation-report@0.1.0",
        "sources": navigation_sources,
        "summary": {
            "entry_with_navigation_count": sum(bool(item["navigation_paths"]) for item in manifest),
            "navigation_occurrence_count": sum(len(item["navigation_paths"]) for item in manifest),
            "entry_with_multiple_navigation_paths_count": sum(len(item["navigation_paths"]) > 1 for item in manifest),
            "navigation_node_count": len(navigation_nodes),
            "pure_directory_node_count": sum(
                item["target_status"] == "no-local" for item in navigation_nodes
            ),
            "resolved_target_node_count": sum(
                item["target_status"] == "resolved-entry"
                for item in navigation_nodes
            ),
            "missing_target_node_count": sum(
                item["target_status"] == "target-not-found"
                for item in navigation_nodes
            ),
        },
    })
    _jsonl(target / "reports" / "navigation-tree.jsonl", navigation_nodes)
    _write_readme(target, build_report)
    return validate_full_build(target)


def build_full_markdown(artifact_dir: Path, output: Path) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve(strict=True)
    artifact = json.loads((artifact_dir / "inventory" / "artifact.json").read_text(encoding="utf-8"))
    if artifact.get("id") != ARTIFACT_ID:
        raise M1C2AError(f"Artifact ID 不匹配：{artifact.get('id')}")
    output = output.resolve()
    marker = output / ".lorebuddy-m1c2a.json"
    expected_marker = {"schema": FULL_BUILD_SCHEMA, "artifact_id": ARTIFACT_ID}
    if output.exists() and (not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")) != expected_marker):
        raise M1C2AError(f"拒绝替换非 LoreBuddy M1-C2A owned 目录：{output}")
    temporary = output.with_name(f".{output.name}.building")
    if temporary.exists():
        temp_marker = temporary / ".lorebuddy-m1c2a.json"
        if not temp_marker.is_file():
            raise M1C2AError(f"拒绝清理未知临时目录：{temporary}")
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    _write_json(temporary / ".lorebuddy-m1c2a.json", expected_marker)
    try:
        result = _build_in_owned_dir(artifact_dir, temporary)
        if not result["valid"]:
            raise M1C2AError(f"全量构建 Validator 失败：{result['errors'][:3]}")
        backup = output.with_name(f".{output.name}.previous")
        if backup.exists():
            shutil.rmtree(backup)
        if output.exists():
            os.replace(output, backup)
        try:
            os.replace(temporary, output)
        except OSError:
            if backup.exists() and not output.exists():
                os.replace(backup, output)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return validate_full_build(output)
    except Exception:
        raise


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _safe_output(root: Path, relative: str) -> Path | None:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    path = (root / pure).resolve()
    return path if path.is_relative_to(root) else None


def validate_full_build(output: Path) -> dict[str, Any]:
    root = output.resolve(strict=True)
    errors: list[dict[str, str]] = []
    required = [
        "README.md",
        "markdown-manifest.jsonl",
        "reports/entries.jsonl",
        "reports/build-report.json",
        "reports/encoding-report.json",
        "reports/fidelity-report.json",
        "reports/link-report.json",
        "reports/asset-report.json",
        "reports/navigation-report.json",
        "reports/navigation-tree.jsonl",
    ]
    for relative in required:
        if not (root / relative).is_file():
            errors.append({"code": "MISSING_FILE", "message": relative})
    try:
        manifest = _load_jsonl(root / "markdown-manifest.jsonl")
        entries = _load_jsonl(root / "reports" / "entries.jsonl")
        build_report = json.loads((root / "reports" / "build-report.json").read_text(encoding="utf-8"))
        asset_report = json.loads((root / "reports" / "asset-report.json").read_text(encoding="utf-8"))
        navigation_report = json.loads(
            (root / "reports" / "navigation-report.json").read_text(encoding="utf-8")
        )
        navigation_nodes = _load_jsonl(root / "reports" / "navigation-tree.jsonl")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": errors + [{"code": "LOAD_ERROR", "message": str(exc)}], "summary": {}}
    ids: set[str] = set()
    outputs: set[str] = set()
    for item in manifest:
        entry_id = item.get("entry_id", "")
        relative = item.get("output_path", "")
        if entry_id in ids:
            errors.append({"code": "DUPLICATE_ENTRY_OUTPUT", "message": entry_id})
        ids.add(entry_id)
        if relative.casefold() in outputs:
            errors.append({"code": "DUPLICATE_OUTPUT_PATH", "message": relative})
        outputs.add(relative.casefold())
        path = _safe_output(root, relative)
        if path is None or not path.is_file() or path.is_symlink():
            errors.append({"code": "INVALID_OUTPUT_PATH", "message": relative})
            continue
        raw = path.read_bytes()
        if b"\r" in raw:
            errors.append({"code": "CR_IN_MARKDOWN", "message": relative})
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            errors.append({"code": "NOT_UTF8", "message": f"{relative}: {exc}"})
            continue
        if PRIVATE_PATH_PATTERN.search(text):
            errors.append({"code": "PRIVATE_ABSOLUTE_PATH", "message": relative})
        try:
            metadata = yaml.safe_load(text.split("---", 2)[1])
        except (IndexError, yaml.YAMLError) as exc:
            errors.append({"code": "INVALID_FRONT_MATTER", "message": f"{relative}: {exc}"})
            continue
        for field in ("entry_id", "source_path", "navigation_paths", "source_sha256", "detected_encoding"):
            if metadata.get(field) != item.get(field):
                errors.append({"code": "FRONT_MATTER_MISMATCH", "message": f"{relative}: {field}"})
        for reference in MARKDOWN_IMAGE_PATTERN.findall(text) + HTML_IMAGE_PATTERN.findall(text):
            if reference.casefold().startswith(("http://", "https://", "data:")):
                continue
            image = (path.parent / reference).resolve()
            if not image.is_relative_to(root) or not image.is_file() or image.is_symlink():
                errors.append({"code": "INVALID_LOCAL_IMAGE", "message": f"{relative}: {reference}"})
    actual_markdown = {path.relative_to(root).as_posix().casefold() for path in (root / "markdown").glob("*.md") if path.is_file()}
    if actual_markdown != outputs:
        errors.append({"code": "MARKDOWN_MANIFEST_CLOSURE", "message": f"actual={len(actual_markdown)} manifest={len(outputs)}"})
    for asset in asset_report.get("assets", []):
        relative = asset.get("output_path", "")
        path = _safe_output(root, relative)
        if path is None or not path.is_file() or path.is_symlink():
            errors.append({"code": "MISSING_ASSET", "message": relative})
            continue
        digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != asset.get("source_sha256"):
            errors.append({"code": "ASSET_DIGEST", "message": relative})
    success_count = sum(item.get("status") == "success" for item in entries)
    if success_count != len(manifest) or success_count != build_report.get("summary", {}).get("html_success_count"):
        errors.append({"code": "SUCCESS_COUNT_MISMATCH", "message": f"entries={success_count} manifest={len(manifest)}"})
    node_ids: set[str] = set()
    node_by_id: dict[str, dict[str, Any]] = {}
    sibling_keys: set[tuple[str, str | None, int]] = set()
    sibling_orders: dict[tuple[str, str | None], list[int]] = defaultdict(list)
    source_orders: set[tuple[str, int]] = set()
    manifest_by_id = {item["entry_id"]: item for item in manifest}
    represented_navigation_paths: set[tuple[str, str]] = set()
    for node in navigation_nodes:
        node_id = node.get("navigation_node_id")
        source_id = node.get("source_entry_id")
        parent_id = node.get("parent_node_id")
        sibling_order = node.get("sibling_order")
        source_order = node.get("source_order")
        if node_id in node_ids:
            errors.append({"code": "DUPLICATE_NAVIGATION_NODE", "message": str(node_id)})
        node_ids.add(node_id)
        node_by_id[node_id] = node
        sibling_key = (str(source_id), parent_id, sibling_order)
        if sibling_key in sibling_keys:
            errors.append({"code": "DUPLICATE_NAVIGATION_SIBLING_ORDER", "message": str(sibling_key)})
        sibling_keys.add(sibling_key)
        sibling_orders[(str(source_id), parent_id)].append(sibling_order)
        source_order_key = (str(source_id), source_order)
        if source_order_key in source_orders:
            errors.append({"code": "DUPLICATE_NAVIGATION_SOURCE_ORDER", "message": str(source_order_key)})
        source_orders.add(source_order_key)
        target_id = node.get("target_entry_id")
        target_status = node.get("target_status")
        local = node.get("local")
        if target_status == "resolved-entry" and not target_id:
            errors.append({"code": "NAVIGATION_TARGET_STATUS", "message": str(node_id)})
        elif target_status == "no-local" and (local or target_id):
            errors.append({"code": "NAVIGATION_TARGET_STATUS", "message": str(node_id)})
        elif target_status == "target-not-found" and (not local or target_id):
            errors.append({"code": "NAVIGATION_TARGET_STATUS", "message": str(node_id)})
        elif target_status not in {
            "resolved-entry",
            "no-local",
            "target-not-found",
        }:
            errors.append({"code": "NAVIGATION_TARGET_STATUS", "message": str(node_id)})
        if target_id in manifest_by_id:
            path = node.get("navigation_path")
            represented_navigation_paths.add((target_id, path))
            if path not in manifest_by_id[target_id].get("navigation_paths", []):
                errors.append({"code": "NAVIGATION_PATH_MISMATCH", "message": str(node_id)})
    for node in navigation_nodes:
        parent_id = node.get("parent_node_id")
        if parent_id is None:
            continue
        parent = node_by_id.get(parent_id)
        if parent is None:
            errors.append({"code": "MISSING_NAVIGATION_PARENT", "message": str(node.get("navigation_node_id"))})
        elif node.get("depth") != parent.get("depth", 0) + 1:
            errors.append({"code": "NAVIGATION_DEPTH_MISMATCH", "message": str(node.get("navigation_node_id"))})
    for sibling_group, orders in sibling_orders.items():
        if sorted(orders) != list(range(len(orders))):
            errors.append({"code": "NAVIGATION_SIBLING_ORDER_GAP", "message": str(sibling_group)})
    for item in manifest:
        for navigation_path in item.get("navigation_paths", []):
            if (item["entry_id"], navigation_path) not in represented_navigation_paths:
                errors.append({"code": "NAVIGATION_OCCURRENCE_MISSING", "message": f"{item['entry_id']}: {navigation_path}"})
    navigation_summary = navigation_report.get("summary", {})
    if navigation_summary.get("navigation_node_count") != len(navigation_nodes):
        errors.append({"code": "NAVIGATION_NODE_COUNT", "message": str(navigation_summary)})
    return {
        "valid": not errors,
        "errors": errors,
        "summary": {
            "markdown_count": len(manifest),
            "asset_count": len(asset_report.get("assets", [])),
            "failed_count": build_report.get("summary", {}).get("html_failed_count"),
            "unresolved_count": build_report.get("summary", {}).get("unresolved_reference_count"),
        },
    }


def load_full_build_report(output: Path) -> dict[str, Any]:
    return json.loads((output.resolve(strict=True) / "reports" / "build-report.json").read_text(encoding="utf-8"))
