from __future__ import annotations

import uuid

import pytest

from lorebuddy.ids import IdentityError, assert_unique_short_ids, short_id, stable_id


def test_stable_id_is_deterministic_and_title_independent_by_contract() -> None:
    first = stable_id("source.entry", "artifact-01\x00directory-record-10")
    second = stable_id("source.entry", "artifact-01\x00directory-record-10")
    other = stable_id("source.entry", "artifact-01\x00directory-record-11")
    assert first == second
    assert first != other
    assert uuid.UUID(first.removeprefix("urn:uuid:")).version == 5


def test_short_id_is_deterministic() -> None:
    identity = stable_id("knowledge.node", "approved-boundary-01")
    assert short_id(identity) == short_id(identity)
    assert len(short_id(identity)) == 8


def test_short_id_collision_is_detected() -> None:
    first = "urn:uuid:12345678-0000-5000-8000-000000000001"
    second = "urn:uuid:12345678-0000-5000-8000-000000000002"
    with pytest.raises(IdentityError, match="short-id 冲突"):
        assert_unique_short_ids([first, second])


@pytest.mark.parametrize(("kind", "key"), [("Bad Kind", "x"), ("a", "x"), ("valid.kind", "")])
def test_invalid_identity_input_is_rejected(kind: str, key: str) -> None:
    with pytest.raises(IdentityError):
        stable_id(kind, key)
