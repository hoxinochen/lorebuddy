"""统一验证接口。"""

from .result import ValidationIssue, ValidationResult
from .m2a_delivery import validate_m2a_delivery
from .schema_validator import DocumentLoadError, SchemaValidator, load_document

__all__ = [
    "DocumentLoadError",
    "SchemaValidator",
    "ValidationIssue",
    "ValidationResult",
    "validate_m2a_delivery",
    "load_document",
]
