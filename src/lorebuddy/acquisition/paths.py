"""CHM Entry 路径的规范化、风险分类与确定性保存路径规划。"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import PurePosixPath
from urllib.parse import unquote


WINDOWS_RESERVED = {
    "con", "prn", "aux", "nul", "clock$",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}
_DRIVE = re.compile(r"^[A-Za-z]:")


class UnsafePathError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PathDecision:
    original_path: str
    normalized_path: str
    preserved_path: str
    path_status: str
    safety_remapped: bool
    conflict_kind: str | None = None
    warnings: tuple[str, ...] = ()


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()[:20]


def normalize_entry_path(raw: str, *, max_length: int = 240) -> tuple[str, tuple[str, ...]]:
    if not isinstance(raw, str) or not raw:
        raise UnsafePathError("empty-path")
    if "\x00" in raw:
        raise UnsafePathError("null-byte")
    decoded = unquote(raw)
    decoded = decoded.replace("\\", "/")
    if decoded.startswith("/") or _DRIVE.match(decoded):
        raise UnsafePathError("absolute-path")
    parts: list[str] = []
    warnings: list[str] = []
    for part in decoded.split("/"):
        if part in {"", "."}:
            if part:
                warnings.append("dot-segment-removed")
            continue
        if part == "..":
            raise UnsafePathError("path-traversal")
        normalized = unicodedata.normalize("NFC", part)
        if normalized != part:
            warnings.append("unicode-normalized")
        if any(ord(char) < 32 for char in normalized):
            raise UnsafePathError("control-character")
        parts.append(normalized)
    if not parts:
        raise UnsafePathError("empty-path")
    result = "/".join(parts)
    if len(result.encode("utf-8")) > max_length:
        warnings.append("path-too-long")
    return result, tuple(sorted(set(warnings)))


def _component_unsafe(component: str) -> str | None:
    if component.endswith((" ", ".")):
        return "windows-trailing-character"
    stem = component.split(".", 1)[0].casefold()
    if stem in WINDOWS_RESERVED:
        return "windows-reserved-name"
    if any(char in '<>:"|?*' for char in component):
        return "windows-invalid-character"
    return None


def _safe_basename(normalized: str) -> str:
    name = PurePosixPath(normalized).name.rstrip(" .")
    name = re.sub(r'[<>:"|?*]', "_", name)
    if not name or _component_unsafe(name):
        name = "entry.bin"
    return name[:100]


def initial_decision(raw: str) -> PathDecision:
    try:
        normalized, warnings = normalize_entry_path(raw)
    except UnsafePathError as exc:
        normalized = f"unsafe/{_digest(raw)}"
        return PathDecision(
            raw, normalized, f"entries/_remapped/{_digest(raw)}/entry.bin",
            str(exc), True, warnings=(str(exc),)
        )
    unsafe = next((_component_unsafe(part) for part in normalized.split("/") if _component_unsafe(part)), None)
    too_long = "path-too-long" in warnings
    if unsafe or too_long:
        reason = unsafe or "path-too-long"
        return PathDecision(
            raw, normalized,
            f"entries/_remapped/{_digest(raw)}/{_safe_basename(normalized)}",
            reason, True, warnings=warnings,
        )
    return PathDecision(raw, normalized, f"entries/{normalized}", "safe", False, warnings=warnings)


def plan_paths(raw_paths: list[str]) -> list[PathDecision]:
    decisions = [initial_decision(raw) for raw in raw_paths]
    groups: dict[str, list[int]] = {}
    for index, decision in enumerate(decisions):
        key = unicodedata.normalize("NFC", decision.normalized_path).casefold()
        groups.setdefault(key, []).append(index)
    for indexes in groups.values():
        if len(indexes) < 2:
            continue
        normalized_values = {decisions[index].normalized_path for index in indexes}
        original_values = {decisions[index].original_path for index in indexes}
        if len(normalized_values) == 1 and len(original_values) > 1:
            kind = "unicode-normalization-collision"
        elif len(normalized_values) > 1:
            kind = "case-insensitive-collision"
        else:
            kind = "duplicate-path"
        for ordinal, index in enumerate(indexes):
            current = decisions[index]
            token = _digest(f"{current.original_path}\x00{ordinal}")
            decisions[index] = replace(
                current,
                preserved_path=f"entries/_remapped/{token}/{_safe_basename(current.normalized_path)}",
                path_status=kind,
                safety_remapped=True,
                conflict_kind=kind,
            )
    return decisions
