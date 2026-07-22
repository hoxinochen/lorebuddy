import hashlib
import json
from pathlib import Path

from lorebuddy.cli import main
from lorebuddy.acquisition.chm_backend import BackendInfo


def test_acquire_inspect_json(tmp_path: Path, project_root: Path, capsys):
    source = tmp_path / "x.chm"
    source.write_bytes(b"fixture")
    assert main(["acquire", "inspect", str(source), "--json"], project_root=project_root) == 0
    output = capsys.readouterr().out
    assert hashlib.sha256(b"fixture").hexdigest() in output
    assert "artifact_id" in output


def test_acquire_run_reports_missing_backend(tmp_path: Path, project_root: Path, monkeypatch, capsys):
    source = tmp_path / "x.chm"
    source.write_bytes(b"fixture")
    monkeypatch.setattr(
        "lorebuddy.acquisition.acquire.EXPECTED_CHM_SHA256",
        hashlib.sha256(b"fixture").hexdigest(),
    )
    monkeypatch.setattr("shutil.which", lambda _: None)
    code = main(["acquire", "run", str(source)], project_root=project_root)
    assert code == 2
    assert "未找到" in capsys.readouterr().err


def test_digest_mismatch_precedes_backend_diagnosis(tmp_path: Path, project_root: Path, monkeypatch, capsys):
    source = tmp_path / "x.chm"
    source.write_bytes(b"wrong")
    monkeypatch.setattr("shutil.which", lambda _: None)
    code = main(["acquire", "run", str(source)], project_root=project_root)
    assert code == 2
    error = capsys.readouterr().err
    assert "SHA-256 不一致" in error
    assert "未找到" not in error


def test_explicit_backend_path_is_passed_without_path_lookup(
    tmp_path: Path, project_root: Path, monkeypatch, capsys
):
    source = tmp_path / "x.chm"
    source.write_bytes(b"fixture")
    digest = hashlib.sha256(b"fixture").hexdigest()
    executable = tmp_path / "tools" / "7zz"
    captured = {}

    class FakeSevenZip:
        def __init__(self, selected):
            captured["selected"] = selected

        def info(self):
            return BackendInfo("fixture", "1", "7zz", "0" * 64)

    monkeypatch.setattr("lorebuddy.cli.SevenZipBackend", FakeSevenZip)
    monkeypatch.setattr("lorebuddy.acquisition.acquire.EXPECTED_CHM_SHA256", digest)
    code = main(
        [
            "acquire", "run", str(source), "--dry-run", "--json",
            "--executable", str(executable),
        ],
        project_root=project_root,
    )
    assert code == 0
    assert captured["selected"] == str(executable)
    assert json.loads(capsys.readouterr().out)["dry_run"] is True
