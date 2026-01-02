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
import fnmatch
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


class IgnoreMatcher:
    """Matches files and directories against exclude patterns."""

    def __init__(self, project_root: Path, include_dev: bool = False):
        self.project_root = project_root
        self.include_dev = include_dev
        self.patterns: set[str] = set()
        self._load_defaults()
        self._load_qgisignore()

    def _load_defaults(self):
        """Load default exclude patterns from constants."""
        from .constants import DEFAULT_EXCLUDE_PATTERNS, DEV_DIRECTORIES

        self.patterns.update(DEFAULT_EXCLUDE_PATTERNS)
        if not self.include_dev:
            # Add with leading slash to force root-relative matching
            for d in DEV_DIRECTORIES:
                self.patterns.add(f"/{d}")

    def _load_qgisignore(self):
        """Load patterns from .qgisignore if it exists."""
        ignore_file = self.project_root / ".qgisignore"
        if ignore_file.exists():
            try:
                with open(ignore_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            self.patterns.add(line)
            except Exception as e:
                from .utils import setup_logger

                logger = setup_logger(__name__)
                logger.warning(f"Could not read .qgisignore: {e}")

    def should_exclude(self, path: Path) -> bool:
        """Determines if a path should be excluded based on current patterns."""
        # Clean relative path to project root
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            # Path not under project root
            return False

        parts = rel_path.parts
        name = path.name

        for pattern in self.patterns:
            # 1. Path-specific match (if pattern contains /)
            if "/" in pattern:
                clean_p = pattern.strip("/")
                p_path = Path(clean_p)
                if rel_path == p_path or p_path in rel_path.parents:
                    return True
                continue

            # 2. Recursive match for specific names or wildcards (WITHOUT /)
            # e.g. '__pycache__' or '*.pyc' matches anywhere
            if fnmatch.fnmatch(name, pattern):
                return True

            if any(fnmatch.fnmatch(p, pattern) for p in parts):
                return True

        return False

        return False

    def get_ignore_func(self):
        """Returns a function compatible with shutil.copytree's ignore argument."""

        def ignore_func(directory: str, contents: list[str]) -> list[str]:
            dir_path = Path(directory)
            ignored = []
            for name in contents:
                full_path = dir_path / name
                if self.should_exclude(full_path):
                    ignored.append(name)
            return ignored

        return ignore_func


def get_source_files(project_root: Path, include_dev: bool = False):
    """Dynamically discover source files and directories to copy."""
    matcher = IgnoreMatcher(project_root, include_dev=include_dev)

    # We copy everything except excluded items at the root level
    for item in project_root.iterdir():
        if matcher.should_exclude(item):
            continue

        yield item
