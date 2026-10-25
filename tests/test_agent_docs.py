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


def test_no_project_turbo_runtime_hints() -> None:
    """`// turbo` is an opencode-only framework hint, not a project directive."""
    assert "// turbo" not in AGENTS.read_text(encoding="utf-8")
    overlay = ROOT / ".agent-state" / "workflows"
    if overlay.is_dir():
        for path in overlay.rglob("*.md"):
            assert "// turbo" not in path.read_text(encoding="utf-8"), path


def test_deprecated_qa_docker_alias_is_not_adopted() -> None:
    """The project uses testing-standards, not the deprecated framework alias."""
    assert not (ROOT / ".agent-state" / "skills" / "qa-docker").exists()
    for name in ("AGENTS.md", "forge.toml", "opencode.json"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "qa-docker" not in text, name


def test_agentic_architecture_plan_links_exist() -> None:
    """The Gen 7/8 annotation must link to the upstream plans."""
    index = ROOT / "docs" / "architecture" / "AGENTIC_SYSTEM_PLANS.md"
    text = index.read_text(encoding="utf-8")

    for link in (
        "../../.agent/architecture/IMPROVEMENT_PLAN_GEN7.md",
        "../../.agent/architecture/IMPROVEMENT_PLAN_GEN8.md",
        "../../.agent/architecture/IMPROVEMENT_PLAN.md",
    ):
        assert f"]({link})" in text
        assert (index.parent / link).resolve().is_file()
