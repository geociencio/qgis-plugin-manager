"""Validation result type shared by all validation rules."""

from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of metadata validation.

    Attributes:
        is_valid: Boolean indicating if the validation passed.
        errors: List of error messages (blocking).
        warnings: List of warning messages (non-blocking).
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]
