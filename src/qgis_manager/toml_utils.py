"""Shared TOML helpers for reading and updating project configuration."""

import re
import tomllib
from pathlib import Path
from typing import Any


def load_toml(path: Path) -> dict[str, Any]:
    """Load a TOML file into a dictionary.

    Args:
        path: Path to the TOML file.

    Returns:
        Parsed dictionary, or an empty dict if the file is missing or malformed.
    """
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def get_project_version(pyproject: Path) -> str | None:
    """Read the version from the [project] section of a pyproject.toml.

    Args:
        pyproject: Path to the pyproject.toml file.

    Returns:
        Version string or None if not present.
    """
    data = load_toml(pyproject)
    version = data.get("project", {}).get("version")
    return str(version) if version else None


def set_project_version(pyproject: Path, version: str) -> bool:
    """Set the version in the [project] section, preserving the rest of the file.

    Uses a line-anchored edit so comments and unrelated content are preserved.
    Unlike a full TOML round-trip, this keeps existing formatting intact.

    Args:
        pyproject: Path to the pyproject.toml file.
        version: New version string.

    Returns:
        True if the version was updated, False otherwise.
    """
    if not pyproject.exists():
        return False

    content = pyproject.read_text(encoding="utf-8")
    updated, changed = _replace_project_version(content, version)
    if changed:
        pyproject.write_text(updated, encoding="utf-8")
    return changed


def _replace_project_version(content: str, version: str) -> tuple[str, bool]:
    """Replace the version value inside the [project] table.

    Stops scanning once a new top-level table is reached, and only edits the
    first `version = "..."` line found within [project].
    """
    lines = content.split("\n")
    in_project = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            in_project = stripped == "[project]"
            continue
        if in_project:
            match = re.match(r'^(\s*version\s*=\s*)"[^"]*"(.*)$', line)
            if match:
                lines[i] = f'{match.group(1)}"{version}"{match.group(2)}'
                return "\n".join(lines), True
    return content, False
