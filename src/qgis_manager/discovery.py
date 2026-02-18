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
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .ignore import IgnoreMatcher, load_ignore_patterns

logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """Convert text to a valid directory name slug.

    Args:
        text: Input string to be converted into a slug.

    Returns:
        A clean, lowercase slug with underscores instead of spaces.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text).strip("_")
    return text


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
    """Save metadata dictionary back to metadata.txt.

    Args:
        project_root: Root directory of the QGIS plugin project.
        metadata: Dictionary with project metadata to persist.

    Raises:
        Exception: If saving the file fails.
    """
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str  # type: ignore[method-assign, assignment] # Preserve case
    # Ensure we only save relevant fields to [general]
    general_data = {k: v for k, v in metadata.items() if k != "slug"}
    config["general"] = general_data

    try:
        with open(project_root / "metadata.txt", "w", encoding="utf-8") as f:
            config.write(f, space_around_delimiters=False)
    except Exception as e:
        logger.error(f"Error saving metadata.txt: {e}")
        raise


def get_source_files(project_root: Path, include_dev: bool = False) -> Iterator[Path]:
    """Dynamically discover source files and directories to copy.

    Args:
        project_root: Root directory of the project.
        include_dev: Whether to include development artifacts.

    Yields:
        Path objects for the root-level items to include in the package.
    """
    spec = load_ignore_patterns(project_root, include_dev=include_dev)
    matcher = IgnoreMatcher(project_root, spec)

    # We copy everything except excluded items at the root level
    for item in project_root.iterdir():
        if matcher.should_exclude(item):
            continue

        yield item
