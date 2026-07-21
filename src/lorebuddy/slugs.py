"""跨平台安全的可读 Slug 与 Note 文件名。"""

from __future__ import annotations

import re
import unicodedata

from .ids import short_id


WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)
_SEPARATOR_RE = re.compile(r"[-_\s]+")
_NON_ASCII_SAFE_RE = re.compile(r"[^a-z0-9-]+")


def stable_slug(title: str, *, fallback: str = "node", max_bytes: int = 80) -> str:
    """生成 ASCII Lowercase Slug；中文等非 ASCII 标题安全回退。

    M1-A 不引入拼音/转写依赖。可读 Slug 一旦经人工批准，应作为 Metadata
    持久化；标题变化不得自动重算已发布 Slug。
    """

    if max_bytes < 8:
        raise ValueError("max_bytes 不能小于 8")
    normalized = unicodedata.normalize("NFC", title or "").casefold().strip(" .")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    candidate = _SEPARATOR_RE.sub("-", ascii_text)
    candidate = _NON_ASCII_SAFE_RE.sub("-", candidate).strip("-.")
    candidate = re.sub(r"-+", "-", candidate)
    if not candidate:
        candidate = fallback
    candidate = _NON_ASCII_SAFE_RE.sub("-", candidate.casefold()).strip("-.") or "node"
    if candidate in WINDOWS_RESERVED:
        candidate = f"{candidate}-note"
    encoded = candidate.encode("utf-8")
    if len(encoded) > max_bytes:
        candidate = encoded[:max_bytes].decode("utf-8", "ignore").rstrip("-.") or "node"
    return unicodedata.normalize("NFC", candidate)


def note_filename(title: str, identity: str, *, max_bytes: int = 120) -> str:
    suffix = f"--{short_id(identity)}.md"
    slug_budget = max_bytes - len(suffix.encode("utf-8"))
    if slug_budget < 8:
        raise ValueError("max_bytes 太小，无法容纳稳定消歧后缀")
    slug = stable_slug(title, max_bytes=slug_budget)
    return f"{slug}{suffix}"
