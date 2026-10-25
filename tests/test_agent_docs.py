"""Consistency tests for the root AGENTS.md and framework references."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"


def test_root_agents_delegates_framework_tables() -> None:
    """Root AGENTS must link to framework docs instead of duplicating their tables."""
    text = AGENTS.read_text(encoding="utf-8")

    assert "single source of truth for this project" in text
    for link in (
        ".agent/AGENTS.md",
        ".agent/QUICK_REFERENCE.md",
        ".agent/workflows/index.md",
    ):
        assert f"]({link})" in text

    assert "| `/start-session`" not in text
    assert "| [agentic-memory]" not in text


def test_overlay_skill_links_exist() -> None:
    """Every project overlay skill listed in AGENTS.md must exist."""
    text = AGENTS.read_text(encoding="utf-8")

    for skill in ("domain-logic", "project-context"):
        link = f".agent-state/skills/{skill}/SKILL.md"
        assert f"]({link})" in text
        assert (ROOT / link).is_file()


def test_framework_reference_files_exist() -> None:
    """The framework files linked from AGENTS.md must be present in the submodule."""
    for link in (
        ".agent/AGENTS.md",
        ".agent/QUICK_REFERENCE.md",
        ".agent/workflows/index.md",
    ):
        assert (ROOT / link).is_file()


def test_qgis_domain_pack_has_single_source() -> None:
    """The framework pack is canonical; no project duplicate should be tracked."""
    text = AGENTS.read_text(encoding="utf-8")

    assert (ROOT / ".agent/scaffold/qgis").is_dir()
    assert not (ROOT / "scaffold/qgis").exists()
    assert ".agent/scaffold/qgis" in text
