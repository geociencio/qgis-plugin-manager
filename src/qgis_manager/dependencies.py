import logging
import subprocess
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

logger = logging.getLogger(__name__)


def get_dependencies(project_root: Path) -> list[str]:
    """Read dependencies from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
            # We look for [tool.qgis-manager.dependencies]
            tool_config = data.get("tool", {}).get("qgis-manager", {})
            deps = tool_config.get("dependencies", [])
            return [str(d) for d in deps] if isinstance(deps, list) else []
    except Exception as e:
        logger.error(f"Error reading dependencies from pyproject.toml: {e}")
        return []


def install_external_libs(project_root: Path, target_dir: str = "libs") -> bool:
    """Install external libraries to a target directory using pip/uv."""
    dependencies = get_dependencies(project_root)
    if not dependencies:
        logger.debug("No dependencies found in pyproject.toml")
        return True

    dest_path = project_root / target_dir
    dest_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"📦 Installing {len(dependencies)} dependencies to {target_dir}/...")

    # We prefer 'uv pip install' if available for speed and consistency
    cmd_base = ["uv", "pip", "install"]
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        cmd_base = [sys.executable, "-m", "pip", "install"]

    cmd = cmd_base + ["--target", str(dest_path)] + dependencies

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"❌ Failed to install dependencies:\n{result.stderr}")
            return False

        logger.info(f"✅ Dependencies installed successfully in {target_dir}/")

        # Recommendation: user needs to add this folder to sys.path in __init__.py
        # We could automate this, but for now just log it.
        return True
    except Exception as e:
        logger.error(f"❌ Unexpected error installing dependencies: {e}")
        return False
