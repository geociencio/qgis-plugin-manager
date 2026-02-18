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
import sys
from pathlib import Path

# tomllib is 3.11+, fallback to a simple parser for 3.10
if sys.version_info >= (3, 11):
    pass
else:
    # Minimal TOML parser for the specific 'ignore' list in pyproject.toml
    # This avoids adding 'tomli' as a dependency.
    class TomlLoaderShim:
        @staticmethod
        def load(f):
            content = f.read().decode("utf-8")
            import re

            # Very basic extraction of tool.qgis-manager.ignore list
            match = re.search(
                r"\[tool\.qgis-manager\]\s*ignore\s*=\s*\[(.*?)\]",
                content,
                re.DOTALL,
            )
            if match:
                items_raw = match.group(1)
                items = re.findall(r'"(.*?)"', items_raw)
                return {"tool": {"qgis-manager": {"ignore": items}}}
            return {}


from .constants import DEFAULT_EXCLUDE_PATTERNS


def load_ignore_patterns(project_root: Path, include_dev: bool = False):
    """
    Load ignore patterns from .gitignore and pyproject.toml.

    Args:
        project_root: The root directory of the project.
        include_dev: Whether to include development files (docs, tests, etc.).

    Returns:
        A list of patterns.
    """
    patterns = list(DEFAULT_EXCLUDE_PATTERNS)

    if not include_dev:
        from .constants import DEV_DIRECTORIES

        for d in DEV_DIRECTORIES:
            # Standard library fnmatch needs proper directory handling
            patterns.append(str(d))
            patterns.append(f"{d}/**/*")

    # 1. Try to load from .gitignore
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        try:
            with open(gitignore, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception:
            pass

    # 2. Try to load from pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            with open(pyproject, "rb") as f:
                data = TomlLoaderShim.load(f)
                custom_ignores = (
                    data.get("tool", {}).get("qgis-manager", {}).get("ignore", [])
                )
                if isinstance(custom_ignores, list):
                    patterns.extend(custom_ignores)
        except Exception:
            pass

    return patterns


class PathFilter:
    """Helper class to filter paths against ignore patterns using standard fnmatch."""

    def __init__(self, project_root: Path, patterns: list[str]):
        self.project_root = project_root
        self.patterns = patterns

    def should_exclude(self, path: Path) -> bool:
        """Determines if a path should be excluded using fnmatch."""
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            return False

        path_str = str(rel_path)
        parts = rel_path.parts

        for pattern in self.patterns:
            # Normalize pattern for matching
            p = pattern.rstrip("/")
            # is_dir_pattern = pattern.endswith("/")
            is_root_relative = pattern.startswith("/")

            if is_root_relative:
                p = p[1:]

            # 1. Exact match or prefix match for directories
            if is_root_relative:
                # Must match from the root
                if (
                    fnmatch.fnmatch(path_str, p)
                    or fnmatch.fnmatch(path_str, f"{p}/*")
                    or path_str.startswith(f"{p}/")
                ):
                    return True
            else:
                # Match anywhere
                if (
                    fnmatch.fnmatch(path_str, f"*{p}")
                    or fnmatch.fnmatch(path_str, f"*{p}/*")
                    or any(fnmatch.fnmatch(part, p) for part in parts)
                ):
                    return True

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
