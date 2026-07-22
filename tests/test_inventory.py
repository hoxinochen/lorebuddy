from pathlib import Path

from lorebuddy.acquisition.inventory import (
    enumerate_regular_files,
    mark_duplicates,
    preserve_entries,
    summarize_inventory,
)
from lorebuddy.ids import stable_id


def test_inventory_preserves_bytes_and_ids(tmp_path: Path):
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / "a.html").write_bytes(b"<html>\r\nbody</html>")
    (staging / "b.txt").write_bytes(b"same")
    (staging / "c.txt").write_bytes(b"same")
    candidates, rejected = enumerate_regular_files(staging)
    artifact_id = stable_id("source-artifact", "fixture")
    records = preserve_entries(candidates, artifact_id, tmp_path / "preserved")
    mark_duplicates(records)
    summary = summarize_inventory(records, rejected)
    assert summary["entry_count"] == 3
    assert summary["total_bytes"] == sum(len(path.read_bytes()) for path in staging.iterdir())
    assert records[1]["id"] != records[2]["id"]
    assert all(
        record["extensions"]["m1b-acquisition"]["entry_kind"] == "regular-file"
        for record in records
    )
    assert records[1]["extensions"]["m1b-acquisition"]["duplicate_status"] == "byte-identical"
    assert (tmp_path / "preserved" / records[0]["storage_path"]).read_bytes() == b"<html>\r\nbody</html>"


def test_non_regular_files_are_rejected(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    target = root / "target"
    target.write_text("x")
    (root / "link").symlink_to(target)
    entries, rejected = enumerate_regular_files(root)
    assert [entry.original_path for entry in entries] == ["target"]
    assert rejected == [{"path": "link", "reason": "symbolic-link"}]
