import json

from lorebuddy.registry import SchemaRegistry
from lorebuddy.validation import SchemaValidator


def test_m1b_profile_schemas_are_registered_and_path_map_fixtures_work(project_root):
    registry = SchemaRegistry.from_project_root(project_root)
    schema_ids = {entry.schema_id: entry.status for entry in registry.list_entries()}
    expected = {
        "m1b.source-path-map-record@0.1.0",
        "m1b.duplicate-report@0.1.0",
        "m1b.acquisition-report@0.1.0",
        "m1b.acquisition-validation-report@0.1.0",
        "m1b.acquisition-workdir@0.1.0",
        "m1b.backend-execution@0.1.0",
    }
    assert expected <= schema_ids.keys()
    assert all(schema_ids[schema_id] == "experimental" for schema_id in expected)
    validator = SchemaValidator(registry)
    fixture_root = project_root / "fixtures" / "m1b" / "expected"
    valid = json.loads((fixture_root / "valid-path-map.json").read_text())
    invalid = json.loads((fixture_root / "invalid-path-map.json").read_text())
    assert validator.validate_data(valid, valid["schema"]).valid
    assert not validator.validate_data(invalid, invalid["schema"]).valid
