"""M1-C1 真实样本选择、转换、资产复制、报告与确定性验证。"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import shutil
import unicodedata
import uuid
from collections import Counter
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

from lorebuddy.ids import short_id

from .hhc_navigation import (
    extract_navigation_paths,
    extract_navigation_tree,
    navigation_key,
)
from .html_to_markdown import (
    MarkdownRenderer,
    collect_anchors,
    first_text,
    normalize_inline,
    parse_html,
    source_visible_segments,
)


ARTIFACT_ID = "urn:uuid:f1824e5e-bdc3-584b-a983-98335dbf1408"
BUILD_SCHEMA = "m1c1.sample-build@0.1.0"
SELECTIONS = (
    ("urn:uuid:5c782775-3372-520d-a8b9-45e3b415463d", ["encoding-conflict", "large-simple-table", "missing-title", "legacy-style"]),
    ("urn:uuid:993a9467-6938-53bb-9a63-462d01fe907f", ["long-body", "multi-level-headings", "lists", "tables"]),
    ("urn:uuid:6a7341e5-fd98-5433-b574-e7d645beec07", ["complex-tables", "large-row-count", "lists"]),
    ("urn:uuid:8b7af327-5530-572b-accd-683e7b8f238e", ["lists", "images", "headings", "tables"]),
    ("urn:uuid:8d4e8ddc-9e26-585b-8a91-12efb3064040", ["long-body", "internal-links", "page-anchors", "tables"]),
    ("urn:uuid:107cca4c-1763-5295-92b8-3619abd11b9e", ["same-name-different-content", "noise-cleaning", "simple-table"]),
    ("urn:uuid:39f56ef5-2fec-5e07-875a-1711c3f37326", ["same-name-different-content", "long-body", "tables"]),
    ("urn:uuid:40015881-c61a-51a0-9513-81a349098173", ["navigation-index", "nonstandard-html", "internal-links"]),
    ("urn:uuid:d04d55e1-60cf-5cc2-afdc-af4b3705a846", ["selected-cross-page-link-target", "long-body", "tables"]),
    ("urn:uuid:6441be68-e2ba-514c-8cd0-36c03d0ea462", ["rowspan-colspan-table", "minimal-html-fallback"]),
)


class M1C1Error(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical(value))


def _load_inventory(artifact_dir: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with (artifact_dir / "inventory" / "entries.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            entries.append(json.loads(line))
    return entries


def _decode(record: dict[str, Any], raw: bytes) -> tuple[str, str, list[str]]:
    extension = record["extensions"]["m1b-acquisition"]
    declared = extension.get("declared_encoding")
    candidate = extension.get("detected_encoding_candidate")
    attempts: list[str] = []
    preferred = [candidate, declared, "gb18030", "utf-8"]
    aliases = {"gb2312": "gb18030", "gbk": "gb18030", "utf-8-sig": "utf-8-sig"}
    for encoding in preferred:
        if not encoding:
            continue
        selected = aliases.get(encoding.casefold(), encoding)
        if selected in attempts:
            continue
        attempts.append(selected)
        try:
            return raw.decode(selected, "strict"), selected, attempts
        except (LookupError, UnicodeDecodeError):
            continue
    raise M1C1Error(f"Entry 无法严格解码：{record['id']} attempts={attempts}")


def _readable_filename(title: str, entry_id: str) -> str:
    value = unicodedata.normalize("NFC", title).strip(" .")
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.") or "sample"
    while len(value.encode("utf-8")) > 80:
        value = value[:-1]
    return f"{value}--{short_id(entry_id)}.md"


def _path_key(value: str) -> str:
    return unicodedata.normalize("NFC", value.replace("\\", "/")).casefold()


class Resolver:
    def __init__(self, *, current: dict[str, Any], entries_by_path: dict[str, dict[str, Any]], selected_outputs: dict[str, str], selected_ids_by_path: dict[str, str], artifact_dir: Path, output_root: Path, anchors: set[str], target_anchors: dict[str, set[str]] | None = None) -> None:
        self.current = current
        self.entries_by_path = entries_by_path
        self.selected_outputs = selected_outputs
        self.selected_ids_by_path = selected_ids_by_path
        self.artifact_dir = artifact_dir
        self.output_root = output_root
        self.anchors = anchors
        self.target_anchors = target_anchors
        self.unresolved: list[dict[str, Any]] = []
        self.resolved_links: list[dict[str, Any]] = []
        self.assets: list[dict[str, Any]] = []
        self.image_reference_count = 0

    def _resolve_path(self, raw: str) -> tuple[str | None, str | None]:
        decoded = unquote(raw).replace("\\", "/")
        split = urlsplit(decoded)
        if split.scheme or decoded.startswith("//"):
            return None, split.fragment or None
        if not split.path:
            return self.current["original_path"], split.fragment or None
        path = split.path.lstrip("/")
        joined = posixpath.normpath(posixpath.join(posixpath.dirname(self.current["original_path"]), path))
        if joined == ".." or joined.startswith("../"):
            return None, split.fragment or None
        return joined, split.fragment or None

    def link(self, raw: str, label: str) -> str | None:
        raw = raw.strip()
        lower = raw.casefold()
        if lower.startswith(("http://", "https://", "mailto:")):
            self._resolved(raw, raw, "external")
            return raw
        if lower.startswith(("javascript:", "mk:@msitstore:", "ms-its:", "file:")):
            self._unresolved("link", raw, None, "unsupported-scheme")
            return None
        resolved, fragment = self._resolve_path(raw)
        if resolved is None:
            self._unresolved("link", raw, None, "path-escape-or-invalid")
            return None
        if _path_key(resolved) == _path_key(self.current["original_path"]):
            if fragment and fragment not in self.anchors:
                self._unresolved("anchor", raw, resolved, "missing-page-anchor")
                return None
            target = f"#{fragment}" if fragment else self.selected_outputs[self.current["id"]]
            self._resolved(raw, target, "same-page")
            return target
        key = _path_key(resolved)
        target_id = self.selected_ids_by_path.get(key)
        suffix = f"#{fragment}" if fragment else ""
        if target_id:
            if fragment and self.target_anchors is not None and fragment not in self.target_anchors.get(target_id, set()):
                self._unresolved("anchor", raw, resolved, "missing-target-anchor", target_id)
                return None
            target = self.selected_outputs[target_id] + suffix
            self._resolved(raw, target, "converted-page", target_id)
            return target
        target = self.entries_by_path.get(key)
        self._unresolved("link", raw, resolved, "target-not-selected" if target else "target-not-found", target["id"] if target else None)
        return None

    def image(self, raw: str, alt: str) -> str | None:
        self.image_reference_count += 1
        raw = raw.strip()
        if not raw or raw.casefold().startswith(("http://", "https://", "data:")):
            self._unresolved("image", raw, None, "external-or-empty-image")
            return None
        resolved, _ = self._resolve_path(raw)
        target = self.entries_by_path.get(_path_key(resolved)) if resolved else None
        if target is None:
            self._unresolved("image", raw, resolved, "asset-not-found")
            return None
        source = self.artifact_dir / "extracted" / target["storage_path"]
        if not source.is_file():
            self._unresolved("image", raw, resolved, "asset-bytes-missing", target["id"])
            return None
        basename = PurePosixPath(target["original_path"]).name
        safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", unicodedata.normalize("NFC", basename)).strip(" .") or "asset.bin"
        relative = Path(short_id(target["id"])) / safe
        destination = self.output_root / "assets" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if hashlib.sha256(destination.read_bytes()).digest() != hashlib.sha256(source.read_bytes()).digest():
                raise M1C1Error(f"资产输出碰撞：{relative}")
        else:
            shutil.copyfile(source, destination, follow_symlinks=False)
        item = {"entry_id": target["id"], "source_path": target["original_path"], "source_sha256": target["digest"], "output_path": f"assets/{relative.as_posix()}"}
        if item not in self.assets:
            self.assets.append(item)
        return f"../assets/{relative.as_posix()}"

    def _unresolved(self, kind: str, raw: str, resolved: str | None, reason: str, target_entry_id: str | None = None) -> None:
        self.unresolved.append({"source_entry_id": self.current["id"], "kind": kind, "raw_target": raw, "resolved_source_path": resolved, "target_entry_id": target_entry_id, "reason": reason})

    def _resolved(self, raw: str, target: str, resolution: str, target_entry_id: str | None = None) -> None:
        self.resolved_links.append({"source_entry_id": self.current["id"], "raw_target": raw, "output_target": target, "target_entry_id": target_entry_id, "resolution": resolution})


def _retention_ratio(segments: list[str], markdown: str) -> float:
    significant = [segment for segment in segments if len(re.sub(r"\s+", "", segment)) >= 2]
    total = sum(len(re.sub(r"\s+", "", segment)) for segment in significant)
    if total == 0:
        return 1.0
    retained = sum(len(re.sub(r"\s+", "", segment)) for segment in significant if segment in markdown)
    return round(retained / total, 6)


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _load_navigation(
    artifact_dir: Path,
    entries: list[dict[str, Any]],
) -> tuple[
    dict[str, list[str]],
    list[dict[str, str]],
    list[dict[str, Any]],
]:
    paths: dict[str, list[str]] = {}
    sources: list[dict[str, str]] = []
    nodes: list[dict[str, Any]] = []
    entries_by_path = {
        navigation_key(entry["original_path"]): entry for entry in entries
    }
    hhc_entries = sorted((entry for entry in entries if PurePosixPath(entry["original_path"]).suffix.casefold() == ".hhc"), key=lambda entry: entry["original_path"])
    for record in hhc_entries:
        raw = (artifact_dir / "extracted" / record["storage_path"]).read_bytes()
        text, _, _ = _decode(record, raw)
        for key, breadcrumbs in extract_navigation_paths(text).items():
            target = paths.setdefault(key, [])
            target.extend(path for path in breadcrumbs if path not in target)
        for node in extract_navigation_tree(text, source_entry_id=record["id"]):
            local = node["local"]
            target = entries_by_path.get(navigation_key(local)) if local else None
            nodes.append(
                {
                    **node,
                    "target_entry_id": target["id"] if target else None,
                    "target_status": (
                        "resolved-entry"
                        if target
                        else "no-local"
                        if not local
                        else "target-not-found"
                    ),
                }
            )
        sources.append({"entry_id": record["id"], "source_path": record["original_path"], "source_sha256": record["digest"]})
    return paths, sources, nodes


def _build_in_owned_dir(artifact_dir: Path, target: Path) -> dict[str, Any]:
    entries = _load_inventory(artifact_dir)
    by_id = {entry["id"]: entry for entry in entries}
    by_path = {_path_key(entry["original_path"]): entry for entry in entries}
    navigation_by_path, navigation_sources, _ = _load_navigation(
        artifact_dir, entries
    )
    selections: list[dict[str, Any]] = []
    parsed: dict[str, tuple[Any, str, str, list[str]]] = {}
    for entry_id, reasons in SELECTIONS:
        record = by_id.get(entry_id)
        if record is None:
            raise M1C1Error(f"选择的 Entry 不存在：{entry_id}")
        raw = (artifact_dir / "extracted" / record["storage_path"]).read_bytes()
        text, used_encoding, attempts = _decode(record, raw)
        tree = parse_html(text)
        title = first_text(tree, "title") or first_text(tree, "h1") or first_text(tree, "h2") or PurePosixPath(record["original_path"]).stem
        output = _readable_filename(title, entry_id)
        selections.append({"entry_id": entry_id, "source_path": record["original_path"], "navigation_paths": navigation_by_path.get(navigation_key(record["original_path"]), []), "source_sha256": record["digest"], "title": title, "output_path": f"markdown/{output}", "reasons": reasons})
        parsed[entry_id] = (tree, title, used_encoding, attempts)
    outputs = {item["entry_id"]: PurePosixPath(item["output_path"]).name for item in selections}
    selected_ids_by_path = {_path_key(item["source_path"]): item["entry_id"] for item in selections}
    all_unresolved: list[dict[str, Any]] = []
    all_assets: list[dict[str, Any]] = []
    conversions: list[dict[str, Any]] = []
    encodings: list[dict[str, Any]] = []
    for item in selections:
        record = by_id[item["entry_id"]]
        tree, title, used_encoding, attempts = parsed[item["entry_id"]]
        resolver = Resolver(current=record, entries_by_path=by_path, selected_outputs=outputs, selected_ids_by_path=selected_ids_by_path, artifact_dir=artifact_dir, output_root=target, anchors=collect_anchors(tree))
        renderer = MarkdownRenderer(link_callback=resolver.link, image_callback=resolver.image)
        body = renderer.render(tree)
        navigation_lines = (["navigation_paths:"] + [f"  - {_yaml_string(path)}" for path in item["navigation_paths"]]) if item["navigation_paths"] else ["navigation_paths: []"]
        front_matter = "\n".join([
            "---",
            f"artifact_id: {_yaml_string(ARTIFACT_ID)}",
            f"entry_id: {_yaml_string(record['id'])}",
            f"source_path: {_yaml_string(record['original_path'])}",
            *navigation_lines,
            f"source_sha256: {_yaml_string(record['digest'])}",
            f"detected_encoding: {_yaml_string(used_encoding)}",
            "---",
            "",
        ])
        markdown = front_matter + f"# {title}\n\n" + body
        output_path = target / item["output_path"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8", newline="\n")
        segments = source_visible_segments(tree)
        conversions.append({
            "entry_id": record["id"], "title": title, "source_path": record["original_path"], "navigation_paths": item["navigation_paths"],
            "output_path": item["output_path"], "source_bytes": record["size"], "markdown_bytes": len(markdown.encode("utf-8")),
            "source_visible_segments": len(segments), "retained_visible_text_ratio": _retention_ratio(segments, markdown),
            "stats": asdict(renderer.stats), "asset_count": len(resolver.assets), "unresolved_count": len(resolver.unresolved),
        })
        extension = record["extensions"]["m1b-acquisition"]
        encodings.append({
            "entry_id": record["id"], "declared_encoding": extension.get("declared_encoding"),
            "detected_candidate": extension.get("detected_encoding_candidate"), "encoding_conflict": extension.get("encoding_conflict"),
            "used_encoding": used_encoding, "strict_decode_attempts": attempts, "status": "decoded",
        })
        all_unresolved.extend(resolver.unresolved)
        all_assets.extend(resolver.assets)
    selections.sort(key=lambda item: item["entry_id"])
    conversions.sort(key=lambda item: item["entry_id"])
    encodings.sort(key=lambda item: item["entry_id"])
    all_unresolved.sort(key=lambda item: (item["source_entry_id"], item["kind"], item["raw_target"], item["reason"]))
    unique_assets = {asset["entry_id"]: asset for asset in all_assets}
    assets = [unique_assets[key] for key in sorted(unique_assets)]
    _write_json(target / "sample-selection.json", {"schema": "m1c1.sample-selection@0.1.0", "artifact_id": ARTIFACT_ID, "navigation_sources": navigation_sources, "sample_count": len(selections), "samples": selections})
    _write_json(target / "reports" / "conversion-report.json", {"schema": "m1c1.conversion-report@0.1.0", "artifact_id": ARTIFACT_ID, "samples": conversions, "assets": assets, "summary": {"sample_count": len(conversions), "asset_count": len(assets), "unresolved_count": len(all_unresolved), "markdown_tables": sum(item["stats"]["markdown_tables"] for item in conversions), "html_tables": sum(item["stats"]["html_tables"] for item in conversions)}})
    _write_json(target / "reports" / "encoding-report.json", {"schema": "m1c1.encoding-report@0.1.0", "entries": encodings, "summary": {"decoded": len(encodings), "conflicts": sum(item["encoding_conflict"] is True for item in encodings)}})
    _write_json(target / "reports" / "unresolved-links.json", {"schema": "m1c1.unresolved-links@0.1.0", "items": all_unresolved, "summary": dict(sorted(Counter(item["reason"] for item in all_unresolved).items()))})
    _write_readme(target, selections, conversions, assets, all_unresolved)
    _write_fidelity_review(target, conversions)
    return validate_sample_build(target)


def _write_readme(target: Path, selections: list[dict[str, Any]], conversions: list[dict[str, Any]], assets: list[dict[str, Any]], unresolved: list[dict[str, Any]]) -> None:
    conversion_by_id = {item["entry_id"]: item for item in conversions}
    lines = ["# LoreBuddy M1-C1 真实 Markdown 样本", "", f"Artifact ID：`{ARTIFACT_ID}`", "", "本目录是可重建的验证产物，不是 Knowledge Node、Library 或 Obsidian 发布视图。", "", "Source Path 是 M1-B Inventory 逐字符保存的物理 CHM Entry 路径，也是相对链接解析基准。Navigation Path 来自 HHC 的 Name 层级，仅表示目录导航，不替代 Source Path。", "", "## 样本", ""]
    for sample in selections:
        report = conversion_by_id[sample["entry_id"]]
        navigation = "；".join(f"`{path}`" for path in sample["navigation_paths"]) or "`unknown`"
        lines.append(f"- [{sample['title']}]({sample['output_path']}) — Source Path：`{sample['source_path']}`；Navigation Path：{navigation}；{', '.join(sample['reasons'])}；文本保留率 `{report['retained_visible_text_ratio']:.3f}`")
    lines.extend(["", "## 汇总", "", f"- Markdown：{len(selections)}", f"- Assets：{len(assets)}", f"- Unresolved：{len(unresolved)}", "- 所有 Markdown 使用 UTF-8 和 LF。", "- 未转换目标不会生成伪链接，详见 `reports/unresolved-links.json`。", ""])
    (target / "README.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _write_fidelity_review(target: Path, conversions: list[dict[str, Any]]) -> None:
    lines = ["# M1-C1 Fidelity Review", "", "该报告用于人工验收，不声称 Full Fidelity Coverage Map。自动文本保留率只检查可见文本片段是否仍出现在 Markdown 中，不能替代逐页阅读。", "", "## 路径语义", "", "`source_path` 是 M1-B Inventory 逐字符保存的物理 CHM Entry 路径，也是相对链接解析基准。`navigation_paths` 来自 HHC 的 `Name` 层级；它不替代或改写 `source_path`。", "", "| Entry ID | 标题 | Source Path | Navigation Path |", "|---|---|---|---|"]
    for item in conversions:
        navigation = "<br>".join(path.replace("|", "\\|") for path in item["navigation_paths"]) or "unknown"
        lines.append(f"| `{item['entry_id']}` | {item['title'].replace('|', '\\|')} | `{item['source_path'].replace('|', '\\|')}` | {navigation} |")
    lines.extend(["", "## 自动结果", "", "| Entry ID | 标题 | 文本保留率 | Markdown Table | HTML Table | 图片 | Unresolved |", "|---|---|---:|---:|---:|---:|---:|"])
    for item in conversions:
        stats = item["stats"]
        lines.append(f"| `{item['entry_id']}` | {item['title'].replace('|', '\\|')} | {item['retained_visible_text_ratio']:.3f} | {stats['markdown_tables']} | {stats['html_tables']} | {item['asset_count']} | {item['unresolved_count']} |")
    lines.extend(["", "## 人工检查清单", "", "- [ ] 标题和标题层级可读且未改写。", "- [ ] 正文、列表和规则文本未总结、意译或静默丢失。", "- [ ] Markdown 表格列对应正确。", "- [ ] 保留的 HTML 表格在普通 Markdown 阅读器中可读。", "- [ ] 图片路径有效且内容正确。", "- [ ] 已映射链接和页面内锚点可用。", "- [ ] unresolved 项没有被伪造成有效链接。", "- [ ] 编码冲突页面没有乱码。", "- [ ] script、style 和明显导航噪声已移除。", ""])
    (target / "reports" / "fidelity-review.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build_samples(artifact_dir: Path, output: Path) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve(strict=True)
    artifact = json.loads((artifact_dir / "inventory" / "artifact.json").read_text(encoding="utf-8"))
    if artifact.get("id") != ARTIFACT_ID:
        raise M1C1Error(f"Artifact ID 不匹配：{artifact.get('id')}")
    output = output.resolve()
    marker = output / ".lorebuddy-m1c1.json"
    if output.exists():
        if not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")) != {"schema": BUILD_SCHEMA, "artifact_id": ARTIFACT_ID}:
            raise M1C1Error(f"拒绝替换非 LoreBuddy M1-C1 owned 目录：{output}")
    temporary = output.with_name(f".{output.name}.building")
    if temporary.exists():
        temp_marker = temporary / ".lorebuddy-m1c1.json"
        if not temp_marker.is_file():
            raise M1C1Error(f"拒绝清理未知临时目录：{temporary}")
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    _write_json(temporary / ".lorebuddy-m1c1.json", {"schema": BUILD_SCHEMA, "artifact_id": ARTIFACT_ID})
    try:
        result = _build_in_owned_dir(artifact_dir, temporary)
        if not result["valid"]:
            raise M1C1Error(f"样本构建验证失败：{result['errors'][:3]}")
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
        return validate_sample_build(output)
    except Exception:
        raise


def validate_sample_build(output: Path) -> dict[str, Any]:
    root = output.resolve(strict=True)
    errors: list[dict[str, str]] = []
    required = ["README.md", "sample-selection.json", "reports/conversion-report.json", "reports/encoding-report.json", "reports/unresolved-links.json", "reports/fidelity-review.md"]
    for relative in required:
        if not (root / relative).is_file():
            errors.append({"code": "MISSING_FILE", "message": relative})
    try:
        selection = json.loads((root / "sample-selection.json").read_text(encoding="utf-8"))
        conversion = json.loads((root / "reports" / "conversion-report.json").read_text(encoding="utf-8"))
        unresolved = json.loads((root / "reports" / "unresolved-links.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": errors + [{"code": "LOAD_ERROR", "message": str(exc)}]}
    samples = selection.get("samples", [])
    if not 5 <= len(samples) <= 10:
        errors.append({"code": "SAMPLE_COUNT", "message": str(len(samples))})
    output_paths: set[str] = set()
    for sample in samples:
        relative = sample.get("output_path", "")
        if relative in output_paths:
            errors.append({"code": "DUPLICATE_OUTPUT", "message": relative})
        output_paths.add(relative)
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append({"code": "MISSING_MARKDOWN", "message": relative})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append({"code": "NOT_UTF8", "message": f"{relative}: {exc}"})
            continue
        for field in ("artifact_id:", "entry_id:", "source_path:", "navigation_paths:", "source_sha256:", "detected_encoding:"):
            if field not in text[:1200]:
                errors.append({"code": "MISSING_METADATA", "message": f"{relative}: {field}"})
        try:
            metadata = yaml.safe_load(text.split("---", 2)[1])
        except (IndexError, yaml.YAMLError) as exc:
            errors.append({"code": "INVALID_METADATA", "message": f"{relative}: {exc}"})
            continue
        if metadata.get("source_path") != sample.get("source_path"):
            errors.append({"code": "SOURCE_PATH_SEMANTICS", "message": relative})
        if metadata.get("navigation_paths") != sample.get("navigation_paths"):
            errors.append({"code": "NAVIGATION_PATH_SEMANTICS", "message": relative})
    for asset in conversion.get("assets", []):
        path = (root / asset.get("output_path", "")).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append({"code": "MISSING_ASSET", "message": asset.get("output_path", "")})
            continue
        digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != asset.get("source_sha256"):
            errors.append({"code": "ASSET_DIGEST", "message": asset.get("output_path", "")})
    if conversion.get("summary", {}).get("unresolved_count") != len(unresolved.get("items", [])):
        errors.append({"code": "UNRESOLVED_COUNT", "message": "汇总不一致"})
    return {"valid": not errors, "errors": errors, "summary": {"sample_count": len(samples), "asset_count": len(conversion.get("assets", [])), "unresolved_count": len(unresolved.get("items", []))}}
