# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Metadata validation for QGIS plugins.

This module provides functions to validate metadata.txt files against
QGIS plugin repository requirements and best practices.

Functions:
    validate_metadata: Validate plugin metadata dictionary
    validate_version: Check version format (X.Y.Z)
    validate_email: Check email format
    validate_url: Check URL format
    get_required_fields: Get list of required metadata fields
"""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of metadata validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


def get_required_fields() -> list[str]:
    """Get list of required metadata fields for QGIS plugins."""
    return [
        "name",
        "description",
        "version",
        "qgisMinimumVersion",
        "author",
        "email",
    ]


def get_optional_fields() -> list[str]:
    """Get list of optional but recommended metadata fields."""
    return [
        "homepage",
        "tracker",
        "repository",
        "tags",
        "category",
        "icon",
        "experimental",
        "deprecated",
        "qgisMaximumVersion",
        "changelog",
        "about",
    ]


def validate_version(version: str) -> bool:
    """
    Validate version format.

    Args:
        version: Version string to validate

    Returns:
        True if version matches X.Y.Z format
    """
    pattern = r"^\d+\.\d+(\.\d+)?$"
    return bool(re.match(pattern, version))


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL format is valid (http/https)
    """
    pattern = r"^https?://[^\s]+$"
    return bool(re.match(pattern, url))


def validate_metadata(metadata: dict[str, Any]) -> ValidationResult:
    """
    Validate plugin metadata against QGIS requirements.

    Args:
        metadata: Dictionary containing plugin metadata

    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []

    # Check required fields
    required = get_required_fields()
    for field in required:
        if field not in metadata or not metadata[field]:
            errors.append(f"Missing required field: '{field}'")

    # Validate version format
    if "version" in metadata:
        if not validate_version(metadata["version"]):
            errors.append(
                f"Invalid version format: '{metadata['version']}'. "
                "Expected X.Y.Z (e.g., 1.0.0)"
            )

    # Validate qgisMinimumVersion format
    if "qgisMinimumVersion" in metadata:
        if not validate_version(metadata["qgisMinimumVersion"]):
            errors.append(
                f"Invalid qgisMinimumVersion: '{metadata['qgisMinimumVersion']}'. "
                "Expected X.Y format (e.g., 3.0)"
            )

    # Validate email format
    if "email" in metadata:
        if not validate_email(metadata["email"]):
            errors.append(
                f"Invalid email format: '{metadata['email']}'"
            )

    # Validate optional URL fields
    url_fields = ["homepage", "tracker", "repository"]
    for field in url_fields:
        if field in metadata and metadata[field]:
            if not validate_url(metadata[field]):
                warnings.append(
                    f"Invalid URL format in '{field}': '{metadata[field]}'"
                )

    # Check for recommended fields
    if "homepage" not in metadata or not metadata["homepage"]:
        warnings.append("Recommended field 'homepage' is missing")

    if "repository" not in metadata or not metadata["repository"]:
        warnings.append("Recommended field 'repository' is missing")

    if "tags" not in metadata or not metadata["tags"]:
        warnings.append("Recommended field 'tags' is missing")

    is_valid = len(errors) == 0

    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
