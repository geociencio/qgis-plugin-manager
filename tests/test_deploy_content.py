"""Regression tests for deploy content comparison."""

from __future__ import annotations

import os
from pathlib import Path

from qgis_manager.core.deploy import _needs_copy


def test_needs_copy_detects_same_size_same_mtime_change(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    destination = tmp_path / "destination.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    destination.write_text("VALUE = 2\n", encoding="utf-8")
    stat = source.stat()
    os.utime(destination, (stat.st_atime, stat.st_mtime))

    assert source.stat().st_size == destination.stat().st_size
    assert source.stat().st_mtime == destination.stat().st_mtime
    assert _needs_copy(source, destination) is True


def test_needs_copy_accepts_identical_content(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    destination = tmp_path / "destination.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    destination.write_text("VALUE = 1\n", encoding="utf-8")

    assert _needs_copy(source, destination) is False
