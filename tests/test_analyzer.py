"""Tests for analyzer process control."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.cli.analyzer import run_qgis_analyzer


@patch("qgis_manager.cli.analyzer.subprocess.run")
def test_analyzer_timeout_returns_124(mock_run: Mock) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired("qgis-analyzer", 1)
    assert run_qgis_analyzer(Path("."), "analyze", timeout=1) == 124


@patch("qgis_manager.cli.analyzer.subprocess.run")
def test_analyzer_availability_is_cached(mock_run: Mock) -> None:
    mock_run.return_value.returncode = 0
    assert run_qgis_analyzer(Path("."), "analyze") == 0
    assert run_qgis_analyzer(Path("."), "analyze") == 0
    # probe + two analyzer calls, not two probes.
    assert mock_run.call_count == 3
