"""M2 Rule Assertion 的 Schema 与跨字段确定性校验。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .result import ValidationIssue, ValidationResult


SCHEMA_ID = "m2.rule-assertion@0.1.0"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "rule-assertion.schema.json"


def _pointer(parts: list[Any]) -> str:
    if not parts:
        return "/"
    return "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in parts)


def _issue(path: str, code: str, message: str) -> ValidationIssue:
    return ValidationIssue(path=path, code=code, message=message)


def validate_rule_assertion(
    data: Any, *, schema_path: Path | str = DEFAULT_SCHEMA_PATH
) -> ValidationResult:
    """验证 Rule Assertion 结构、来源范围和审核状态，不执行规则语义。"""

    path = Path(schema_path)
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return ValidationResult(
            False,
            SCHEMA_ID,
            (_issue("/", "RULE_SCHEMA_LOAD_ERROR", str(exc)),),
            str(path),
            "Rule Assertion Schema 加载失败",
        )

    validator = Draft202012Validator(schema)
    errors = [
        _issue(
            _pointer(list(error.absolute_path)),
            f"RULE_SCHEMA_{str(error.validator).upper()}",
            error.message,
        )
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    ]
    if errors:
        return ValidationResult(False, SCHEMA_ID, tuple(errors), None, f"Schema 验证失败：{len(errors)} 个错误")

    assert isinstance(data, dict)
    status = data["review_status"]
    record = data.get("review_record")
    if status in {"approved", "rejected"}:
        if record is None:
            errors.append(_issue("/review_record", "RULE_REVIEW_RECORD_REQUIRED", "终态必须有人工 review_record"))
        elif record["decision"] != status:
            errors.append(_issue("/review_record/decision", "RULE_REVIEW_DECISION_MISMATCH", "decision 必须与 review_status 一致"))
    elif record is not None:
        errors.append(_issue("/review_record", "RULE_REVIEW_RECORD_EARLY", "candidate / in_review 不得携带终态 review_record"))

    for index, binding in enumerate(data["source_bindings"]):
        source_path = binding["source_path"]
        body_range = binding["body_range"]
        if source_path.startswith("/") or "\\" in source_path or ".." in source_path.split("/"):
            errors.append(_issue(f"/source_bindings/{index}/source_path", "RULE_SOURCE_PATH", "source_path 必须是受限相对路径"))
        if body_range["end"] <= body_range["start"]:
            errors.append(_issue(f"/source_bindings/{index}/body_range", "RULE_SOURCE_RANGE", "body_range 必须满足 end > start"))

    valid = not errors
    return ValidationResult(
        valid,
        SCHEMA_ID,
        tuple(errors),
        None,
        "Rule Assertion 验证通过" if valid else f"Rule Assertion 验证失败：{len(errors)} 个错误",
    )
