"""Tests for hook inspection without execution."""

from __future__ import annotations

from pathlib import Path

from qgis_manager.cli.commands.hooks import HooksCommand
from qgis_manager.hooks import discover_python_hooks


def test_discover_python_hooks_does_not_execute(tmp_path: Path) -> None:
    marker = tmp_path / "executed.marker"
    (tmp_path / "plugin_hooks.py").write_text(
        f"from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed')\n\n"
        "def pre_deploy(context):\n"
        "    return True\n\n"
        "async def post_deploy(context):\n"
        "    return True\n",
        encoding="utf-8",
    )

    assert discover_python_hooks(tmp_path) == ["pre_deploy", "post_deploy"]
    HooksCommand()._hooks_list(tmp_path)
    assert not marker.exists()


def test_discover_python_hooks_ignores_invalid_syntax(tmp_path: Path) -> None:
    (tmp_path / "plugin_hooks.py").write_text("def broken(:\n", encoding="utf-8")
    assert discover_python_hooks(tmp_path) == []
