"""Cross-platform detection of the local QGIS plugin directory."""

import os
import sys
from pathlib import Path


def get_qgis_plugin_dir(profile: str = "default", version: int = 3) -> Path:
    """Detect the QGIS plugin directory based on the OS and version."""
    if sys.platform == "linux":
        return (
            Path.home()
            / f".local/share/QGIS/QGIS{version}/profiles/{profile}/python/plugins"
        )
    elif sys.platform == "darwin":
        return (
            Path.home()
            / f"Library/Application Support/QGIS/QGIS{version}/profiles"
            / profile
            / "python/plugins"
        )
    elif sys.platform == "win32":
        return (
            Path(os.environ["APPDATA"])
            / f"QGIS/QGIS{version}/profiles/{profile}/python/plugins"
        )
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")
