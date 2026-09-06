"""Helpers to invoke the external qgis-plugin-analyzer tool."""

import subprocess
from pathlib import Path


def run_qgis_analyzer(root: Path, subcommand: str, *args: str) -> int:
    """Run ``qgis-analyzer``, falling back to ``uv run`` when not installed.

    Args:
        root: Project root directory.
        subcommand: qgis-analyzer subcommand (e.g. ``analyze``, ``security``).
        *args: Additional arguments passed before the project path.

    Returns:
        The qgis-analyzer exit code.
    """
    try:
        subprocess.run(
            ["qgis-analyzer", "--version"], capture_output=True, check=True
        )
        cmd = ["qgis-analyzer", subcommand, *args, str(root)]
    except (subprocess.CalledProcessError, FileNotFoundError):
        cmd = ["uv", "run", "qgis-analyzer", subcommand, *args, str(root)]

    return subprocess.run(cmd, check=False).returncode
