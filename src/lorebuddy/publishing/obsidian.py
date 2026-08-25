"""M1-C3 Obsidian Baseline Publisher。

Publisher 只消费显式传入且通过 M1-C2A Validator 的 Build Root。它不读取
CHM、Acquisition、Vault 配置或当前工作目录中的隐式状态。
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

from lorebuddy.samples.full_build import validate_full_build


PUBLISHER_PROFILE = "m1c3.obsidian-baseline@0.1.0"
MARKER = {"schema": PUBLISHER_PROFILE, "publisher_version": "0.1.0"}
REPORT_FILES = (
    "entries.jsonl",
    "build-report.json",
    "encoding-report.json",
    "fidelity-report.json",
    "link-report.json",
    "asset-report.json",
    "navigation-report.json",
    "navigation-tree.jsonl",
)
PRIVATE_PATH_PATTERN = re.compile(r"(?:/Users/[^/\s]+/|/home/[^/\s]+/)")
MARKDOWN_REFERENCE = re.compile(
    r"(?P<image>!)?\[(?P<label>[^\]]*)\]\("
    r"(?P<target><[^>\n]+>|(?:[^()\n]|\([^()\n]*\))+)\)"
)
HTML_HREF = re.compile(
    r"(?P<prefix><a\b[^>]*\bhref=[\"'])(?P<target>[^\"']+)(?P<suffix>[\"'])",
    re.IGNORECASE,
)
HTML_IMAGE = re.compile(
    r"(?P<prefix><img\b[^>]*\bsrc=[\"'])(?P<target>[^\"']+)(?P<suffix>[\"'])",
    re.IGNORECASE,
)
WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)


class ObsidianPublisherError(RuntimeError):
    """M1-C3 发布输入或输出违反边界。"""


@dataclass(slots=True)
class PublisherInput:
    root: Path
    artifact_id: str
    manifest: list[dict[str, Any]]
    assets: list[dict[str, Any]]
    resolved_links: list[dict[str, Any]]
    unresolved_links: list[dict[str, Any]]
    entries_by_id: dict[str, dict[str, Any]]
    navigation_nodes: list[dict[str, Any]]


def _canonical(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def _jsonl(records: list[dict[str, Any]]) -> bytes:
    return b"".join(_canonical(record) for record in records)


def _safe_path(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts:
        raise ObsidianPublisherError(f"非法相对路径：{relative!r}")
    path = (root / pure).resolve()
    if not path.is_relative_to(root):
        raise ObsidianPublisherError(f"路径逃逸：{relative!r}")
    return path


def _read_input_file(root: Path, relative: str) -> bytes:
    path = _safe_path(root, relative)
    if not path.is_file() or path.is_symlink():
        raise ObsidianPublisherError(f"输入文件缺失或不是普通文件：{relative}")
    return path.read_bytes()


def _load_input(build_root: Path) -> PublisherInput:
    root = build_root.resolve(strict=True)
    validation = validate_full_build(root)
    if not validation["valid"]:
        raise ObsidianPublisherError(
            f"M1-C2A Build Root 未通过 Validator：{validation['errors'][:3]}"
        )
    for relative in (
        ".lorebuddy-m1c2a.json",
        "markdown-manifest.jsonl",
        *(f"reports/{name}" for name in REPORT_FILES),
    ):
        _read_input_file(root, relative)
    marker = json.loads(_read_input_file(root, ".lorebuddy-m1c2a.json"))
    artifact_id = marker.get("artifact_id")
    if not isinstance(artifact_id, str) or not artifact_id:
        raise ObsidianPublisherError("M1-C2A Marker 缺少 Artifact ID")
    manifest = _load_jsonl(root / "markdown-manifest.jsonl")
    asset_report = json.loads(_read_input_file(root, "reports/asset-report.json"))
    link_report = json.loads(_read_input_file(root, "reports/link-report.json"))
    entries = _load_jsonl(root / "reports/entries.jsonl")
    navigation_nodes = _load_jsonl(root / "reports/navigation-tree.jsonl")
    entries_by_id = {
        entry["entry_id"]: entry
        for entry in entries
        if entry.get("status") == "success"
    }
    if len(entries_by_id) != len(manifest):
        raise ObsidianPublisherError("Entries Report 与 Manifest 不闭合")
    for item in manifest:
        if item.get("entry_id") not in entries_by_id:
            raise ObsidianPublisherError(
                f"Manifest Entry 缺少成功报告：{item.get('entry_id')}"
            )
        _read_input_file(root, item["output_path"])
    for asset in asset_report.get("assets", []):
        _read_input_file(root, asset["output_path"])
    return PublisherInput(
        root=root,
        artifact_id=artifact_id,
        manifest=manifest,
        assets=asset_report.get("assets", []),
        resolved_links=link_report.get("resolved", []),
        unresolved_links=link_report.get("unresolved", []),
        entries_by_id=entries_by_id,
        navigation_nodes=navigation_nodes,
    )


def _display_filename(label: str, namespace: str) -> str:
    value = unicodedata.normalize("NFC", label).strip(" .")
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.") or "未分类"
    while len(value.encode("utf-8")) > 80:
        value = value[:-1]
    suffix = hashlib.sha256(namespace.encode("utf-8")).hexdigest()[:8]
    return f"{value}--{suffix}.md"


def _safe_note_component(display: str, *, fallback: str) -> str:
    value = unicodedata.normalize("NFC", display).strip(" .")
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"-+", "-", value).strip("-.") or "note"
    if value.casefold() in WINDOWS_RESERVED:
        value = f"{value} note"
    while len(value.encode("utf-8")) > 80:
        value = value[:-1]
    return value or fallback


def _preferred_note_path(raw_parts: list[str], title: str) -> str:
    if raw_parts:
        parts = [
            _safe_note_component(part, fallback=f"level-{position + 1}")
            for position, part in enumerate(raw_parts)
        ]
    else:
        parts = ["_Unclassified", _safe_note_component(title, fallback="note")]
    return PurePosixPath("Notes", *parts[:-1], f"{parts[-1]}.md").as_posix()


def _note_path_key(path: str) -> str:
    return unicodedata.normalize("NFC", path).casefold()


def _navigation_match_key(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _navigation_affinity(
    titles: list[str],
    source_path: str,
) -> tuple[int, int, int]:
    """衡量 HHC 路径与物理 Source Path 的结构亲和度。"""

    source = PurePosixPath(source_path)
    source_parts = [*source.parts[:-1], source.stem]
    navigation_keys = [
        key for title in titles if (key := _navigation_match_key(title))
    ]
    source_keys = [
        key for part in source_parts if (key := _navigation_match_key(part))
    ]
    navigation_counts = Counter(navigation_keys)
    source_counts = Counter(source_keys)
    exact_matches = sum(
        min(count, source_counts.get(key, 0))
        for key, count in navigation_counts.items()
    )
    partial_matches = sum(
        1
        for navigation_key in navigation_keys
        for source_key in source_keys
        if navigation_key != source_key
        and min(len(navigation_key), len(source_key)) >= 2
        and (
            navigation_key in source_key
            or source_key in navigation_key
        )
    )
    length_proximity = -abs(len(navigation_keys) - len(source_keys))
    return exact_matches, partial_matches, length_proximity


def _plan_note_paths(source: PublisherInput) -> tuple[dict[str, str], int, int]:
    """选择最贴近 Source Path 的 HHC 路径，仅在碰撞时追加稳定短 ID。"""

    nodes_by_id = {
        node["navigation_node_id"]: node for node in source.navigation_nodes
    }
    occurrences_by_entry: dict[str, list[tuple[list[str], str, int]]] = (
        defaultdict(list)
    )
    for node in sorted(
        source.navigation_nodes,
        key=lambda item: (item["source_entry_id"], item["source_order"]),
    ):
        entry_id = node.get("target_entry_id")
        if entry_id not in source.entries_by_id:
            continue
        ancestry: list[str] = []
        current: dict[str, Any] | None = node
        visited: set[str] = set()
        while current is not None:
            node_id = current["navigation_node_id"]
            if node_id in visited:
                raise ObsidianPublisherError(f"Navigation Tree 存在循环：{node_id}")
            visited.add(node_id)
            ancestry.append(current["title"])
            parent_id = current.get("parent_node_id")
            current = nodes_by_id.get(parent_id) if parent_id else None
        occurrences_by_entry[entry_id].append(
            (
                list(reversed(ancestry)),
                node["source_entry_id"],
                node["source_order"],
            )
        )

    candidates: dict[str, list[tuple[str, str]]] = defaultdict(list)
    unclassified_count = 0
    for item in source.manifest:
        entry_id = item["entry_id"]
        title = source.entries_by_id[entry_id].get("title") or PurePosixPath(
            item["output_path"]
        ).stem
        occurrences = occurrences_by_entry.get(entry_id, [])
        raw_parts: list[str] = []
        if occurrences:
            scores = [
                _navigation_affinity(parts, item["source_path"])
                for parts, _, _ in occurrences
            ]
            best_score = max(scores)
            raw_parts = min(
                (
                    occurrence
                    for occurrence, score in zip(occurrences, scores)
                    if score == best_score
                ),
                key=lambda value: (value[1], value[2]),
            )[0]
        preferred = _preferred_note_path(raw_parts, title)
        candidates[_note_path_key(preferred)].append((entry_id, preferred))
        if not (item.get("navigation_paths") or []):
            unclassified_count += 1

    planned: dict[str, str] = {}
    collision_count = 0
    output_keys: set[str] = set()
    for key in sorted(candidates):
        group = sorted(candidates[key])
        collided = len(group) > 1
        collision_count += len(group) if collided else 0
        for entry_id, preferred in group:
            output = preferred
            if collided:
                path = PurePosixPath(preferred)
                short_id = entry_id.removeprefix("urn:uuid:").replace("-", "")[:8]
                output = path.with_name(f"{path.stem}--{short_id}.md").as_posix()
            output_key = _note_path_key(output)
            if output_key in output_keys:
                raise ObsidianPublisherError(f"Note 输出路径无法确定性消歧：{output}")
            output_keys.add(output_key)
            planned[entry_id] = output
    return planned, collision_count, unclassified_count


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _relative_target(from_path: str, to_path: str, fragment: str | None = None) -> str:
    source_parent = PurePosixPath(from_path).parent
    target = os.path.relpath(
        PurePosixPath(to_path).as_posix(), source_parent.as_posix()
    ).replace("\\", "/")
    return target + (f"#{fragment}" if fragment else "")


def _split_target(value: str) -> tuple[str, str, str | None]:
    stripped = value.strip()
    if stripped.startswith("<") and ">" in stripped:
        end = stripped.index(">")
        path = stripped[1:end]
        suffix = stripped[end + 1 :]
        return "<", path, suffix
    return "", stripped, None


def _markdown_destination(path: str) -> str:
    return f"<{path}>" if any(character in path for character in " ()") else path


def _input_reference_path(note_input: str, target: str) -> str | None:
    split = urlsplit(unquote(target))
    if split.scheme or target.startswith("//") or not split.path:
        return None
    joined = (
        PurePosixPath(note_input).parent / PurePosixPath(split.path)
    )
    normalized = PurePosixPath(os.path.normpath(joined.as_posix()))
    if normalized.is_absolute() or ".." in normalized.parts:
        return None
    return normalized.as_posix()


def _rewrite_note(
    text: str,
    *,
    entry_id: str,
    input_path: str,
    output_path: str,
    note_by_id: dict[str, str],
    resolved_by_source: dict[str, dict[str, dict[str, Any]]],
    asset_outputs: dict[str, str],
) -> tuple[str, dict[str, int]]:
    stats: Counter[str] = Counter()
    source_links = resolved_by_source.get(entry_id, {})

    def rewrite_markdown(match: re.Match[str]) -> str:
        _, target, _ = _split_target(match.group("target"))
        split = urlsplit(unquote(target))
        if match.group("image"):
            input_asset = _input_reference_path(input_path, target)
            projected = asset_outputs.get(input_asset or "")
            if projected:
                target = _relative_target(output_path, projected)
                stats["image_rewritten"] += 1
        elif not split.scheme and not target.startswith("//"):
            link = source_links.get(target)
            if link and link.get("target_entry_id") in note_by_id:
                target = _relative_target(
                    output_path,
                    note_by_id[link["target_entry_id"]],
                    split.fragment or None,
                )
                stats["internal_link_rewritten"] += 1
            elif link and link.get("resolution") == "same-page":
                if not target.startswith("#"):
                    target = _relative_target(
                        output_path,
                        note_by_id[entry_id],
                        split.fragment or None,
                    )
                stats["internal_link_rewritten"] += 1
            elif target.startswith("#"):
                stats["same_page_anchor_preserved"] += 1
        return (
            ("!" if match.group("image") else "")
            + f"[{match.group('label')}]"
            + f"({_markdown_destination(target)})"
        )

    text = MARKDOWN_REFERENCE.sub(rewrite_markdown, text)

    def rewrite_html_link(match: re.Match[str]) -> str:
        target = html.unescape(match.group("target"))
        split = urlsplit(unquote(target))
        link = source_links.get(target)
        if link and link.get("target_entry_id") in note_by_id:
            target = _relative_target(
                output_path,
                note_by_id[link["target_entry_id"]],
                split.fragment or None,
            )
            stats["internal_link_rewritten"] += 1
        elif target.startswith("#"):
            stats["same_page_anchor_preserved"] += 1
        return (
            match.group("prefix")
            + html.escape(target, quote=True)
            + match.group("suffix")
        )

    def rewrite_html_image(match: re.Match[str]) -> str:
        target = html.unescape(match.group("target"))
        input_asset = _input_reference_path(input_path, target)
        projected = asset_outputs.get(input_asset or "")
        if projected:
            target = _relative_target(output_path, projected)
            stats["image_rewritten"] += 1
        return (
            match.group("prefix")
            + html.escape(target, quote=True)
            + match.group("suffix")
        )

    text = HTML_HREF.sub(rewrite_html_link, text)
    text = HTML_IMAGE.sub(rewrite_html_image, text)
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ObsidianPublisherError(f"输入 Note 缺少 Front Matter：{input_path}")
    publisher_fields = (
        f'publisher_profile: "{PUBLISHER_PROFILE}"\n'
        'publisher_release: "baseline"\n'
        f'publisher_note_path: "{output_path}"\n'
    )
    text = "---" + parts[1].rstrip() + "\n" + publisher_fields + "---" + parts[2]
    return text, dict(stats)


def _navigation_files(
    source: PublisherInput,
    note_by_id: dict[str, str],
) -> tuple[dict[str, bytes], list[dict[str, str]], dict[str, int]]:
    """把完整 HHC 节点树投影为多层目录索引，不复制正文。"""

    nodes = source.navigation_nodes
    by_id = {node["navigation_node_id"]: node for node in nodes}
    children: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        children[node.get("parent_node_id")].append(node)
    for values in children.values():
        values.sort(
            key=lambda item: (
                item["source_entry_id"],
                item["sibling_order"],
                item["source_order"],
                item["navigation_node_id"],
            )
        )

    component_by_id: dict[str, str] = {}
    for parent_id, siblings in children.items():
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for node in siblings:
            component = _safe_note_component(node["title"], fallback="navigation")
            grouped[_note_path_key(component)].append(node)
        for group in grouped.values():
            collided = len(group) > 1
            for node in group:
                component = _safe_note_component(
                    node["title"], fallback="navigation"
                )
                if collided:
                    short = (
                        node["navigation_node_id"]
                        .removeprefix("urn:uuid:")
                        .replace("-", "")[:8]
                    )
                    component = f"{component}--{short}"
                component_by_id[node["navigation_node_id"]] = component

    path_parts_by_id: dict[str, list[str]] = {}

    def path_parts(node: dict[str, Any]) -> list[str]:
        node_id = node["navigation_node_id"]
        existing = path_parts_by_id.get(node_id)
        if existing is not None:
            return existing
        parent_id = node.get("parent_node_id")
        parts = (
            path_parts(by_id[parent_id])
            if parent_id is not None and parent_id in by_id
            else []
        )
        result = [*parts, component_by_id[node_id]]
        path_parts_by_id[node_id] = result
        return result

    index_by_node: dict[str, str] = {}
    for node in nodes:
        node_id = node["navigation_node_id"]
        if (
            children.get(node_id)
            or node.get("target_entry_id") not in note_by_id
            or node.get("parent_node_id") is None
        ):
            index_by_node[node_id] = PurePosixPath(
                "Books", *path_parts(node), "_目录.md"
            ).as_posix()

    files: dict[str, bytes] = {}
    indexes: list[dict[str, str]] = []
    for node in nodes:
        node_id = node["navigation_node_id"]
        output = index_by_node.get(node_id)
        if output is None:
            continue
        lines = [
            "---",
            f'publisher_profile: "{PUBLISHER_PROFILE}"',
            'publisher_file_type: "navigation-index"',
            f'navigation_node_id: "{node_id}"',
            f"navigation_source_order: {node['source_order']}",
            "---",
            f"# {node['title']}",
            "",
        ]
        target_entry_id = node.get("target_entry_id")
        if target_entry_id in note_by_id:
            target = _relative_target(output, note_by_id[target_entry_id])
            lines.extend([f"- [本节正文]({target})", ""])
        elif node.get("local"):
            lines.extend(
                [
                    f"- Source Local 未解析：`{node['local']}`",
                    "",
                ]
            )
        if children.get(node_id):
            lines.extend(["## 子项", ""])
        for child in children.get(node_id, []):
            child_id = child["navigation_node_id"]
            child_target_id = child.get("target_entry_id")
            child_index = index_by_node.get(child_id)
            label = _escape_label(child["title"])
            if child_target_id in note_by_id:
                body_target = _relative_target(output, note_by_id[child_target_id])
                if child_index:
                    directory_target = _relative_target(output, child_index)
                    lines.append(
                        f"- [{label}]({body_target}) · [目录]({directory_target})"
                    )
                else:
                    lines.append(f"- [{label}]({body_target})")
            elif child_index:
                directory_target = _relative_target(output, child_index)
                suffix = "（Source Local 未解析）" if child.get("local") else ""
                lines.append(f"- [{label}]({directory_target}){suffix}")
            else:
                lines.append(f"- {label}")
        files[output] = ("\n".join(lines).rstrip() + "\n").encode("utf-8")
        indexes.append(
            {
                "title": node["title"],
                "output_path": output,
                "navigation_node_id": node_id,
            }
        )

    roots = children.get(None, [])
    home_indexes = [
        {
            "title": node["title"],
            "output_path": (
                index_by_node[node["navigation_node_id"]]
                if node["navigation_node_id"] in index_by_node
                else note_by_id[node["target_entry_id"]]
            ),
        }
        for node in roots
        if node["navigation_node_id"] in index_by_node
        or node.get("target_entry_id") in note_by_id
    ]
    unclassified_ids = sorted(
        item["entry_id"]
        for item in source.manifest
        if not (item.get("navigation_paths") or [])
    )
    if unclassified_ids:
        output = "Books/_Unclassified/_目录.md"
        lines = [
            "---",
            f'publisher_profile: "{PUBLISHER_PROFILE}"',
            'publisher_file_type: "navigation-index"',
            "navigation_node_id: null",
            'generated_navigation_kind: "unclassified"',
            "---",
            "# 无 HHC Navigation Path",
            "",
        ]
        for entry_id in unclassified_ids:
            title = source.entries_by_id[entry_id].get("title") or PurePosixPath(
                note_by_id[entry_id]
            ).stem
            target = _relative_target(output, note_by_id[entry_id])
            lines.append(f"- [{_escape_label(title)}]({target})")
        files[output] = ("\n".join(lines).rstrip() + "\n").encode("utf-8")
        home_indexes.append(
            {"title": "无 HHC Navigation Path", "output_path": output}
        )
        indexes.append(
            {
                "title": "无 HHC Navigation Path",
                "output_path": output,
                "navigation_node_id": "",
            }
        )
    return files, home_indexes, {
        "navigation_node_count": len(nodes),
        "navigation_index_count": len(indexes),
        "linked_target_count": sum(
            node.get("target_entry_id") in note_by_id for node in nodes
        ),
        "missing_target_count": sum(
            bool(node.get("local"))
            and node.get("target_entry_id") not in note_by_id
            for node in nodes
        ),
    }


def _file_type(path: str) -> str:
    if path.startswith("Notes/"):
        return "note"
    if path.startswith("Assets/"):
        return "asset"
    if path.startswith("Books/"):
        return "navigation-index"
    if path.startswith("Reports/"):
        return "report"
    if path == "Home.md":
        return "home"
    if path == "README.md":
        return "readme"
    if path.endswith("publisher-manifest.jsonl"):
        return "publisher-manifest"
    if path.endswith("publish-report.json"):
        return "publish-report"
    return "control"


def _build_files(source: PublisherInput) -> tuple[dict[str, bytes], dict[str, Any]]:
    files: dict[str, bytes] = {}
    copied_input_by_output: dict[str, str] = {}
    note_by_id, note_path_collision_count, unclassified_note_count = (
        _plan_note_paths(source)
    )

    asset_outputs: dict[str, str] = {}
    asset_by_output: dict[str, dict[str, Any]] = {}
    for asset in source.assets:
        input_path = PurePosixPath(asset["output_path"])
        if not input_path.parts or input_path.parts[0] != "assets":
            raise ObsidianPublisherError(
                f"Asset Report 路径不在 assets/：{asset['output_path']}"
            )
        output = PurePosixPath("Assets", *input_path.parts[1:]).as_posix()
        asset_outputs[asset["output_path"]] = output
        asset_by_output[output] = asset
        files[output] = _read_input_file(source.root, asset["output_path"])

    resolved_by_source: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for link in source.resolved_links:
        existing = resolved_by_source[link["source_entry_id"]].get(link["output_target"])
        if existing and existing.get("target_entry_id") != link.get("target_entry_id"):
            raise ObsidianPublisherError(
                f"同一已解析 Link 映射到多个目标：{link['source_entry_id']} {link['output_target']}"
            )
        resolved_by_source[link["source_entry_id"]][link["output_target"]] = link

    note_stats: Counter[str] = Counter()
    publisher_manifest: list[dict[str, Any]] = []
    manifest_by_id = {item["entry_id"]: item for item in source.manifest}
    for entry_id in sorted(note_by_id):
        item = manifest_by_id[entry_id]
        raw = _read_input_file(source.root, item["output_path"])
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise ObsidianPublisherError(
                f"输入 Markdown 不是 UTF-8：{item['output_path']}: {exc}"
            ) from exc
        rewritten, stats = _rewrite_note(
            text,
            entry_id=entry_id,
            input_path=item["output_path"],
            output_path=note_by_id[entry_id],
            note_by_id=note_by_id,
            resolved_by_source=resolved_by_source,
            asset_outputs=asset_outputs,
        )
        note_stats.update(stats)
        data = rewritten.encode("utf-8")
        files[note_by_id[entry_id]] = data
        publisher_manifest.append(
            {
                "schema": "m1c3.publisher-note@0.1.0",
                "publisher_profile": PUBLISHER_PROFILE,
                "artifact_id": source.artifact_id,
                "entry_id": entry_id,
                "input_path": item["output_path"],
                "output_path": note_by_id[entry_id],
                "source_path": item["source_path"],
                "navigation_paths": item.get("navigation_paths") or [],
                "source_sha256": item["source_sha256"],
                "content_sha256": _digest(data),
            }
        )

    navigation_files, indexes, navigation_stats = _navigation_files(
        source, note_by_id
    )
    files.update(navigation_files)

    for name in REPORT_FILES:
        output = f"Reports/{name}"
        input_path = f"reports/{name}"
        files[output] = _read_input_file(source.root, input_path)
        copied_input_by_output[output] = input_path
    unresolved_reasons = Counter(
        item.get("reason", "unknown") for item in source.unresolved_links
    )
    limitations = [
        "# Source Limitations",
        "",
        "以下项目来自 M1-C2A Link / Asset Report。Publisher 未创建伪目标或伪资产。",
        "",
        f"- Unresolved 总数：{len(source.unresolved_links)}",
    ]
    limitations.extend(
        f"- `{reason}`：{count}"
        for reason, count in sorted(unresolved_reasons.items())
    )
    files["Reports/Source-Limitations.md"] = (
        "\n".join(limitations) + "\n"
    ).encode("utf-8")

    home = [
        "---",
        f'publisher_profile: "{PUBLISHER_PROFILE}"',
        'publisher_file_type: "home"',
        "---",
        "# LoreBuddy",
        "",
        "这是由 LoreBuddy 生成的 Obsidian Baseline Vault。正文位于 `Notes/`，导航入口位于 `Books/`。",
        "",
        "## 书籍与顶层来源",
        "",
    ]
    for index in indexes:
        home.append(
            f"- [{_escape_label(index['title'])}]({index['output_path']})"
        )
    home.extend(
        [
            "",
            "## 构建信息",
            "",
            f"- 正文 Note：{len(publisher_manifest)}",
            f"- 本地 Asset：{len(source.assets)}",
            f"- HHC Navigation Node：{navigation_stats['navigation_node_count']}",
            f"- Unresolved：{len(source.unresolved_links)}",
            "- [Source Limitations](Reports/Source-Limitations.md)",
            "",
        ]
    )
    files["Home.md"] = ("\n".join(home) + "\n").encode("utf-8")
    files["README.md"] = (
        "# LoreBuddy Obsidian Baseline Vault\n\n"
        "使用 Obsidian 的“打开文件夹作为仓库”选择本目录，然后打开 `Home.md`。\n\n"
        "该目录是确定性生成的只读产品视图。请勿在其中保存重要个人修改；"
        "Source Reality 限制见 `Reports/Source-Limitations.md`。\n"
    ).encode("utf-8")
    files[".lorebuddy/.lorebuddy-m1c3.json"] = _canonical(MARKER)
    files[".lorebuddy/publisher-manifest.jsonl"] = _jsonl(publisher_manifest)

    report = {
        "schema": "m1c3.publish-report@0.1.0",
        "publisher_profile": PUBLISHER_PROFILE,
        "artifact_id": source.artifact_id,
        "summary": {
            "note_count": len(publisher_manifest),
            "asset_count": len(source.assets),
            "navigation_index_count": navigation_stats["navigation_index_count"],
            "navigation_occurrence_count": navigation_stats[
                "navigation_node_count"
            ],
            "navigation_linked_target_count": navigation_stats[
                "linked_target_count"
            ],
            "navigation_missing_target_count": navigation_stats[
                "missing_target_count"
            ],
            "note_path_collision_count": note_path_collision_count,
            "unclassified_note_count": unclassified_note_count,
            "internal_link_rewrite_count": note_stats["internal_link_rewritten"],
            "same_page_anchor_preserved_count": note_stats[
                "same_page_anchor_preserved"
            ],
            "image_rewrite_count": note_stats["image_rewritten"],
            "unresolved_preserved_count": len(source.unresolved_links),
        },
        "unresolved_reasons": dict(sorted(unresolved_reasons.items())),
        "navigation_order": {
            "global_sibling_order": "source-hhc-sibling-order",
            "entry_navigation_paths_order": "preserved",
            "pure_directory_nodes": "preserved-as-navigation-index",
        },
        "note_path_projection": {
            "canonical_navigation_path": "highest-source-path-affinity",
            "fallback": "Notes/_Unclassified/<title>.md",
            "identity_suffix": "only-on-normalized-output-path-collision",
            "multiple_navigation_paths": "single-body-multiple-index-references",
            "tie_breaker": "source-entry-id-then-hhc-source-order",
        },
    }
    files[".lorebuddy/publish-report.json"] = _canonical(report)

    input_by_note = {
        item["output_path"]: item for item in publisher_manifest
    }
    ownership_files: list[dict[str, Any]] = []
    for path in sorted(files):
        note = input_by_note.get(path)
        asset = asset_by_output.get(path)
        ownership_files.append(
            {
                "path": path,
                "file_type": _file_type(path),
                "entry_id": note.get("entry_id") if note else None,
                "asset_entry_id": asset.get("entry_id") if asset else None,
                "asset_source_sha256": asset.get("source_sha256") if asset else None,
                "input_source": (
                    note.get("input_path")
                    if note
                    else asset.get("output_path")
                    if asset
                    else copied_input_by_output.get(path, "publisher-generated")
                ),
                "content_sha256": _digest(files[path]),
                "publisher_version": "0.1.0",
            }
        )
    ownership = {
        "schema": "m1c3.ownership-manifest@0.1.0",
        "publisher_profile": PUBLISHER_PROFILE,
        "self_path": ".lorebuddy/ownership-manifest.json",
        "self_digest_policy": "excluded-to-avoid-self-referential-digest",
        "files": ownership_files,
    }
    files[".lorebuddy/ownership-manifest.json"] = _canonical(ownership)
    return files, report


def _owned_output(path: Path) -> bool:
    marker = path / ".lorebuddy" / ".lorebuddy-m1c3.json"
    if not path.is_dir() or not marker.is_file() or marker.is_symlink():
        return False
    try:
        return json.loads(marker.read_text(encoding="utf-8")) == MARKER
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False


def _plan_changes(output: Path, files: dict[str, bytes]) -> dict[str, int]:
    if not output.exists():
        return {
            "create_count": len(files),
            "rewrite_count": 0,
            "unchanged_count": 0,
            "remove_count": 0,
        }
    if not _owned_output(output):
        raise ObsidianPublisherError(f"拒绝覆盖非 LoreBuddy M1-C3 owned 目录：{output}")
    actual = {
        path.relative_to(output).as_posix(): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    return {
        "create_count": sum(path not in actual for path in files),
        "rewrite_count": sum(
            path in actual and actual[path] != data for path, data in files.items()
        ),
        "unchanged_count": sum(
            path in actual and actual[path] == data for path, data in files.items()
        ),
        "remove_count": sum(path not in files for path in actual),
    }


def dry_run_obsidian_baseline(build_root: Path, output: Path) -> dict[str, Any]:
    source = _load_input(build_root)
    target = output.resolve()
    if (
        target == source.root
        or target.is_relative_to(source.root)
        or source.root.is_relative_to(target)
    ):
        raise ObsidianPublisherError("输出目录不得与输入 Build Root 重叠")
    files, report = _build_files(source)
    return {
        "dry_run": True,
        "input_valid": True,
        "output": str(target),
        "changes": _plan_changes(target, files),
        "summary": report["summary"],
    }


def publish_obsidian_baseline(build_root: Path, output: Path) -> dict[str, Any]:
    source = _load_input(build_root)
    target = output.resolve()
    if (
        target == source.root
        or target.is_relative_to(source.root)
        or source.root.is_relative_to(target)
    ):
        raise ObsidianPublisherError("输出目录不得与输入 Build Root 重叠")
    files, _ = _build_files(source)
    changes = _plan_changes(target, files)
    staging = target.with_name(f".{target.name}.staging")
    backup = target.with_name(f".{target.name}.previous")
    for candidate in (staging, backup):
        if candidate.exists():
            if not _owned_output(candidate):
                raise ObsidianPublisherError(f"拒绝清理未知目录：{candidate}")
            shutil.rmtree(candidate)
    staging.mkdir(parents=True)
    try:
        marker_path = staging / ".lorebuddy" / ".lorebuddy-m1c3.json"
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_bytes(files[".lorebuddy/.lorebuddy-m1c3.json"])
        for relative, data in files.items():
            if relative == ".lorebuddy/.lorebuddy-m1c3.json":
                continue
            destination = _safe_path(staging, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        validation = validate_obsidian_baseline(staging)
        if not validation["valid"]:
            raise ObsidianPublisherError(
                f"Publisher Staging Validator 失败：{validation['errors'][:3]}"
            )
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(staging, target)
        except OSError:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        final = validate_obsidian_baseline(target)
        return {**final, "changes": changes, "output": str(target)}
    except Exception:
        if staging.exists() and _owned_output(staging):
            shutil.rmtree(staging)
        raise


def _local_reference(note_path: Path, target: str, root: Path) -> Path | None:
    target = html.unescape(target).strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    split = urlsplit(unquote(target))
    if split.scheme or target.startswith("//") or not split.path:
        return None
    path = (note_path.parent / split.path).resolve()
    return path if path.is_relative_to(root) else Path()


def validate_obsidian_baseline(output: Path) -> dict[str, Any]:
    root = output.resolve(strict=True)
    errors: list[dict[str, str]] = []
    required = (
        "README.md",
        "Home.md",
        ".lorebuddy/.lorebuddy-m1c3.json",
        ".lorebuddy/publisher-manifest.jsonl",
        ".lorebuddy/ownership-manifest.json",
        ".lorebuddy/publish-report.json",
    )
    for relative in required:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            errors.append({"code": "MISSING_FILE", "message": relative})
    if errors:
        return {"valid": False, "errors": errors, "summary": {}}
    try:
        marker = json.loads(
            (root / ".lorebuddy/.lorebuddy-m1c3.json").read_text(encoding="utf-8")
        )
        manifest = _load_jsonl(root / ".lorebuddy/publisher-manifest.jsonl")
        ownership = json.loads(
            (root / ".lorebuddy/ownership-manifest.json").read_text(encoding="utf-8")
        )
        report = json.loads(
            (root / ".lorebuddy/publish-report.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "valid": False,
            "errors": [{"code": "LOAD_ERROR", "message": str(exc)}],
            "summary": {},
        }
    if marker != MARKER:
        errors.append({"code": "INVALID_MARKER", "message": str(marker)})

    actual_files = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    declared = {
        item.get("path"): item for item in ownership.get("files", [])
    }
    self_path = ownership.get("self_path")
    if set(actual_files) != set(declared) | {self_path}:
        errors.append(
            {
                "code": "OWNERSHIP_CLOSURE",
                "message": (
                    f"actual={len(actual_files)} declared={len(declared)} self={self_path}"
                ),
            }
        )
    allowed_types = {
        "note",
        "asset",
        "navigation-index",
        "report",
        "home",
        "readme",
        "publisher-manifest",
        "publish-report",
        "control",
    }
    for relative, item in declared.items():
        path = actual_files.get(relative)
        if path is None:
            continue
        if item.get("file_type") not in allowed_types:
            errors.append({"code": "UNKNOWN_OWNED_TYPE", "message": relative})
        if _digest(path.read_bytes()) != item.get("content_sha256"):
            errors.append({"code": "OWNED_DIGEST", "message": relative})

    entry_ids: set[str] = set()
    note_paths: set[str] = set()
    for item in manifest:
        entry_id = item.get("entry_id")
        output_path = item.get("output_path")
        if entry_id in entry_ids:
            errors.append({"code": "DUPLICATE_ENTRY_NOTE", "message": str(entry_id)})
        entry_ids.add(entry_id)
        if str(output_path).casefold() in note_paths:
            errors.append({"code": "DUPLICATE_NOTE_PATH", "message": str(output_path)})
        note_paths.add(str(output_path).casefold())
        path = actual_files.get(output_path)
        if path is None:
            errors.append({"code": "MISSING_NOTE", "message": str(output_path)})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            errors.append({"code": "NOT_UTF8", "message": f"{output_path}: {exc}"})
            continue
        if "\r" in text:
            errors.append({"code": "CR_IN_FILE", "message": output_path})
        if PRIVATE_PATH_PATTERN.search(text):
            errors.append({"code": "PRIVATE_ABSOLUTE_PATH", "message": output_path})
        try:
            metadata = yaml.safe_load(text.split("---", 2)[1])
        except (IndexError, yaml.YAMLError) as exc:
            errors.append(
                {"code": "INVALID_FRONT_MATTER", "message": f"{output_path}: {exc}"}
            )
            continue
        for field in (
            "entry_id",
            "source_path",
            "navigation_paths",
            "source_sha256",
        ):
            if metadata.get(field) != item.get(field):
                errors.append(
                    {
                        "code": "PUBLISHER_METADATA_MISMATCH",
                        "message": f"{output_path}: {field}",
                    }
                )
        if metadata.get("publisher_profile") != PUBLISHER_PROFILE:
            errors.append(
                {"code": "PUBLISHER_PROFILE", "message": str(output_path)}
            )
        if _digest(path.read_bytes()) != item.get("content_sha256"):
            errors.append({"code": "NOTE_DIGEST", "message": str(output_path)})

    for relative, path in actual_files.items():
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            if relative.startswith("Assets/"):
                continue
            errors.append({"code": "NOT_UTF8", "message": relative})
            continue
        if "\r" in text:
            errors.append({"code": "CR_IN_FILE", "message": relative})
        if PRIVATE_PATH_PATTERN.search(text):
            errors.append({"code": "PRIVATE_ABSOLUTE_PATH", "message": relative})
        if not relative.endswith(".md"):
            continue
        references = [
            (bool(match.group("image")), _split_target(match.group("target"))[1])
            for match in MARKDOWN_REFERENCE.finditer(text)
        ]
        references.extend(
            (False, match.group("target")) for match in HTML_HREF.finditer(text)
        )
        references.extend(
            (True, match.group("target")) for match in HTML_IMAGE.finditer(text)
        )
        for is_image, target in references:
            local = _local_reference(path, target, root)
            if local == Path():
                errors.append(
                    {"code": "REFERENCE_ESCAPE", "message": f"{relative}: {target}"}
                )
            elif local is not None and not local.is_file():
                errors.append(
                    {
                        "code": "MISSING_LOCAL_IMAGE"
                        if is_image
                        else "MISSING_LOCAL_LINK",
                        "message": f"{relative}: {target}",
                    }
                )

    actual_notes = {
        path.relative_to(root).as_posix().casefold()
        for path in (root / "Notes").rglob("*.md")
        if path.is_file()
    }
    if actual_notes != note_paths:
        errors.append(
            {
                "code": "NOTE_MANIFEST_CLOSURE",
                "message": f"actual={len(actual_notes)} manifest={len(note_paths)}",
            }
        )
    summary = report.get("summary", {})
    navigation_nodes = _load_jsonl(root / "Reports/navigation-tree.jsonl")
    actual_navigation_indexes = [
        path for path in (root / "Books").rglob("*.md") if path.is_file()
    ]
    navigation_node_ids: set[str] = set()
    for path in actual_navigation_indexes:
        try:
            metadata = yaml.safe_load(
                path.read_text(encoding="utf-8").split("---", 2)[1]
            )
        except (IndexError, UnicodeError, yaml.YAMLError) as exc:
            errors.append(
                {
                    "code": "INVALID_NAVIGATION_FRONT_MATTER",
                    "message": f"{path.relative_to(root)}: {exc}",
                }
            )
            continue
        node_id = metadata.get("navigation_node_id")
        if node_id is None:
            continue
        if node_id in navigation_node_ids:
            errors.append(
                {"code": "DUPLICATE_NAVIGATION_INDEX", "message": str(node_id)}
            )
        navigation_node_ids.add(node_id)
    known_navigation_node_ids = {
        node.get("navigation_node_id") for node in navigation_nodes
    }
    if not navigation_node_ids.issubset(known_navigation_node_ids):
        errors.append(
            {
                "code": "UNKNOWN_NAVIGATION_INDEX_NODE",
                "message": str(
                    sorted(navigation_node_ids - known_navigation_node_ids)[:3]
                ),
            }
        )
    if summary.get("navigation_index_count") != len(actual_navigation_indexes):
        errors.append(
            {
                "code": "REPORT_NAVIGATION_INDEX_COUNT",
                "message": (
                    f"actual={len(actual_navigation_indexes)} "
                    f"report={summary.get('navigation_index_count')}"
                ),
            }
        )
    if summary.get("navigation_occurrence_count") != len(navigation_nodes):
        errors.append(
            {
                "code": "REPORT_NAVIGATION_NODE_COUNT",
                "message": (
                    f"actual={len(navigation_nodes)} "
                    f"report={summary.get('navigation_occurrence_count')}"
                ),
            }
        )
    if summary.get("note_count") != len(manifest):
        errors.append({"code": "REPORT_NOTE_COUNT", "message": str(summary)})
    return {
        "valid": not errors,
        "errors": errors,
        "summary": {
            "note_count": len(manifest),
            "asset_count": summary.get("asset_count"),
            "navigation_index_count": summary.get("navigation_index_count"),
            "unresolved_count": summary.get("unresolved_preserved_count"),
        },
    }


def load_obsidian_publish_report(output: Path) -> dict[str, Any]:
    root = output.resolve(strict=True)
    return json.loads(
        (root / ".lorebuddy/publish-report.json").read_text(encoding="utf-8")
    )
