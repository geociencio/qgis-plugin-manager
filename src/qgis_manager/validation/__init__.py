"""Metadata, repository and structure validation for QGIS plugins."""

from .fields import (
    get_required_fields,
    validate_boolean_field,
    validate_category,
    validate_email,
    validate_tags,
    validate_url,
    validate_version,
)
from .metadata import validate_metadata
from .repository import validate_official_compliance
from .result import ValidationResult
from .structure import validate_project_structure

__all__ = [
    "ValidationResult",
    "get_required_fields",
    "validate_boolean_field",
    "validate_category",
    "validate_email",
    "validate_metadata",
    "validate_official_compliance",
    "validate_project_structure",
    "validate_tags",
    "validate_url",
    "validate_version",
]
