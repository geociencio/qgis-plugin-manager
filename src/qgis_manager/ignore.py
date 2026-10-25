# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2026-02-18
#         copyright            : (C) 2026 by Juan M Bernales
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
Ignore pattern handling using standard library only.

Provides functionality to read ignore patterns from .gitignore and pyproject.toml
without requiring external dependencies like pathspec.
"""

import fnmatch
from collections.abc import Iterator
from pathlib import Path

from .constants import DEFAULT_EXCLUDE_PATTERNS
from .toml_utils import load_toml


def _load_ignore_file(project_root: Path) -> list[str]:
    """Load the first available ignore file (.qgisignore or .gitignore)."""
    for ignore_name in (".qgisignore", ".gitignore"):
        ignore_file = project_root / ignore_name
        if not ignore_file.exists():
            continue
        try:
            with open(ignore_file, encoding="utf-8") as handle:
                return [
                    line
                    for raw in handle
                    if (line := raw.strip()) and not line.startswith("#")
                ]
        except OSError:
            continue
    return []


def _load_pyproject_ignores(project_root: Path) -> list[str]:
    """Load ``[tool.qgis-manager].ignore`` from pyproject.toml."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return []
    data = load_toml(pyproject)
    tool_config = data.get("tool", {}).get("qgis-manager", {})
    custom_ignores = tool_config.get("ignore", [])
    if not isinstance(custom_ignores, list):
        return []
    return [str(item) for item in custom_ignores]


def load_ignore_patterns(project_root: Path, include_dev: bool = False) -> list[str]:
    """Load default, ignore-file and pyproject patterns.

    Args:
        project_root: The root directory of the project.
        include_dev: Whether to include development files (docs, tests, etc.).

    Returns:
        A list of patterns.
    """
    patterns = list(DEFAULT_EXCLUDE_PATTERNS)
    if not include_dev:
        from .constants import DEV_DIRECTORIES

        for directory in DEV_DIRECTORIES:
            patterns.append(f"/{directory}")
            patterns.append(f"/{directory}/**/*")
    patterns.extend(_load_ignore_file(project_root))
    patterns.extend(_load_pyproject_ignores(project_root))
    return patterns


class IgnoreMatcher:
    """Helper class to filter paths against ignore patterns using standard fnmatch.

    Root patterns are evaluated first, then ignore files found in ancestor
    directories between the project root and the path. Deeper rules win, and
    negation is applied in order.
    """

    def __init__(self, project_root: Path, include_dev: bool = False):
        self.project_root = project_root
        self.patterns = load_ignore_patterns(project_root, include_dev)
        self._nested_cache: dict[Path, list[str]] = {}

    def should_exclude(self, path: Path) -> bool:
        """Determine if a path is excluded, honoring ordered ``!`` negations."""
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            return False
        excluded = False
        path_str = str(rel_path).replace("\\", "/")
        for pattern in self.patterns:
            excluded = self._apply(pattern, path_str, rel_path.parts, excluded)
        for base_dir, pattern in self._nested_rules(path):
            try:
                nested_rel = path.relative_to(base_dir)
            except ValueError:
                continue
            nested_str = str(nested_rel).replace("\\", "/")
            excluded = self._apply(pattern, nested_str, nested_rel.parts, excluded)
        return excluded

    def _apply(
        self, pattern: str, path_str: str, parts: tuple[str, ...], excluded: bool
    ) -> bool:
        negated = pattern.startswith("!")
        candidate = pattern[1:] if negated else pattern
        if candidate and self._matches(path_str, parts, candidate):
            return not negated
        return excluded

    def _nested_rules(self, path: Path) -> Iterator[tuple[Path, str]]:
        try:
            relative_parent = path.parent.relative_to(self.project_root)
        except ValueError:
            return
        current = self.project_root
        for part in relative_parent.parts:
            current = current / part
            for pattern in self._patterns_for_dir(current):
                yield current, pattern

    def _patterns_for_dir(self, directory: Path) -> list[str]:
        if directory in self._nested_cache:
            return self._nested_cache[directory]
        patterns = _load_ignore_file(directory)
        self._nested_cache[directory] = patterns
        return patterns

    @staticmethod
    def _matches(path_str: str, parts: tuple[str, ...], pattern: str) -> bool:
        """Return True when one ignore pattern matches the relative path."""
        p = pattern.rstrip("/")
        is_root_relative = p.startswith("/")
        if is_root_relative:
            p = p[1:]
        if is_root_relative:
            return fnmatch.fnmatch(path_str, p) or path_str.startswith(p + "/")
        if any(fnmatch.fnmatch(part, p) for part in parts):
            return True
        if fnmatch.fnmatch(path_str, p) or fnmatch.fnmatch(path_str, f"*/{p}"):
            return True
        return path_str.startswith(f"{p}/") or f"/{p}/" in path_str
