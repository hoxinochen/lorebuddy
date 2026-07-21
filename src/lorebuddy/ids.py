"""稳定身份基础工具。"""

from __future__ import annotations

import re
import uuid
from collections.abc import Iterable


LOREBUDDY_NAMESPACE = uuid.UUID("a90f68a7-6fe9-5de8-bcdf-f85872a6f27b")
_KIND_RE = re.compile(r"^[a-z][a-z0-9.-]{1,63}$")


class IdentityError(ValueError):
    pass


def stable_id(kind: str, natural_key: str) -> str:
    """由显式类型和不透明自然键确定性派生 UUIDv5 URN。"""

    if not _KIND_RE.fullmatch(kind):
        raise IdentityError("kind 必须是 2～64 位小写命名空间标识")
    if not isinstance(natural_key, str) or not natural_key:
        raise IdentityError("natural_key 必须是非空字符串")
    value = uuid.uuid5(LOREBUDDY_NAMESPACE, f"{kind}\x00{natural_key}")
    return value.urn


def parse_uuid_urn(value: str) -> uuid.UUID:
    if not isinstance(value, str) or not value.startswith("urn:uuid:"):
        raise IdentityError("ID 必须是 UUID URN")
    try:
        return uuid.UUID(value.removeprefix("urn:uuid:"))
    except ValueError as exc:
        raise IdentityError("ID 不是有效 UUID URN") from exc


def short_id(value: str, length: int = 8) -> str:
    if not 8 <= length <= 32:
        raise IdentityError("short-id 长度必须在 8～32 之间")
    return parse_uuid_urn(value).hex[:length]


def assert_unique_short_ids(values: Iterable[str], length: int = 8) -> None:
    seen: dict[str, str] = {}
    for value in values:
        candidate = short_id(value, length)
        if candidate in seen and seen[candidate] != value:
            raise IdentityError(
                f"short-id 冲突：{candidate} 同时映射 {seen[candidate]} 与 {value}"
            )
        seen[candidate] = value
