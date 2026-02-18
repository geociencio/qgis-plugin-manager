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

Functions:
    slugify: Convert plugin name to valid directory slug
    find_project_root: Locate project root by searching for metadata.txt
    get_plugin_metadata: Parse metadata.txt and extract plugin information
    get_source_files: Discover source files to include in deployment
"""

import configparser
import re
from pathlib import Path

from .ignore import IgnoreMatcher, load_ignore_patterns


def slugify(text: str) -> str:
    """Convert text to a valid directory name slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text).strip("_")
    return text


def find_project_root(start_path: Path) -> Path:
    """Find the project root by looking for metadata.txt or pyproject.toml."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / "metadata.txt").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not find a project root (missing metadata.txt or pyproject.toml)."
    )


def get_plugin_metadata(project_root: Path) -> dict:
    """Read metadata.txt and return as a dict. Fallback to basic info if missing."""
    metadata_path = project_root / "metadata.txt"
    if not metadata_path.exists():
        # Minimum metadata for tool-only projects
        return {
            "name": project_root.name,
            "slug": slugify(project_root.name),
            "version": "unknown",
        }

    config = configparser.ConfigParser()
    try:
        config.read(metadata_path, encoding="utf-8")
    except UnicodeDecodeError:
        config.read(metadata_path, encoding="latin-1")

    if "general" not in config:
        # Fallback if file exists but is empty/malformed
        return {"name": project_root.name, "slug": slugify(project_root.name)}

    metadata = dict(config["general"])
    if "name" not in metadata:
        metadata["name"] = project_root.name

    metadata["slug"] = slugify(metadata["name"])
    return metadata


def save_plugin_metadata(project_root: Path, metadata: dict) -> None:
    """Save metadata dictionary back to metadata.txt."""
    config = configparser.ConfigParser()
    # Ensure we only save relevant fields to [general]
    general_data = {k: v for k, v in metadata.items() if k != "slug"}
    config["general"] = general_data

    with open(project_root / "metadata.txt", "w", encoding="utf-8") as f:
        config.write(f, space_around_delimiters=False)


def get_source_files(project_root: Path, include_dev: bool = False):
    """Dynamically discover source files and directories to copy."""
    spec = load_ignore_patterns(project_root, include_dev=include_dev)
    matcher = IgnoreMatcher(project_root, spec)

    # We copy everything except excluded items at the root level
    for item in project_root.iterdir():
        if matcher.should_exclude(item):
            continue

        yield item
