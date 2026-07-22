from lorebuddy.acquisition.duplicates import build_duplicate_report


def _entry(identifier, path, digest, conflict=None):
    return {
        "id": identifier,
        "original_path": path,
        "digest": digest,
        "extensions": {"m1b-acquisition": {"conflict_kind": conflict}},
    }


def test_duplicate_report_keeps_distinct_entries():
    entries = [
        _entry("a", "one/x.txt", "sha256:1"),
        _entry("b", "two/y.txt", "sha256:1"),
        _entry("c", "three/x.txt", "sha256:2", "case-insensitive-collision"),
    ]
    report = build_duplicate_report(entries)
    assert report["summary"]["byte_identical_groups"] == 1
    assert report["summary"]["same_name_different_content_groups"] == 1
    assert report["summary"]["path_conflict_entries"] == 1
