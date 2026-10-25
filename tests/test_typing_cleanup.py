"""Tests for typing metadata, CLI package cleanup and include-dev discovery."""

from __future__ import annotations

from pathlib import Path

import qgis_manager.cli as cli_package
from qgis_manager.discovery import get_source_files

ROOT = Path(__file__).resolve().parents[1]


def test_py_typed_marker_exists() -> None:
    assert (ROOT / "src" / "qgis_manager" / "py.typed").is_file()


def test_cli_resolves_to_package_and_shadow_module_is_gone() -> None:
    assert Path(cli_package.__file__ or "").name == "__init__.py"
    assert not (ROOT / "src" / "qgis_manager" / "cli.py").exists()


def test_source_files_respect_include_dev(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_text("[general]\nname=Demo\n", encoding="utf-8")
    (tmp_path / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_demo.py").write_text("", encoding="utf-8")

    production = {path.name for path in get_source_files(tmp_path, include_dev=False)}
    development = {path.name for path in get_source_files(tmp_path, include_dev=True)}

    assert "tests" not in production
    assert "tests" in development
    assert "module.py" in production
