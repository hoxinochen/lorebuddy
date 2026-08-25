"""面向 ChatGPT Project 的确定性、低文件数 Markdown 导出。

该导出只消费通过 M1-C3 Validator 的独立 Obsidian Baseline，不读取 CHM、
M1-C2A Build Root、Vault 配置或其他隐式状态。它把每份 Note 原字节嵌入少量
内容包，以减少上传文件数；不改写正文，也不冒充 Knowledge Node。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from lorebuddy.publishing.obsidian import validate_obsidian_baseline


GPT_EXPORT_PROFILE = "m1c4.gpt-project-export@0.1.0"
DEFAULT_MAX_UPLOAD_FILES = 20
DEFAULT_MAX_CONTENT_FILES = 18
DEFAULT_MAX_BUNDLE_BYTES = 1_950_000
CONTROL_FILES = ("00-README.md", "01-CONTENTS.md")
EXPORT_MARKER_PREFIX = b"<!-- LOREBUDDY_GPT_EXPORT "
ENTRY_MARKER_PREFIX = b"<!-- LOREBUDDY_ENTRY "
ENTRY_MARKER_SUFFIX = b" -->\n"
ENTRY_END = b"\n<!-- /LOREBUDDY_ENTRY -->\n"
BUNDLE_RESERVE_BYTES = 8192
PRIVATE_PATH_PATTERN = re.compile(rb"(?:/Users/[^/\s]+/|/home/[^/\s]+/)")


class GPTProjectExportError(RuntimeError):
    """GPT Project 导出输入、预算或输出违反合同。"""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _safe_file(root: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if not relative or pure.is_absolute() or ".." in pure.parts:
        raise GPTProjectExportError(f"非法相对路径：{relative!r}")
    path = (root / pure).resolve()
    if not path.is_relative_to(root):
        raise GPTProjectExportError(f"路径逃逸：{relative!r}")
    if not path.is_file() or path.is_symlink():
        raise GPTProjectExportError(f"文件缺失或不是普通文件：{relative}")
    return path


def _load_source(source_root: Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    root = source_root.resolve(strict=True)
    validation = validate_obsidian_baseline(root)
    if not validation["valid"]:
        raise GPTProjectExportError(
            f"M1-C3 Baseline 未通过 Validator：{validation['errors'][:3]}"
        )
    report = json.loads(
        _safe_file(root, ".lorebuddy/publish-report.json").read_text(
            encoding="utf-8"
        )
    )
    manifest_path = _safe_file(root, ".lorebuddy/publisher-manifest.jsonl")
    manifest = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not manifest:
        raise GPTProjectExportError("M1-C3 Publisher Manifest 为空")
    return root, report, sorted(manifest, key=lambda item: item["output_path"])


def _entry_record(item: dict[str, Any], note: bytes) -> bytes:
    metadata = {
        "b": len(note),
        "id": item["entry_id"],
    }
    return (
        ENTRY_MARKER_PREFIX
        + _canonical_json(metadata)
        + ENTRY_MARKER_SUFFIX
        + note
        + ENTRY_END
    )


def _navigation_components(item: dict[str, Any]) -> list[str]:
    parts = list(PurePosixPath(item["output_path"]).parts)
    if parts and parts[0] == "Notes":
        parts = parts[1:]
    if not parts:
        return ["_Unclassified"]
    parts[-1] = PurePosixPath(parts[-1]).stem
    return parts


def _group_navigation_summary(
    group: list[tuple[dict[str, Any], bytes]],
) -> tuple[list[dict[str, Any]], list[str]]:
    top_counts: Counter[str] = Counter()
    topics_by_top: dict[str, Counter[str]] = defaultdict(Counter)
    searchable_components: Counter[str] = Counter()
    for item, _ in group:
        parts = _navigation_components(item)
        top = parts[0]
        top_counts[top] += 1
        for component in parts[1:-1]:
            topics_by_top[top][component] += 1
            searchable_components[component] += 1
    sources: list[dict[str, Any]] = []
    for top, count in sorted(top_counts.items()):
        topics = [
            {"entry_count": topic_count, "title": title}
            for title, topic_count in sorted(
                topics_by_top[top].items(),
                key=lambda pair: (-pair[1], pair[0]),
            )[:8]
        ]
        sources.append(
            {"entry_count": count, "source": top, "topics": topics}
        )
    keywords = [
        title
        for title, _ in sorted(
            searchable_components.items(),
            key=lambda pair: (-pair[1], pair[0]),
        )[:24]
    ]
    return sources, keywords


def _bundle_header(
    number: int,
    total: int,
    group: list[tuple[dict[str, Any], bytes]],
) -> bytes:
    sources, keywords = _group_navigation_summary(group)
    lines = [
        f"# LoreBuddy GPT 内容包 {number:02d}/{total:02d}",
        "",
        f"导出 Profile：`{GPT_EXPORT_PROFILE}`。本包包含 {len(group)} 个 "
        "Entry。每个 `LOREBUDDY_ENTRY` 边界内是一份未经改写的 M1-C3 Note，"
        "Front Matter 保留稳定 Entry ID、物理 Source Path、Navigation Paths "
        "和来源摘要。",
        "",
        "## 本包内容导航",
        "",
        "以下目录由 Publisher 输出路径机械汇总，不是对官方正文的 AI 总结：",
        "",
    ]
    for source in sources:
        topic_text = "；".join(
            f"{topic['title']}（{topic['entry_count']}）"
            for topic in source["topics"]
        )
        suffix = f"。主要导航：{topic_text}" if topic_text else ""
        lines.append(
            f"- {source['source']}：{source['entry_count']} 个 Entry{suffix}"
        )
    lines.extend(["", "## 检索提示", ""])
    if keywords:
        lines.append("- 高频导航词：" + "、".join(keywords))
    lines.extend(
        [
            "- 回答问题时只读取与用户请求直接相关的 Entry，不要因为本包同时"
            "包含其他来源而展开无关规则。",
            "- 若资料明确存在同一规则的新旧版本，默认采用最新适用版本；旧版"
            "只用于缺少新版对应内容、历史比较或用户明确指定的旧版 Campaign。",
            "",
        ]
    )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _pack_entries(
    source_root: Path,
    manifest: list[dict[str, Any]],
    *,
    max_content_files: int,
    max_bundle_bytes: int,
) -> tuple[list[list[tuple[dict[str, Any], bytes]]], int]:
    if max_content_files < 1:
        raise GPTProjectExportError("max_content_files 必须大于 0")
    if max_bundle_bytes <= BUNDLE_RESERVE_BYTES:
        raise GPTProjectExportError(
            f"max_bundle_bytes 必须大于 {BUNDLE_RESERVE_BYTES}"
        )
    records: list[tuple[dict[str, Any], bytes]] = []
    groups: list[list[tuple[dict[str, Any], bytes]]] = []
    current: list[tuple[dict[str, Any], bytes]] = []
    current_size = BUNDLE_RESERVE_BYTES
    note_bytes = 0
    for item in manifest:
        note = _safe_file(source_root, item["output_path"]).read_bytes()
        if _digest(note) != item["content_sha256"]:
            raise GPTProjectExportError(
                f"Note 摘要与 Publisher Manifest 不一致：{item['output_path']}"
            )
        record = _entry_record(item, note)
        if len(record) + BUNDLE_RESERVE_BYTES > max_bundle_bytes:
            raise GPTProjectExportError(
                f"单份 Note 无法装入内容包：{item['output_path']}"
            )
        records.append((item, record))
        note_bytes += len(note)
    for item, record in records:
        if current and current_size + len(record) > max_bundle_bytes:
            groups.append(current)
            current = []
            current_size = BUNDLE_RESERVE_BYTES
        current.append((item, record))
        current_size += len(record)
    if current:
        groups.append(current)
    if len(groups) > max_content_files:
        # 连续路径优先的顺序装箱若超过文件预算，使用稳定 Best Fit
        # Decreasing。它只改变 Entry 被分配到哪个内容包，不改变 Note 字节、
        # Entry 身份或包内稳定排序。
        bins: list[tuple[int, list[tuple[dict[str, Any], bytes]]]] = []
        for item, record in sorted(
            records,
            key=lambda pair: (-len(pair[1]), pair[0]["output_path"]),
        ):
            candidates = [
                (max_bundle_bytes - (size + len(record)), index)
                for index, (size, _) in enumerate(bins)
                if size + len(record) <= max_bundle_bytes
            ]
            if candidates:
                _, index = min(candidates)
                size, members = bins[index]
                members.append((item, record))
                bins[index] = (size + len(record), members)
            elif len(bins) < max_content_files:
                bins.append(
                    (BUNDLE_RESERVE_BYTES + len(record), [(item, record)])
                )
            else:
                raise GPTProjectExportError(
                    "文件预算不足：稳定装箱仍无法在 "
                    f"{max_content_files} 个内容包、每包 {max_bundle_bytes} bytes "
                    "内保存全部 Entry"
                )
        groups = [
            sorted(members, key=lambda pair: pair[0]["output_path"])
            for _, members in bins
        ]
        groups.sort(key=lambda members: members[0][0]["output_path"])
    return groups, note_bytes


def _render_files(
    source_root: Path,
    report: dict[str, Any],
    manifest: list[dict[str, Any]],
    *,
    max_upload_files: int,
    max_content_files: int,
    max_bundle_bytes: int,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    if max_upload_files > DEFAULT_MAX_UPLOAD_FILES:
        raise GPTProjectExportError(
            f"M1-C4 文件预算不得超过 {DEFAULT_MAX_UPLOAD_FILES}"
        )
    if max_content_files > DEFAULT_MAX_CONTENT_FILES:
        raise GPTProjectExportError(
            f"M1-C4 内容包预算不得超过 {DEFAULT_MAX_CONTENT_FILES}"
        )
    if max_bundle_bytes > DEFAULT_MAX_BUNDLE_BYTES:
        raise GPTProjectExportError(
            f"M1-C4 单包预算不得超过 {DEFAULT_MAX_BUNDLE_BYTES} bytes"
        )
    if max_upload_files < len(CONTROL_FILES) + 1:
        raise GPTProjectExportError("max_upload_files 至少为 3")
    if max_content_files > max_upload_files - len(CONTROL_FILES):
        raise GPTProjectExportError(
            "max_content_files 不能超过扣除控制文件后的上传文件预算"
        )
    groups, source_note_bytes = _pack_entries(
        source_root,
        manifest,
        max_content_files=max_content_files,
        max_bundle_bytes=max_bundle_bytes,
    )
    artifact_id = report["artifact_id"]
    manifest_bytes = _safe_file(
        source_root, ".lorebuddy/publisher-manifest.jsonl"
    ).read_bytes()
    marker = {
        "artifact_id": artifact_id,
        "entry_count": len(manifest),
        "manifest_sha256": _digest(manifest_bytes),
        "max_bundle_bytes": max_bundle_bytes,
        "max_content_files": max_content_files,
        "max_upload_files": max_upload_files,
        "profile": GPT_EXPORT_PROFILE,
    }
    files: dict[str, bytes] = {}
    bundle_rows: list[dict[str, Any]] = []
    total = len(groups)
    for index, group in enumerate(groups, start=1):
        name = f"{index + 1:02d}-content-{index:02d}.md"
        sources, keywords = _group_navigation_summary(group)
        data = _bundle_header(index, total, group) + b"".join(
            record for _, record in group
        )
        if len(data) > max_bundle_bytes:
            raise GPTProjectExportError(
                f"内容包超过字节预算：{name}={len(data)} > {max_bundle_bytes}"
            )
        files[name] = data
        bundle_rows.append(
            {
                "entry_count": len(group),
                "file": name,
                "first_output_path": group[0][0]["output_path"],
                "last_output_path": group[-1][0]["output_path"],
                "navigation_keywords": keywords,
                "sha256": _digest(data),
                "sources": sources,
                "utf8_bytes": len(data),
            }
        )
    readme_marker = (
        EXPORT_MARKER_PREFIX + _canonical_json(marker) + ENTRY_MARKER_SUFFIX
    ).decode("ascii")
    files["00-README.md"] = (
        readme_marker
        + "# LoreBuddy GPT Project Export\n\n"
        "该目录是从已通过 Validator 的 M1-C3 Obsidian Baseline 确定性生成的"
        "低文件数只读导出，适合上传到 ChatGPT Project 作为项目资料。\n\n"
        "## 使用方式\n\n"
        "1. 上传本目录全部文件；\n"
        "2. 优先让模型阅读 `00-README.md` 与 `01-CONTENTS.md`；\n"
        "3. 回答规则问题时要求引用 Entry ID、`source_path` 或标题；\n"
        "4. 以后新增资料应作为独立文件上传，不要修改这些生成内容包。\n\n"
        "## 默认规则版本策略\n\n"
        "- 资料明确存在同一规则的新旧版本时，默认采用最新适用版本，不再"
        "反复询问是否使用 2024 等新版规则；\n"
        "- 旧版仅用于新版没有对应内容、历史比较，或用户明确指定的旧版"
        " Campaign；\n"
        "- 不得把新旧版本字段静默拼接；第三方或 Homebrew 不因日期较新而"
        "自动覆盖官方规则；\n"
        "- 无法确认是否为同一规则时，应报告歧义，不得猜测替代关系。\n\n"
        "## 检索节制\n\n"
        "- 先阅读 `01-CONTENTS.md` 的任务路由和包级目录；\n"
        "- 只检索与当前问题直接相关的内容包与 Entry；\n"
        "- 不要为了回答单个角色、法术或规则问题扫描全部规则；\n"
        "- 找到足够的直接来源后停止扩大检索范围。\n\n"
        "## 边界\n\n"
        f"- 内容包只合并 M1-C3 的 {len(manifest):,} 份正文 Note，不包含重复导航索引、"
        "报告或图片二进制；\n"
        "- 每份 Note 的原字节和 Front Matter 均保留，正文未总结、改写或"
        "语义切分；\n"
        "- 原相对链接保留为来源文本，但合并后不承诺可点击；\n"
        "- 这是受限的本地导出，不表示内容可公开或再分发；\n"
        "- 本导出不是 Fragment、Knowledge Node、Library、RAG 或向量库。\n\n"
        f"上传文件预算：最多 {max_upload_files} 个；本次实际 "
        f"{len(files) + 2} 个，其中 2 个控制文件、{total} 个内容包。\n"
    ).encode("utf-8")
    contents_lines = [
        "# LoreBuddy GPT Export Contents",
        "",
        f"- Profile：`{GPT_EXPORT_PROFILE}`",
        f"- Artifact ID：`{artifact_id}`",
        f"- Entry：{len(manifest)}",
        f"- Source Note 原字节：{source_note_bytes}",
        f"- 内容包：{total}",
        f"- 总上传文件：{total + 2} / {max_upload_files}",
        f"- 单内容包上限：{max_bundle_bytes} UTF-8 bytes",
        "- Token Count：未直接测量；字节上限仅作为保守的本地预检约束",
        "",
        "## 默认规则版本策略",
        "",
        "- 同一规则存在明确新旧版本时，默认采用最新适用版本。",
        "- 旧版只用于新版没有对应内容、历史比较或用户明确指定的旧版 Campaign。",
        "- 不静默混合新旧字段；第三方或 Homebrew 不因日期较新而覆盖官方规则。",
        "- 无法确认替代关系时报告歧义，但不反复询问一般性的版本偏好。",
        "",
        "## 任务检索路由",
        "",
        "| 用户任务 | 优先检索标题或 Navigation 关键词 | 默认排除 |",
        "|---|---|---|",
        "| 创建或升级角色 | 玩家手册2024、职业、子职、物种、种族、背景、专长、装备、法术 | 模组正文、怪物图鉴、无关世界设定 |",
        "| 查询通用规则 | 玩家手册2024、城主指南2024、对应规则标题 | 旧版同名规则，除非新版缺项 |",
        "| 法术与能力 | 法术、施法、职业、子职、专长 | 无关怪物与模组 |",
        "| 怪物与遭遇 | 怪物图鉴2025、生物图集、遭遇、环境 | 玩家构筑资料，除非发生能力交互 |",
        "| DM 或冒险准备 | 城主指南2024、对应模组、地点、NPC、遭遇 | 无关规则书与模组 |",
        "| 版本比较 | 同名标题、年份、旧版、新版 | 不适用；必须并列标注来源 |",
        "",
        "路由表用于缩小候选范围，不替代 Entry 原文和来源引用。",
        "",
        "## 内容包概览",
        "",
    ]
    for row in bundle_rows:
        contents_lines.extend(
            [
                f"### `{row['file']}`",
                "",
                f"- Entry：{row['entry_count']}",
                "- 主要来源："
                + "；".join(
                    f"{source['source']}（{source['entry_count']}）"
                    for source in row["sources"]
                ),
                "- 高频导航词："
                + (
                    "、".join(row["navigation_keywords"])
                    if row["navigation_keywords"]
                    else "无"
                ),
                "",
            ]
        )
    contents_lines.extend(
        [
        "## 文件完整性",
        "",
        "| 文件 | Entry | UTF-8 bytes | SHA-256 |",
        "|---|---:|---:|---|",
        ]
    )
    for row in bundle_rows:
        contents_lines.append(
            f"| `{row['file']}` | {row['entry_count']} | "
            f"{row['utf8_bytes']} | `{row['sha256']}` |"
        )
        integrity = {
            "entry_count": row["entry_count"],
            "file": row["file"],
            "sha256": row["sha256"],
            "utf8_bytes": row["utf8_bytes"],
        }
        contents_lines.append(
            "<!-- LOREBUDDY_BUNDLE "
            + _canonical_json(integrity).decode("ascii")
            + " -->"
        )
    files["01-CONTENTS.md"] = ("\n".join(contents_lines) + "\n").encode("utf-8")
    summary = {
        "artifact_id": artifact_id,
        "bundle_count": total,
        "content_file_count": total,
        "control_file_count": 2,
        "entry_count": len(manifest),
        "max_bundle_bytes": max_bundle_bytes,
        "max_content_files": max_content_files,
        "max_upload_files": max_upload_files,
        "profile": GPT_EXPORT_PROFILE,
        "source_manifest_sha256": marker["manifest_sha256"],
        "source_note_bytes": source_note_bytes,
        "upload_file_count": len(files),
    }
    return files, summary


def _owned_output(path: Path) -> bool:
    marker = path / "00-README.md"
    if not path.is_dir() or not marker.is_file() or marker.is_symlink():
        return False
    try:
        first = marker.read_bytes().splitlines(keepends=True)[0]
        return (
            first.startswith(EXPORT_MARKER_PREFIX)
            and f'"profile":"{GPT_EXPORT_PROFILE}"'.encode("ascii") in first
        )
    except OSError:
        return False


def _write_atomic(output: Path, files: dict[str, bytes]) -> None:
    target = output.resolve()
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not _owned_output(target):
        raise GPTProjectExportError(f"拒绝覆盖未知输出目录：{target}")
    staging = parent / f".{target.name}.lorebuddy-gpt-staging"
    backup = parent / f".{target.name}.lorebuddy-gpt-backup"
    for path in (staging, backup):
        if path.exists():
            if not _owned_output(path):
                raise GPTProjectExportError(f"拒绝清理未知工作目录：{path}")
            shutil.rmtree(path)
    staging.mkdir()
    for relative, data in sorted(files.items()):
        destination = staging / relative
        destination.write_bytes(data)
    if target.exists():
        os.replace(target, backup)
    try:
        os.replace(staging, target)
    except Exception:
        if backup.exists() and not target.exists():
            os.replace(backup, target)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def build_gpt_project_export(
    source_root: Path,
    output: Path,
    *,
    max_upload_files: int = DEFAULT_MAX_UPLOAD_FILES,
    max_content_files: int = DEFAULT_MAX_CONTENT_FILES,
    max_bundle_bytes: int = DEFAULT_MAX_BUNDLE_BYTES,
) -> dict[str, Any]:
    """从 M1-C3 Baseline 生成低文件数、确定性的 GPT Project Export。"""

    root, report, manifest = _load_source(source_root)
    files, summary = _render_files(
        root,
        report,
        manifest,
        max_upload_files=max_upload_files,
        max_content_files=max_content_files,
        max_bundle_bytes=max_bundle_bytes,
    )
    _write_atomic(output, files)
    validation = validate_gpt_project_export(root, output)
    if not validation["valid"]:
        raise GPTProjectExportError(
            f"导出后 Validator 失败：{validation['errors'][:3]}"
        )
    return validation


def _parse_export_marker(readme: bytes) -> dict[str, Any]:
    first = readme.splitlines(keepends=True)[0]
    if not first.startswith(EXPORT_MARKER_PREFIX) or not first.endswith(
        ENTRY_MARKER_SUFFIX
    ):
        raise GPTProjectExportError("00-README.md 缺少有效 Export Marker")
    return json.loads(
        first[len(EXPORT_MARKER_PREFIX) : -len(ENTRY_MARKER_SUFFIX)]
    )


def _parse_bundle(data: bytes) -> list[tuple[dict[str, Any], bytes]]:
    records: list[tuple[dict[str, Any], bytes]] = []
    cursor = 0
    while True:
        start = data.find(ENTRY_MARKER_PREFIX, cursor)
        if start < 0:
            break
        marker_end = data.find(ENTRY_MARKER_SUFFIX, start)
        if marker_end < 0:
            raise GPTProjectExportError("内容包存在未闭合 Entry Marker")
        metadata = json.loads(
            data[start + len(ENTRY_MARKER_PREFIX) : marker_end]
        )
        note_start = marker_end + len(ENTRY_MARKER_SUFFIX)
        byte_length = metadata.get("b")
        if not isinstance(byte_length, int) or byte_length < 0:
            raise GPTProjectExportError("Entry Marker 缺少有效 byte_length")
        note_end = note_start + byte_length
        if data[note_end : note_end + len(ENTRY_END)] != ENTRY_END:
            raise GPTProjectExportError(
                f"Entry 边界或 byte_length 无效：{metadata.get('id')}"
            )
        records.append((metadata, data[note_start:note_end]))
        cursor = note_end + len(ENTRY_END)
    return records


def validate_gpt_project_export(
    source_root: Path,
    output: Path,
) -> dict[str, Any]:
    """对照显式 M1-C3 输入验证导出闭合、原字节与文件预算。"""

    errors: list[dict[str, str]] = []
    try:
        root, report, manifest = _load_source(source_root)
    except (OSError, ValueError, json.JSONDecodeError, GPTProjectExportError) as exc:
        return {"valid": False, "errors": [{"code": "INVALID_SOURCE", "message": str(exc)}]}
    export = output.resolve()
    if not export.is_dir():
        return {
            "valid": False,
            "errors": [{"code": "MISSING_OUTPUT", "message": str(export)}],
        }
    actual_paths: list[str] = []
    for path in sorted(export.rglob("*")):
        if path.is_symlink() or (path.exists() and not path.is_file()):
            if path != export and not path.is_dir():
                errors.append({"code": "NON_REGULAR_FILE", "message": str(path)})
            continue
        if path.is_file():
            actual_paths.append(path.relative_to(export).as_posix())
    try:
        readme = _safe_file(export, "00-README.md").read_bytes()
        marker = _parse_export_marker(readme)
    except (OSError, ValueError, json.JSONDecodeError, GPTProjectExportError) as exc:
        errors.append({"code": "INVALID_MARKER", "message": str(exc)})
        marker = {}
    manifest_bytes = _safe_file(
        root, ".lorebuddy/publisher-manifest.jsonl"
    ).read_bytes()
    expected_marker = {
        "artifact_id": report["artifact_id"],
        "entry_count": len(manifest),
        "manifest_sha256": _digest(manifest_bytes),
        "max_bundle_bytes": marker.get("max_bundle_bytes"),
        "max_content_files": marker.get("max_content_files"),
        "max_upload_files": marker.get("max_upload_files"),
        "profile": GPT_EXPORT_PROFILE,
    }
    if marker != expected_marker:
        errors.append(
            {
                "code": "SOURCE_IDENTITY_MISMATCH",
                "message": f"actual={marker!r} expected={expected_marker!r}",
            }
        )
    content_paths = sorted(
        path
        for path in actual_paths
        if re.fullmatch(r"\d{2}-content-\d{2}\.md", path)
    )
    expected_paths = {*CONTROL_FILES, *content_paths}
    if set(actual_paths) != expected_paths:
        errors.append(
            {
                "code": "FILE_CLOSURE",
                "message": (
                    f"unexpected={sorted(set(actual_paths) - expected_paths)} "
                    f"missing={sorted(expected_paths - set(actual_paths))}"
                ),
            }
        )
    max_upload_files = marker.get("max_upload_files")
    max_content_files = marker.get("max_content_files")
    max_bundle_bytes = marker.get("max_bundle_bytes")
    if (
        not isinstance(max_upload_files, int)
        or not isinstance(max_content_files, int)
        or not isinstance(max_bundle_bytes, int)
    ):
        errors.append(
            {"code": "INVALID_BUDGET", "message": "Export Marker 预算字段无效"}
        )
        max_upload_files = DEFAULT_MAX_UPLOAD_FILES
        max_content_files = DEFAULT_MAX_CONTENT_FILES
        max_bundle_bytes = DEFAULT_MAX_BUNDLE_BYTES
    if len(actual_paths) > max_upload_files:
        errors.append(
            {
                "code": "FILE_BUDGET",
                "message": f"{len(actual_paths)} > {max_upload_files}",
            }
        )
    if len(content_paths) > max_content_files:
        errors.append(
            {
                "code": "CONTENT_FILE_BUDGET",
                "message": f"{len(content_paths)} > {max_content_files}",
            }
        )
    try:
        expected_files, _ = _render_files(
            root,
            report,
            manifest,
            max_upload_files=max_upload_files,
            max_content_files=max_content_files,
            max_bundle_bytes=max_bundle_bytes,
        )
    except GPTProjectExportError as exc:
        errors.append({"code": "EXPECTED_RENDER_FAILED", "message": str(exc)})
        expected_files = {}
    for relative, expected_data in expected_files.items():
        if relative not in actual_paths:
            continue
        actual_data = _safe_file(export, relative).read_bytes()
        if actual_data != expected_data:
            errors.append(
                {"code": "NONDETERMINISTIC_OUTPUT", "message": relative}
            )
    expected_by_id = {item["entry_id"]: item for item in manifest}
    seen: dict[str, str] = {}
    source_note_bytes = 0
    for relative in content_paths:
        data = _safe_file(export, relative).read_bytes()
        if len(data) > max_bundle_bytes:
            errors.append(
                {
                    "code": "BUNDLE_BYTE_BUDGET",
                    "message": f"{relative}={len(data)}",
                }
            )
        try:
            data.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            errors.append({"code": "NOT_UTF8", "message": f"{relative}: {exc}"})
        try:
            records = _parse_bundle(data)
        except (ValueError, json.JSONDecodeError, GPTProjectExportError) as exc:
            errors.append({"code": "INVALID_BUNDLE", "message": f"{relative}: {exc}"})
            continue
        for metadata, note in records:
            entry_id = metadata.get("id")
            item = expected_by_id.get(entry_id)
            if item is None:
                errors.append({"code": "UNKNOWN_ENTRY", "message": str(entry_id)})
                continue
            if entry_id in seen:
                errors.append(
                    {
                        "code": "DUPLICATE_ENTRY",
                        "message": f"{entry_id}: {seen[entry_id]}, {relative}",
                    }
                )
                continue
            seen[entry_id] = relative
            expected_note = _safe_file(root, item["output_path"]).read_bytes()
            source_note_bytes += len(note)
            expected_metadata = {
                "b": len(expected_note),
                "id": entry_id,
            }
            if metadata != expected_metadata:
                errors.append(
                    {"code": "ENTRY_METADATA", "message": f"{entry_id}"}
                )
            if note != expected_note:
                errors.append(
                    {"code": "ENTRY_BYTES", "message": f"{entry_id}"}
                )
    missing = sorted(set(expected_by_id) - set(seen))
    if missing:
        errors.append(
            {
                "code": "MISSING_ENTRIES",
                "message": f"count={len(missing)} first={missing[:3]}",
            }
        )
    for relative in actual_paths:
        data = _safe_file(export, relative).read_bytes()
        if PRIVATE_PATH_PATTERN.search(data):
            errors.append({"code": "PRIVATE_PATH", "message": relative})
    return {
        "valid": not errors,
        "errors": errors,
        "summary": {
            "artifact_id": report["artifact_id"],
            "bundle_count": len(content_paths),
            "content_file_count": len(content_paths),
            "control_file_count": len(CONTROL_FILES),
            "entry_count": len(seen),
            "max_bundle_bytes": max(
                (
                    _safe_file(export, relative).stat().st_size
                    for relative in content_paths
                ),
                default=0,
            ),
            "profile": GPT_EXPORT_PROFILE,
            "source_manifest_sha256": _digest(manifest_bytes),
            "source_note_bytes": source_note_bytes,
            "upload_file_count": len(actual_paths),
        },
    }
