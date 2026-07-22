"""保守的媒体类型与编码线索检测；不修改来源字节。"""

from __future__ import annotations

import mimetypes
import re
from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class MediaEvidence:
    declared_media_type: str | None
    detected_media_type: str
    confidence: str


@dataclass(frozen=True, slots=True)
class EncodingEvidence:
    declared_encoding: str | None
    detected_encoding_candidate: str | None
    confidence: str
    conflict: bool
    evidence: tuple[str, ...]


_EXTENSION_TYPES = {
    ".htm": "text/html", ".html": "text/html", ".hhc": "text/html",
    ".hhk": "text/html", ".css": "text/css", ".js": "text/javascript",
    ".xml": "application/xml", ".txt": "text/plain", ".svg": "image/svg+xml",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".bmp": "image/bmp", ".webp": "image/webp",
    ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf",
}


def detect_media_type(path: str, prefix: bytes) -> MediaEvidence:
    suffix = PurePosixPath(path).suffix.lower()
    declared = _EXTENSION_TYPES.get(suffix) or mimetypes.guess_type(path)[0]
    signatures = (
        (b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"),
        (b"GIF87a", "image/gif"), (b"GIF89a", "image/gif"),
        (b"BM", "image/bmp"), (b"wOFF", "font/woff"), (b"wOF2", "font/woff2"),
    )
    detected = next((kind for magic, kind in signatures if prefix.startswith(magic)), None)
    stripped = prefix.lstrip().lower()
    if detected is None and (stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html")):
        detected = "text/html"
    if detected is None and stripped.startswith(b"<?xml"):
        detected = "application/xml"
    if detected:
        confidence = "high" if declared in {None, detected} else "conflict"
        return MediaEvidence(declared, detected, confidence)
    if declared:
        return MediaEvidence(declared, declared, "extension-only")
    if b"\x00" not in prefix:
        return MediaEvidence(None, "text/plain", "low")
    return MediaEvidence(None, "application/octet-stream", "unknown")


_META_CHARSET = re.compile(br"charset\s*=\s*[\"']?\s*([a-zA-Z0-9._-]+)", re.I)
_XML_ENCODING = re.compile(br"<\?xml[^>]+encoding\s*=\s*[\"']([^\"']+)", re.I)


def detect_encoding(prefix: bytes, media_type: str) -> EncodingEvidence:
    if not (media_type.startswith("text/") or media_type in {"application/xml", "image/svg+xml"}):
        return EncodingEvidence(None, None, "not-applicable", False, ())
    evidence: list[str] = []
    bom: str | None = None
    for marker, name in ((b"\xef\xbb\xbf", "utf-8-sig"), (b"\xff\xfe", "utf-16le"), (b"\xfe\xff", "utf-16be")):
        if prefix.startswith(marker):
            bom = name
            evidence.append(f"bom:{name}")
            break
    match = _META_CHARSET.search(prefix[:8192]) or _XML_ENCODING.search(prefix[:8192])
    declared = match.group(1).decode("ascii", "ignore").lower() if match else None
    if declared:
        evidence.append(f"declaration:{declared}")
    candidate = bom
    confidence = "high" if bom else "unknown"
    if candidate is None:
        try:
            prefix.decode("utf-8", "strict")
            candidate, confidence = "utf-8", "medium"
            evidence.append("strict-decode:utf-8")
        except UnicodeDecodeError:
            try:
                prefix.decode("gb18030", "strict")
                candidate, confidence = "gb18030", "low"
                evidence.append("strict-decode:gb18030")
            except UnicodeDecodeError:
                evidence.append("strict-decode:none")
    normalized_declared = {"gb2312": "gb2312", "gbk": "gbk", "gb18030": "gb18030", "utf-8": "utf-8"}.get(declared, declared)
    conflict = bool(normalized_declared and candidate and normalized_declared != candidate and not (normalized_declared in {"gbk", "gb2312"} and candidate == "gb18030"))
    return EncodingEvidence(declared, candidate, confidence, conflict, tuple(evidence))
