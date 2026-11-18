"""Shared pytest fixtures."""

import pytest

from qgis_manager.cli import analyzer


@pytest.fixture(autouse=True)
def _reset_analyzer_cache():
    analyzer.reset_analyzer_cache()
    yield
