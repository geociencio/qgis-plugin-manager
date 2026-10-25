"""Metadata validation rules for QGIS plugins."""

from __future__ import annotations

import re
from typing import Any

from ..discovery import slugify
from .fields import (
    get_required_fields,
    validate_boolean_field,
    validate_category,
    validate_email,
    validate_tags,
    validate_url,
    validate_version,
)
from .result import ValidationResult


def _validate_required(metadata: dict[str, Any], errors: list[str]) -> None:
    for field in get_required_fields():
        if field not in metadata or not metadata[field]:
            errors.append(f"Missing required field: '{field}'")


def _validate_name(metadata: dict[str, Any], errors: list[str]) -> None:
    if "name" not in metadata:
        return
    name = metadata["name"]
    if re.search(r"[\r\n\t]", name):
        errors.append(
            f"Plugin name contains illegal characters (newlines/tabs): '{name}'"
        )
    if not slugify(str(name)):
        errors.append(
            "Plugin name must contain at least one ASCII letter or digit "
            "to produce a valid plugin directory name"
        )


def _validate_versions(metadata: dict[str, Any], errors: list[str]) -> None:
    if "version" in metadata and not validate_version(
        metadata["version"], allow_short=False
    ):
        errors.append(
            f"Invalid version format: '{metadata['version']}'. "
            "Expected X.Y.Z (e.g., 1.0.0)"
        )
    if "qgisMinimumVersion" in metadata and not validate_version(
        metadata["qgisMinimumVersion"]
    ):
        errors.append(
            f"Invalid qgisMinimumVersion: '{metadata['qgisMinimumVersion']}'. "
            "Expected X.Y format (e.g., 3.0)"
        )


def _validate_contact(metadata: dict[str, Any], errors: list[str]) -> None:
    if "email" in metadata and not validate_email(metadata["email"]):
        errors.append(f"Invalid email format: '{metadata['email']}'")


def _validate_urls(metadata: dict[str, Any], warnings: list[str]) -> None:
    for field in ("homepage", "tracker", "repository"):
        value = metadata.get(field)
        if value and not validate_url(value):
            warnings.append(f"Invalid URL format in '{field}': '{value}'")


def _validate_recommended(metadata: dict[str, Any], warnings: list[str]) -> None:
    for field in ("homepage", "repository"):
        if not metadata.get(field):
            warnings.append(f"Recommended field '{field}' is missing")
    if not metadata.get("tags"):
        warnings.append("Recommended field 'tags' is missing")
    elif not validate_tags(metadata["tags"]):
        warnings.append("Tags should be comma-separated list of keywords")


def _validate_category(metadata: dict[str, Any], warnings: list[str]) -> None:
    category = metadata.get("category")
    if category and not validate_category(category):
        warnings.append(
            f"Unknown category: '{category}'. "
            "Allowed: Vector, Raster, Database, Web, Processing, Plugins"
        )


def _validate_boolean_fields(metadata: dict[str, Any], warnings: list[str]) -> None:
    for field in ("experimental", "deprecated", "hasProcessingProvider"):
        value = metadata.get(field)
        if value and not validate_boolean_field(str(value)):
            warnings.append(
                f"Field '{field}' should be 'True' or 'False'. Found: '{value}'"
            )


def validate_metadata(metadata: dict[str, Any]) -> ValidationResult:
    """Validate plugin metadata against QGIS requirements."""
    errors: list[str] = []
    warnings: list[str] = []
    _validate_required(metadata, errors)
    _validate_name(metadata, errors)
    _validate_versions(metadata, errors)
    _validate_contact(metadata, errors)
    _validate_urls(metadata, warnings)
    _validate_recommended(metadata, warnings)
    _validate_category(metadata, warnings)
    _validate_boolean_fields(metadata, warnings)
    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)
