import pytest

from lorebuddy.acquisition.paths import UnsafePathError, normalize_entry_path, plan_paths


@pytest.mark.parametrize("value", ["../x", "/x", "C:\\x", "a/%2e%2e/x", "a\x00b", "", "."])
def test_unsafe_paths_are_rejected(value):
    with pytest.raises(UnsafePathError):
        normalize_entry_path(value)


def test_path_normalization_is_nfc_and_posix():
    normalized, warnings = normalize_entry_path("a\\e\u0301//file.html")
    assert normalized == "a/é/file.html"
    assert "unicode-normalized" in warnings


def test_case_and_unicode_collisions_are_remapped():
    decisions = plan_paths(["A/File.htm", "a/file.htm", "é.txt", "e\u0301.txt"])
    assert all(item.safety_remapped for item in decisions)
    assert decisions[0].conflict_kind == "case-insensitive-collision"
    assert decisions[2].conflict_kind == "unicode-normalization-collision"
    assert len({item.preserved_path for item in decisions}) == 4


def test_windows_reserved_and_long_paths_are_remapped():
    decisions = plan_paths(["CON.txt", "a" * 241 + ".txt"])
    assert [item.safety_remapped for item in decisions] == [True, True]
