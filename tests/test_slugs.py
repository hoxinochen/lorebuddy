from __future__ import annotations

import unicodedata

from lorebuddy.ids import stable_id
from lorebuddy.slugs import note_filename, stable_slug


def test_english_slug_normalizes_space_case_and_punctuation() -> None:
    assert stable_slug("  Hello, WORLD.  ") == "hello-world"


def test_chinese_title_uses_safe_deterministic_fallback() -> None:
    assert stable_slug("专注") == "node"
    assert unicodedata.is_normalized("NFC", stable_slug("专注"))


def test_windows_reserved_name_is_disarmed() -> None:
    assert stable_slug("CON") == "con-note"


def test_empty_slug_and_trailing_dots_are_safe() -> None:
    assert stable_slug(" ... ") == "node"
    assert not stable_slug("name. ").endswith((" ", "."))


def test_note_filename_has_stable_collision_suffix_and_length() -> None:
    identity = stable_id("knowledge.node", "approved-boundary-01")
    filename = note_filename("Same Title", identity, max_bytes=40)
    assert filename.startswith("same-title--")
    assert filename.endswith(".md")
    assert len(filename.encode("utf-8")) <= 40


def test_same_title_different_identity_is_disambiguated() -> None:
    first = note_filename("Same Title", stable_id("knowledge.node", "boundary-01"))
    second = note_filename("Same Title", stable_id("knowledge.node", "boundary-02"))
    assert first != second
    assert first.casefold() != second.casefold()
