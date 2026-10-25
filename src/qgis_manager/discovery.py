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

import logging
from collections.abc import Iterator
from pathlib import Path

from .ignore import IgnoreMatcher
from .metadata import (
    get_plugin_metadata,
    save_plugin_metadata,
    sync_metadata_version,
)
from .naming import slugify, validate_slug

logger = logging.getLogger(__name__)

__all__ = [
    "find_project_root",
    "get_plugin_metadata",
    "get_source_files",
    "save_plugin_metadata",
    "slugify",
    "sync_metadata_version",
    "validate_slug",
]


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
        has_metadata = (current / "metadata.txt").exists()
        has_pyproject = (current / "pyproject.toml").exists()
        if current == start_path.resolve():
            if has_metadata or has_pyproject:
                return current
        elif has_metadata:
            return current
        elif (current / ".git").exists():
            # Do not select a parent monorepo pyproject.toml above the repo.
            break
        elif has_pyproject:
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not find a project root (missing metadata.txt or pyproject.toml)."
    )


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
