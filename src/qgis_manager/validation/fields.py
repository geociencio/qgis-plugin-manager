"""Field-level validators for QGIS plugin metadata."""

import re


def get_required_fields() -> list[str]:
    """Get list of required metadata fields for QGIS plugins.

    Returns:
        List of field names that must be present in metadata.txt.
    """
    return [
        "name",
        "description",
        "about",
        "version",
        "qgisMinimumVersion",
        "author",
        "email",
    ]


def validate_version(version_str: str, allow_short: bool = True) -> bool:
    """Validate version format using semantic versioning.

    Args:
        version_str: Version string to validate.
        allow_short: Accept the ``X.Y`` form used by ``qgisMinimumVersion``.
            Plugin versions should pass ``False`` because the QGIS repository
            expects ``X.Y.Z``.

    Returns:
        True if version matches SemVer format (including pre-releases).
    """
    pattern = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9A-Za-z-]*))*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"  # noqa: E501

    # QGIS minimum version is often only X.Y (e.g. "3.0").
    if allow_short and re.match(r"^\d+\.\d+$", version_str):
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
