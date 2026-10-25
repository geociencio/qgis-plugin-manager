"""Tests for compile source scanning and bounded external tools."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from qgis_manager.core.compile import _iter_compile_sources, compile_ui_files


def test_compile_scan_skips_vendor_and_build_dirs(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "real.ui").write_text("", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "real.qrc").write_text("", encoding="utf-8")
    for directory in (".venv", "libs", "dist", "build"):
        (tmp_path / directory).mkdir()
        (tmp_path / directory / "vendor.ui").write_text("", encoding="utf-8")

    ui_names = {path.name for path in _iter_compile_sources(tmp_path, "*.ui")}
    qrc_names = {path.name for path in _iter_compile_sources(tmp_path, "*.qrc")}

    assert ui_names == {"real.ui"}
    assert qrc_names == {"real.qrc"}


def test_compile_ui_timeout_is_reported(tmp_path: Path) -> None:
    (tmp_path / "form.ui").write_text("", encoding="utf-8")
    timeout = subprocess.TimeoutExpired("pyuic6", 300)
    with (
        patch("qgis_manager.core.compile.get_uic_tool", return_value="pyuic6"),
        patch("qgis_manager.core.compile.subprocess.run", side_effect=timeout),
    ):
        assert compile_ui_files(tmp_path) is False
