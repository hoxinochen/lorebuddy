import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path

from lorebuddy.acquisition import acquire
from lorebuddy.acquisition.acquire import run_acquisition
from lorebuddy.acquisition.chm_backend import BackendInfo, ExecutionResult
from lorebuddy.validation.source_semantics import validate_acquisition


@dataclass
class FixtureBackend:
    fixture: Path

    def info(self):
        return BackendInfo("fixture", "1.0", "fixture", "0" * 64)

    def extract(self, source, output, timeout):
        shutil.copytree(self.fixture, output)
        return ExecutionResult(self.info(), ("fixture", "extract"), 0, "", "", 0.0)


def _run(tmp_path: Path, project_root: Path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "fixture.chm"
    source.write_bytes(b"synthetic chm container")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    old = acquire.EXPECTED_CHM_SHA256
    acquire.EXPECTED_CHM_SHA256 = digest
    try:
        run_acquisition(
            source,
            tmp_path / "out",
            backend=FixtureBackend(project_root / "fixtures" / "m1b" / "synthetic"),
            project_root=project_root,
        )
    finally:
        acquire.EXPECTED_CHM_SHA256 = old
    return next((tmp_path / "out").iterdir())


def test_acquisition_is_valid_and_deterministic(tmp_path: Path, project_root: Path):
    first = _run(tmp_path / "first", project_root)
    second = _run(tmp_path / "second", project_root)
    first_files = sorted((first / "inventory").glob("*"))
    second_files = sorted((second / "inventory").glob("*"))
    assert [path.name for path in first_files] == [path.name for path in second_files]
    for left, right in zip(first_files, second_files, strict=True):
        assert left.read_bytes() == right.read_bytes(), left.name
    assert validate_acquisition(first, project_root=project_root)["valid"]


def test_tampered_entry_fails_validation(tmp_path: Path, project_root: Path):
    artifact = _run(tmp_path, project_root)
    saved = next((artifact / "extracted" / "entries").rglob("*.css"))
    saved.write_bytes(b"changed")
    result = validate_acquisition(artifact, project_root=project_root)
    assert not result["valid"]
    assert {error["code"] for error in result["errors"]} & {"SIZE_MISMATCH", "DIGEST_MISMATCH"}
