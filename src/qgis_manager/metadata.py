"""Line-oriented helpers for reading and updating ``metadata.txt`` files.

The functions in this module deliberately avoid a full TOML/INI round-trip:
QGIS ``metadata.txt`` files may contain comments, blank lines, custom sections
and multi-line values, and rewriting them with ``configparser`` destroys that
content.  Updates are applied in place so untouched lines keep their original
formatting.
"""

from __future__ import annotations

import configparser
import logging
import os
import re
from pathlib import Path
from typing import Any

from .naming import slugify
from .toml_utils import get_project_version

logger = logging.getLogger(__name__)

#: ``key=value`` or ``key: value`` inside a section, keeping surrounding spaces.
_KEY_RE = re.compile(r"^(\s*)([A-Za-z][A-Za-z0-9_]*)(\s*[=:]\s*)(.*)$")


def _render_key_lines(match: re.Match[str], value: str) -> list[str]:
    """Render a key line (plus indented continuation lines) for ``value``."""
    parts = value.splitlines() or [""]
    rendered = [f"{match.group(1)}{match.group(2)}{match.group(3)}{parts[0]}"]
    rendered.extend(f"    {part}" for part in parts[1:])
    return rendered


def format_general_entries(updates: dict[str, str]) -> list[str]:
    """Render ``key=value`` entries, indenting multi-line values.

    Args:
        updates: Mapping of metadata key to value.

    Returns:
        One or more lines per entry, with continuation lines indented.
    """
    lines: list[str] = []
    for key, value in updates.items():
        parts = value.splitlines() or [""]
        lines.append(f"{key}={parts[0]}")
        lines.extend(f"    {part}" for part in parts[1:])
    return lines


def _insert_missing_keys(
    out: list[str], general_tail: int, updates: dict[str, str], applied: set[str]
) -> None:
    """Insert keys that were not found in ``[general]`` at the section end."""
    remaining = [key for key in updates if key not in applied]
    if not remaining:
        return

    if general_tail < 0:
        if out and out[-1].strip() != "":
            out.append("")
        out.append("[general]")
        general_tail = len(out)

    new_lines: list[str] = []
    for key in remaining:
        new_lines.extend(format_general_entries({key: updates[key]}))
    out[general_tail:general_tail] = new_lines


def update_general_keys(text: str, updates: dict[str, str]) -> str:
    """Update keys inside the ``[general]`` section of a metadata document.

    Existing keys are updated in place, preserving their indentation,
    delimiter and all surrounding lines (comments, blank lines, other
    sections).  Keys that are absent are appended at the end of ``[general]``;
    if the section does not exist it is created at the end of the document.

    Args:
        text: Full contents of a ``metadata.txt`` file.
        updates: Mapping of metadata key to its new value.

    Returns:
        The updated document.  When ``updates`` is empty the input is returned
        unchanged.
    """
    if not updates:
        return text

    out: list[str] = []
    in_general = False
    applied: set[str] = set()
    general_tail = -1  # index in ``out`` right after the last [general] entry

    lines = text.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            in_general = stripped == "[general]"
            out.append(line)
            index += 1
            continue

        match = _KEY_RE.match(line) if in_general else None
        if match is None:
            out.append(line)
            index += 1
            continue

        key = match.group(2)
        if key in updates:
            applied.add(key)
            out.extend(_render_key_lines(match, str(updates[key])))
            general_tail = len(out)
            index += 1
            # Drop the old continuation lines of the replaced key.
            while (
                index < len(lines)
                and lines[index][:1] in (" ", "\t")
                and lines[index].strip()
            ):
                index += 1
            continue

        out.append(line)
        general_tail = len(out)
        index += 1

    _insert_missing_keys(out, general_tail, updates, applied)
    return "\n".join(out)


def write_text_atomic(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically, preserving nothing but content.

    A temporary file is created next to the destination and moved over it with
    :func:`os.replace`, so a failure cannot leave a half-written file.

    Args:
        path: Destination file.
        text: Content to write as UTF-8.

    Raises:
        OSError: If the temporary file cannot be written or moved.
    """
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


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
