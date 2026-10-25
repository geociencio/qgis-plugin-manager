"""Release-note naming checks for the tag-driven release workflow."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs" / "releases" / "notes"
NORMALIZED = re.compile(r"v\d+\.\d+\.\d+\.md")


def test_active_release_notes_use_normalized_names() -> None:
    active = [
        path for path in NOTES.iterdir() if path.is_file() and path.suffix == ".md"
    ]
    assert active
    assert all(NORMALIZED.fullmatch(path.name) for path in active)


def test_legacy_duplicate_note_is_preserved_in_archive() -> None:
    archived = NOTES / "archive" / "RELEASE_NOTES_v0.6.2.md"
    assert archived.is_file()
    assert (NOTES / "v0.6.2.md").is_file()


def test_no_stale_legacy_note_links() -> None:
    for path in (ROOT / "docs" / "releases").rglob("*.md"):
        if "archive" in path.parts:
            continue
        assert "notes/RELEASE_NOTES_" not in path.read_text(encoding="utf-8"), path
