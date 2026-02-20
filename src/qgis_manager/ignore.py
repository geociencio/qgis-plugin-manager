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
    import tomllib
else:
    # Minimal TOML parser for the specific 'ignore' list in pyproject.toml
    # This avoids adding 'tomli' as a dependency.
    class TomlLoaderShim:
        @staticmethod
        def load(f):
            content = f.read().decode("utf-8")
            import re

            # Try [tool.qgis-manager.ignore] section first
            match = re.search(
                r"\[tool\.qgis-manager\.ignore\]\s*ignore\s*=\s*\[(.*?)\]",
                content,
                re.DOTALL,
            )
            if match:
                items_raw = match.group(1)
                items = re.findall(r'"(.*?)"', items_raw)
                return {"tool": {"qgis-manager": {"ignore": items}}}

            # Fallback to [tool.qgis-manager] ignore key
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
            # Root-level only dev dirs
            patterns.append(f"/{d}")
            patterns.append(f"/{d}/**/*")

    # 1. Try to load from .gitignore or .qgisignore
    ignore_loaded = False
    for ignore_name in [".qgisignore", ".gitignore"]:
        if ignore_loaded:
            break

        ignore_file = project_root / ignore_name
        if ignore_file.exists():
            try:
                with open(ignore_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            patterns.append(line)
                ignore_loaded = True
            except Exception:
                pass

    # 2. Try to load from pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        try:
            with open(pyproject, "rb") as f:
                if sys.version_info >= (3, 11):
                    data = tomllib.load(f)
                else:
                    data = TomlLoaderShim.load(f)

                tool_config = data.get("tool", {}).get("qgis-manager", {})
                custom_ignores = tool_config.get("ignore", [])
                if isinstance(custom_ignores, list):
                    patterns.extend(custom_ignores)
        except Exception:
            pass

    return patterns


class IgnoreMatcher:
    """Helper class to filter paths against ignore patterns using standard fnmatch."""

    def __init__(self, project_root: Path, include_dev: bool = False):
        self.project_root = project_root
        self.patterns = load_ignore_patterns(project_root, include_dev)

    def should_exclude(self, path: Path) -> bool:
        """Determine if a path should be excluded (fnmatch with Git-like semantics)."""
        try:
            rel_path = path.relative_to(self.project_root)
        except ValueError:
            return False

        path_str = str(rel_path).replace("\\", "/")
        parts = rel_path.parts

        for pattern in self.patterns:
            p = pattern.rstrip("/")
            is_root_relative = p.startswith("/")
            if is_root_relative:
                p = p[1:]

            if is_root_relative:
                if fnmatch.fnmatch(path_str, p) or path_str.startswith(p + "/"):
                    return True
            else:
                # Global matching (matches any part of the path or the whole path)
                if any(fnmatch.fnmatch(part, p) for part in parts):
                    return True

                # Match full path
                if fnmatch.fnmatch(path_str, p) or fnmatch.fnmatch(path_str, f"*/{p}"):
                    return True

                # Implicit recursion for directories
                if path_str.startswith(f"{p}/") or f"/{p}/" in path_str:
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
