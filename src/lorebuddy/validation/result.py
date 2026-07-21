"""结构化验证结果。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    path: str
    code: str
    message: str
    validator: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    schema_id: str
    errors: tuple[ValidationIssue, ...]
    file: str | None
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "schema_id": self.schema_id,
            "errors": [asdict(error) for error in self.errors],
            "file": self.file,
            "summary": self.summary,
        }
