from __future__ import annotations

from pathlib import Path

from lorebuddy.cli import main
from lorebuddy.publishing import (
    build_gpt_project_export,
    publish_obsidian_baseline,
    validate_gpt_project_export,
)
from test_obsidian_publisher import _m1c2a_fixture


def _baseline(tmp_path: Path) -> Path:
    source = _m1c2a_fixture(tmp_path)
    output = tmp_path / "m1c3"
    publish_obsidian_baseline(source, output)
    return output


def test_gpt_export_preserves_each_note_once_and_is_deterministic(
    tmp_path: Path,
) -> None:
    source = _baseline(tmp_path)
    first = tmp_path / "gpt-first"
    second = tmp_path / "gpt-second"

    first_report = build_gpt_project_export(
        source,
        first,
        max_bundle_bytes=10_000,
    )
    second_report = build_gpt_project_export(
        source,
        second,
        max_bundle_bytes=10_000,
    )

    assert first_report["valid"]
    assert first_report["summary"]["entry_count"] == 2
    assert first_report["summary"]["upload_file_count"] == 3
    assert first_report == second_report
    assert {
        path.relative_to(first).as_posix()
        for path in first.rglob("*")
        if path.is_file()
    } == {
        path.relative_to(second).as_posix()
        for path in second.rglob("*")
        if path.is_file()
    }
    for relative in (
        path.relative_to(first)
        for path in first.rglob("*")
        if path.is_file()
    ):
        assert (first / relative).read_bytes() == (second / relative).read_bytes()

    bundle = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(first.glob("*-content-*.md"))
    )
    assert bundle.count("<!-- LOREBUDDY_ENTRY ") == 2
    assert "## 本包内容导航" in bundle
    assert "Book：2 个 Entry" in bundle
    assert "source_path: \"book/one.htm\"" in bundle
    assert "navigation_paths:" in bundle
    contents = (first / "01-CONTENTS.md").read_text(encoding="utf-8")
    assert "## 任务检索路由" in contents
    assert "默认采用最新适用版本" in contents


def test_gpt_export_validator_detects_note_mutation(tmp_path: Path) -> None:
    source = _baseline(tmp_path)
    output = tmp_path / "gpt"
    build_gpt_project_export(source, output, max_bundle_bytes=10_000)
    bundle = output / "02-content-01.md"
    bundle.write_bytes(
        bundle.read_bytes().replace("未解析目标".encode(), "已篡改目标".encode(), 1)
    )

    result = validate_gpt_project_export(source, output)

    assert not result["valid"]
    assert any(
        error["code"] in {"ENTRY_BYTES", "INVALID_BUNDLE"}
        for error in result["errors"]
    )


def test_gpt_export_cli_exit_codes(tmp_path: Path) -> None:
    source = _baseline(tmp_path)
    output = tmp_path / "gpt"

    assert (
        main(
            [
                "gpt-export",
                "build",
                str(source),
                "--output",
                str(output),
                "--max-bundle-bytes",
                "10000",
                "--json",
            ],
            project_root=tmp_path,
        )
        == 0
    )
    assert (
        main(
            [
                "gpt-export",
                "validate",
                str(source),
                str(output),
                "--json",
            ],
            project_root=tmp_path,
        )
        == 0
    )
    (output / "unexpected.txt").write_text("user file", encoding="utf-8")
    assert (
        main(
            [
                "gpt-export",
                "validate",
                str(source),
                str(output),
                "--json",
            ],
            project_root=tmp_path,
        )
        == 1
    )
