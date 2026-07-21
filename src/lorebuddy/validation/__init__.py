"""统一验证接口。"""

from .result import ValidationIssue, ValidationResult
from .schema_validator import DocumentLoadError, SchemaValidator, load_document

__all__ = [
    "DocumentLoadError",
    "SchemaValidator",
    "ValidationIssue",
    "ValidationResult",
    "load_document",
]
