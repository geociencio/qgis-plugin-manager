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
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


def get_required_fields() -> list[str]:
    """Get list of required metadata fields for QGIS plugins.

    Returns:
        List of field names that must be present in metadata.txt.
    """
    return [
        "name",
        "description",
        "version",
        "qgisMinimumVersion",
        "author",
        "email",
    ]


def get_optional_fields() -> list[str]:
    """Get list of optional but recommended metadata fields.

    Returns:
        List of field names that are optional but recommended.
    """
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


def validate_version(version_str: str) -> bool:
    """Validate version format using semantic versioning.

    Args:
        version_str: Version string to validate.

    Returns:
        True if version matches SemVer format (including pre-releases).
    """
    pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-zA-Z0-9-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][a-zA-Z0-9-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"  # noqa: E501

    # QGIS mínimo a menudo solo tiene X.Y (ej "3.0"). Fallback simple si falla.  # noqa: E501
    if re.match(r"^\d+\.\d+$", version_str):
        return True

    return bool(re.match(pattern, version_str))


def validate_email(email: str) -> bool:
    """Validate email format using a standard regex.

    Args:
        email: Email address to validate.

    Returns:
        True if email format is valid.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format (must start with http or https).

    Args:
        url: URL to validate.

    Returns:
        True if URL format is valid.
    """
    pattern = r"^https?://[^\s]+$"
    return bool(re.match(pattern, url))


def validate_category(category: str) -> bool:
    """Validate plugin category against official allowed values.

    Args:
        category: Category string.

    Returns:
        True if category is valid.
    """
    allowed = ["Vector", "Raster", "Database", "Web", "Processing", "Plugins"]
    return category in allowed


def validate_boolean_field(value: str) -> bool:
    """Validate strict boolean fields (True/False).

    Args:
        value: Field value.

    Returns:
        True if value is exactly "True" or "False".
    """
    return value in ["True", "False"]


def validate_tags(tags: str) -> bool:
    """Validate comma-separated tags format.

    Args:
        tags: Tags string.

    Returns:
        True if tags are comma-separated and not empty.
    """
    if not tags.strip():
        return False  # Empty tags are technically allowed but we want at least one
    # Check if it looks like a list
    parts = [t.strip() for t in tags.split(",")]
    return len(parts) > 0 and all(parts)


def validate_official_compliance(project_root: Path) -> ValidationResult:
    """Check if the project complies with official QGIS repository rules.

    Args:
        project_root: Root directory of the project.

    Returns:
        ValidationResult containing errors and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Prohibited binary extensions
    prohibited = [".so", ".dll", ".exe", ".dylib", ".pyd", ".pyc", ".pyo"]
    found_binaries = []
    for ext in prohibited:
        for p in project_root.rglob(f"*{ext}"):
            found_binaries.append(str(p.relative_to(project_root)))

    if found_binaries:
        errors.append(
            "Official repository prohibits binaries. "
            f"Found: {', '.join(found_binaries)}"
        )

    # 2. License file check (Must be named LICENSE)
    license_file = project_root / "LICENSE"
    if not license_file.exists():
        # Check for common variants to give better advice
        variants = ["LICENSE.txt", "COPYING", "LICENSE.md"]
        found_variant = next((v for v in variants if (project_root / v).exists()), None)
        if found_variant:
            errors.append(
                f"License file must be named exactly 'LICENSE' "
                f"(no extension). Found '{found_variant}'."
            )
        else:
            errors.append("Critical file missing for official repository: 'LICENSE'")

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def validate_project_structure(
    project_root: Path, metadata: dict[str, Any]
) -> ValidationResult:
    """Validate the physical structure of the plugin project.

    Args:
        project_root: Root directory of the project.
        metadata: Plugin metadata dictionary.

    Returns:
        ValidationResult with validation status and messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Essential files
    init_py = project_root / "__init__.py"
    if not init_py.exists():
        errors.append("Critical file missing: '__init__.py'")
    else:
        # Check for classFactory
        try:
            content = init_py.read_text(encoding="utf-8")
            if "def classFactory" not in content:
                errors.append(
                    "Critical function missing in '__init__.py': 'def classFactory'"
                )
        except Exception:
            errors.append("Could not read '__init__.py'")

    # 2. Icon validation
    icon_name = metadata.get("icon", "icon.png")
    icon_path = project_root / icon_name
    if not icon_path.exists():
        if icon_name == "icon.png":
            warnings.append("Recommended file missing: 'icon.png' (standard icon)")
        else:
            errors.append(f"Specified icon file does not exist: '{icon_name}'")

    # 3. Code consistency (Basic check)
    # If the user specifies a class name, it's harder to check without parsing Python,
    # but we can check if there's at least some .py files besides __init__.py
    py_files = list(project_root.glob("*.py"))
    if len(py_files) <= 1:  # Only __init__.py or none
        warnings.append(
            "Project contains very few Python files. Is the plugin logic implemented?"
        )

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)


def validate_metadata(metadata: dict[str, Any]) -> ValidationResult:
    """Validate plugin metadata against QGIS requirements.

    Args:
        metadata: Dictionary containing plugin metadata.

    Returns:
        ValidationResult with validation status and messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required fields
    required = get_required_fields()
    for field in required:
        if field not in metadata or not metadata[field]:
            errors.append(f"Missing required field: '{field}'")

    # Validate name/slug consistency
    if "name" in metadata:
        name = metadata["name"]
        if re.search(r"[\r\n\t]", name):
            errors.append(
                f"Plugin name contains illegal characters (newlines/tabs): '{name}'"
            )

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
            errors.append(f"Invalid email format: '{metadata['email']}'")

    # Validate optional URL fields
    url_fields = ["homepage", "tracker", "repository"]
    for field in url_fields:
        if field in metadata and metadata[field]:
            if not validate_url(metadata[field]):
                warnings.append(f"Invalid URL format in '{field}': '{metadata[field]}'")

    # Check for recommended fields
    if "homepage" not in metadata or not metadata["homepage"]:
        warnings.append("Recommended field 'homepage' is missing")

    if "repository" not in metadata or not metadata["repository"]:
        warnings.append("Recommended field 'repository' is missing")

    if "tags" not in metadata or not metadata["tags"]:
        warnings.append("Recommended field 'tags' is missing")
    elif not validate_tags(metadata["tags"]):
        warnings.append("Tags should be comma-separated list of keywords")

    # Validate category
    if "category" in metadata:
        if not validate_category(metadata["category"]):
            warnings.append(
                f"Unknown category: '{metadata['category']}'. "
                "Allowed: Vector, Raster, Database, Web, Processing, Plugins"
            )

    # Validate boolean fields
    bool_fields = ["experimental", "deprecated", "hasProcessingProvider"]
    for field in bool_fields:
        if field in metadata and metadata[field]:
            warnings.append(
                f"Field '{field}' should be 'True' or 'False'. "
                f"Found: '{metadata[field]}'"
            )

    is_valid = len(errors) == 0

    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
