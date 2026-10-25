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
Plugin discovery and metadata extraction utilities.

This module provides functions to automatically discover QGIS plugin projects,
read metadata.txt files, and identify source files for deployment.
"""

import configparser
import logging
import re
import unicodedata
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .ignore import IgnoreMatcher
from .metadata import (
    format_general_entries,
    update_general_keys,
    write_text_atomic,
)
from .toml_utils import get_project_version

logger = logging.getLogger(__name__)

#: A slug that is safe to use as a directory/module name inside a QGIS profile.
_SLUG_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

#: Names that cannot be used as a directory on Windows.
_RESERVED_SLUGS = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


def slugify(text: str) -> str:
    """Convert text to a safe ASCII directory/module name slug.

    Non-ASCII characters are transliterated or dropped (``Café`` -> ``cafe``),
    spaces and separators collapse to underscores, and a leading underscore is
    added when the result would start with a digit so it remains a valid Python
    identifier.  An empty string is returned when no ASCII alphanumeric
    character is left; callers must reject that result.

    Args:
        text: Input string to be converted into a slug.

    Returns:
        A lowercase ASCII slug using only letters, digits and underscores.
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    if ascii_text and ascii_text[0].isdigit():
        return f"_{ascii_text}"
    return ascii_text


def validate_slug(slug: str, *, source: str = "plugin") -> str:
    """Validate a plugin slug before using it in a filesystem operation.

    Empty slugs are the dangerous case: joining them with a plugins directory
    yields the directory itself, so a recursive delete/sync could affect every
    installed plugin.  Only ASCII lowercase letters, digits and underscores are
    accepted (the first character may be an underscore).

    Args:
        slug: Slug to validate.
        source: Human-readable origin of the slug, used in the error message.

    Returns:
        The validated slug.

    Raises:
        ValueError: If the slug is empty or contains unsafe characters.
    """
    if not slug or not _SLUG_RE.fullmatch(slug) or slug in _RESERVED_SLUGS:
        raise ValueError(
            f"Invalid {source} slug {slug!r}. The name must contain at least "
            "one ASCII letter or digit and may only use letters, digits and "
            "underscores after normalization."
        )
    return slug


def find_project_root(start_path: Path) -> Path:
    """Find the project root by looking for metadata.txt or pyproject.toml.

    Args:
        start_path: Directory to start the search from.

    Returns:
        The directory containing metadata.txt or pyproject.toml.

    Raises:
        FileNotFoundError: If no project root is found by searching upwards.
    """
    current = start_path.resolve()
    while current != current.parent:
        if (current / "metadata.txt").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not find a project root (missing metadata.txt or pyproject.toml)."
    )


def get_plugin_metadata(project_root: Path) -> dict[str, Any]:
    """Read metadata.txt and return as a dict.

    Falls back to basic info (name and slug) if the file is missing or malformed.

    Args:
        project_root: Root directory of the QGIS plugin project.

    Returns:
        A dictionary containing the metadata fields found in [general].
    """
    metadata_path = project_root / "metadata.txt"
    if not metadata_path.exists():
        # Minimum metadata for tool-only projects
        return {
            "name": project_root.name,
            "slug": slugify(project_root.name),
            "version": "unknown",
        }

    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str  # type: ignore[method-assign, assignment] # Preserve case
    try:
        config.read(metadata_path, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            config.read(metadata_path, encoding="latin-1")
        except Exception as e:
            logger.error(f"Critical error in get_plugin_metadata (read latin-1): {e}")
            return {"name": project_root.name, "slug": slugify(project_root.name)}
    except Exception as e:
        logger.error(f"Critical error in get_plugin_metadata (read utf-8): {e}")
        # Fallback if file exists but is empty/malformed
        return {"name": project_root.name, "slug": slugify(project_root.name)}

    try:
        metadata = dict(config["general"])
    except Exception as e:
        logger.error(f"Error accessing ['general'] in metadata.txt: {e}")
        return {"name": project_root.name, "slug": slugify(project_root.name)}

    if "name" not in metadata:
        metadata["name"] = project_root.name

    metadata["slug"] = slugify(metadata["name"])
    return metadata


def save_plugin_metadata(project_root: Path, metadata: dict[str, Any]) -> None:
    """Save metadata back to metadata.txt preserving comments and other sections.

    Only changed keys are rewritten; untouched lines, comments, blank lines and
    custom sections keep their original formatting.  The write is atomic.

    Args:
        project_root: Root directory of the QGIS plugin project.
        metadata: Dictionary with project metadata to persist.

    Raises:
        OSError: If the file cannot be written.
    """
    metadata_path = project_root / "metadata.txt"
    updates = {str(key): str(value) for key, value in metadata.items() if key != "slug"}

    if metadata_path.exists():
        current = get_plugin_metadata(project_root)
        current.pop("slug", None)
        updates = {
            key: value for key, value in updates.items() if current.get(key) != value
        }
        if not updates:
            return

        text = metadata_path.read_text(encoding="utf-8")
        new_text = update_general_keys(text, updates)
    else:
        lines = ["[general]", *format_general_entries(updates)]
        new_text = "\n".join(lines) + "\n"

    try:
        write_text_atomic(metadata_path, new_text)
    except OSError as exc:
        logger.error(f"Error saving metadata.txt: {exc}")
        raise


def sync_metadata_version(project_root: Path) -> bool:
    """Sync the metadata.txt version from pyproject.toml.

    Args:
        project_root: Root directory of the plugin project.

    Returns:
        True if metadata.txt was updated, False if it was already in sync
        or if pyproject.toml has no version.
    """
    version = get_project_version(project_root / "pyproject.toml")
    if not version:
        return False

    metadata = get_plugin_metadata(project_root)
    if metadata.get("version") == version:
        return False

    metadata["version"] = version
    save_plugin_metadata(project_root, metadata)
    return True


def get_source_files(project_root: Path, include_dev: bool = False) -> Iterator[Path]:
    """Dynamically discover source files and directories to copy.

    Args:
        project_root: Root directory of the project.
        include_dev: Whether to include development artifacts.

    Yields:
        Path objects for the root-level items to include in the package.
    """
    matcher = IgnoreMatcher(project_root, include_dev=include_dev)

    # We copy everything except excluded items at the root level
    for item in project_root.iterdir():
        if item.is_symlink() or matcher.should_exclude(item):
            continue

        yield item
