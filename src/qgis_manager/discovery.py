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


def slugify(text: str) -> str:
    """Convert text to a valid directory name slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text).strip("_")
    return text


def find_project_root(start_path: Path) -> Path:
    """Find the project root by looking for metadata.txt."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / "metadata.txt").exists():
            return current
        current = current.parent
    raise FileNotFoundError(
        "Could not find a QGIS plugin project root (missing metadata.txt)."
    )


def get_plugin_metadata(project_root: Path) -> dict:
    """Read metadata.txt and return as a dict."""
    config = configparser.ConfigParser()
    # Handle UTF-8 and other encodings if necessary
    try:
        config.read(project_root / "metadata.txt", encoding="utf-8")
    except UnicodeDecodeError:
        config.read(project_root / "metadata.txt", encoding="latin-1")

    if "general" not in config:
        raise ValueError("Invalid metadata.txt: missing [general] section.")

    metadata = dict(config["general"])
    if "name" not in metadata:
        raise ValueError("Invalid metadata.txt: missing 'name' field.")

    metadata["slug"] = slugify(metadata["name"])
    return metadata


def get_source_files(project_root: Path):
    """Dynamically discover source files and directories to copy."""
    # Common exclusions
    exclude_patterns = {
        "__pycache__",
        ".git",
        ".venv",
        ".agent",
        ".ai-context",
        "venv",
        "env",
        "tests",
        ".pytest_cache",
        ".ruff_cache",
        "*.pyc",
        "*.bak*",
        "build",
        "dist",
        "*.egg-info",
        "scripts",
        "tools",
        "research",
    }

    # We copy everything except excluded items
    for item in project_root.iterdir():
        if item.name in exclude_patterns:
            continue

        # Check simple pattern matches (for files like *.pyc)
        if any(item.match(p) for p in exclude_patterns if "*" in p):
            continue

        yield item
