from __future__ import annotations

from copy import deepcopy

from lorebuddy.validation import validate_rule_assertion


def _candidate() -> dict:
    return {
        "schema": "m2.rule-assertion@0.1.0",
        "id": "urn:uuid:11111111-1111-4111-8111-111111111111",
        "ruleset": {"system": "example-trpg", "version": "0.1", "profile_id": "pilot"},
        "assertion": {
            "trigger": [{"kind": "trigger", "text": "When the declared event occurs."}],
            "conditions": [{"kind": "condition", "text": "The stated condition is true."}],
            "activities": [{"kind": "activity", "text": "Perform the declared operation."}],
            "effects": [{"kind": "effect", "text": "Apply the declared outcome."}],
            "prerequisites": [{"kind": "prerequisite", "text": "The declared prerequisite is met."}],
            "choices": [{"kind": "choice", "text": "Select one declared option."}],
        },
        "source_bindings": [
            {
                "entry_id": "urn:uuid:22222222-2222-4222-8222-222222222222",
                "source_path": "book/entry.md",
                "body_range": {"unit": "lines", "start": 10, "end": 12},
            }
        ],
        "review_status": "candidate",
    }


def test_candidate_rule_assertion_is_valid() -> None:
    result = validate_rule_assertion(_candidate())
    assert result.valid, result.to_dict()


def test_approved_rule_assertion_requires_matching_review_record() -> None:
    assertion = _candidate()
    assertion["review_status"] = "approved"
    missing = validate_rule_assertion(assertion)
    assert not missing.valid
    assert any(error.code == "RULE_REVIEW_RECORD_REQUIRED" for error in missing.errors)

    assertion["review_record"] = {
        "review_id": "urn:uuid:33333333-3333-4333-8333-333333333333",
        "decision": "rejected",
        "reviewer": "human-reviewer",
        "reason": "The candidate is not admitted.",
    }
    mismatch = validate_rule_assertion(assertion)
    assert not mismatch.valid
    assert any(error.code == "RULE_REVIEW_DECISION_MISMATCH" for error in mismatch.errors)


def test_rule_assertion_rejects_domain_specific_fields_and_invalid_range() -> None:
    assertion = deepcopy(_candidate())
    assertion["assertion"]["effects"][0]["damage"] = 8
    schema_result = validate_rule_assertion(assertion)
    assert not schema_result.valid
    assert any(error.code == "RULE_SCHEMA_ADDITIONALPROPERTIES" for error in schema_result.errors)

    assertion = deepcopy(_candidate())
    assertion["source_bindings"][0]["source_path"] = "../outside.md"
    assertion["source_bindings"][0]["body_range"]["end"] = 10
    cross_field_result = validate_rule_assertion(assertion)
    assert not cross_field_result.valid
    codes = {error.code for error in cross_field_result.errors}
    assert {"RULE_SOURCE_PATH", "RULE_SOURCE_RANGE"} <= codes
