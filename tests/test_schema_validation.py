from __future__ import annotations

from pathlib import Path

from lorebuddy.registry import SchemaRegistry
from lorebuddy.validation import SchemaValidator, load_document


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = PROJECT_ROOT / "fixtures" / "m1a"


def _validator() -> SchemaValidator:
    return SchemaValidator(SchemaRegistry.from_project_root(PROJECT_ROOT))


def test_all_valid_and_invalid_fixtures_have_expected_result() -> None:
    validator = _validator()
    counts = {"valid": 0, "invalid": 0}
    schema_ids = {"valid": set(), "invalid": set()}
    for expectation in counts:
        for path in sorted((FIXTURE_ROOT / expectation).glob("*.json")):
            data = load_document(path)
            result = validator.validate_data(data, data["schema"], file=str(path))
            assert result.valid is (expectation == "valid"), result.to_dict()
            counts[expectation] += 1
            schema_ids[expectation].add(data["schema"])
    assert counts == {"valid": 8, "invalid": 8}
    registered = {
        entry.schema_id
        for entry in validator.registry.list_entries()
        if entry.schema_id.startswith("core.")
    }
    assert schema_ids == {"valid": registered, "invalid": registered}


def test_validator_reports_json_pointer_for_invalid_path() -> None:
    validator = _validator()
    path = FIXTURE_ROOT / "invalid" / "entry.json"
    data = load_document(path)
    result = validator.validate_data(data, data["schema"], file=str(path))
    assert not result.valid
    assert any(error.path == "/storage_path" for error in result.errors)
    assert all(error.code.startswith("SCHEMA_") for error in result.errors)


def test_unknown_schema_id_returns_structured_failure() -> None:
    result = _validator().validate_data({}, "core.unknown@0.1.0")
    assert not result.valid
    assert result.errors[0].code == "UNKNOWN_SCHEMA"
    assert result.schema_id == "core.unknown@0.1.0"


def test_yaml_duplicate_key_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.yaml"
    path.write_text("schema: core.package-manifest@0.1.0\nschema: duplicate\n", encoding="utf-8")
    result = _validator().validate_file("core.package-manifest@0.1.0", path)
    assert not result.valid
    assert result.errors[0].code == "DOCUMENT_LOAD_ERROR"


def test_valid_yaml_document_is_supported(tmp_path: Path) -> None:
    source = FIXTURE_ROOT / "valid" / "source-mapping.json"
    data = load_document(source)
    path = tmp_path / "source-mapping.yaml"
    import yaml

    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    result = _validator().validate_file(data["schema"], path)
    assert result.valid, result.to_dict()
