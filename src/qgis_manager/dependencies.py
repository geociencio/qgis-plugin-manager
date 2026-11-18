import logging
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .toml_utils import load_toml

logger = logging.getLogger(__name__)

_NAME = r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?"
_REQUIREMENT_RE = re.compile(
    rf"^{_NAME}(?:\[[A-Za-z0-9._,-]+\])?"
    r"(?:\s*(?:===|==|!=|~=|>=|<=|>|<)\s*[A-Za-z0-9.*+!_-]+"
    r"(?:\s*,\s*(?:===|==|!=|~=|>=|<=|>|<)\s*[A-Za-z0-9.*+!_-]+)*)?"
    r"(?:\s*;\s*[^;]+)?$"
)


def is_valid_requirement(requirement: str) -> bool:
    """Return True for a conservative PEP 508 requirement."""
    if not requirement or requirement.startswith("-"):
        return False
    if any(character in requirement for character in "\r\n\x00"):
        return False
    if re.search(r"(?:^|\s)-", requirement):
        return False
    return bool(_REQUIREMENT_RE.match(requirement))


@dataclass(frozen=True)
class DependencyPolicy:
    """Bounded execution policy for dependency installation."""

    timeout: int = 300
    dry_run: bool = False


def get_dependencies(project_root: Path) -> list[str]:
    """Read dependencies from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        return []

    data = load_toml(pyproject_path)
    # We look for [tool.qgis-manager.dependencies]
    tool_config = data.get("tool", {}).get("qgis-manager", {})
    deps = tool_config.get("dependencies", [])
    return [str(d) for d in deps] if isinstance(deps, list) else []


def install_external_libs(
    project_root: Path,
    target_dir: str = "libs",
    policy: DependencyPolicy | None = None,
) -> bool:
    """Install external libraries to a target directory using pip/uv."""
    policy = policy or DependencyPolicy()
    dependencies = get_dependencies(project_root)
    if not dependencies:
        logger.debug("No dependencies found in pyproject.toml")
        return True

    invalid = [dep for dep in dependencies if not is_valid_requirement(dep)]
    if invalid:
        logger.error("❌ Refusing unsafe dependency requirements: %s", invalid)
        return False

    target = Path(target_dir)
    if target.is_absolute() or ".." in target.parts:
        logger.error("❌ Dependency target must stay inside the project: %s", target)
        return False
    project = project_root.resolve()
    dest_path = (project / target).resolve()
    if not dest_path.is_relative_to(project):
        logger.error("❌ Dependency target escapes the project: %s", dest_path)
        return False

    logger.info(f"📦 Installing {len(dependencies)} dependencies to {target_dir}/...")

    # We prefer 'uv pip install' if available for speed and consistency
    cmd_base = ["uv", "pip", "install"]
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            check=True,
            timeout=policy.timeout,
        )
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        cmd_base = [sys.executable, "-m", "pip", "install"]

    cmd = cmd_base + ["--target", str(dest_path), "--", *dependencies]
    if policy.dry_run:
        logger.info("Dry run: %s", subprocess.list2cmdline(cmd))
        return True
    dest_path.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=policy.timeout,
        )
        if result.returncode != 0:
            logger.error(f"❌ Failed to install dependencies:\n{result.stderr}")
            return False

        logger.info(f"✅ Dependencies installed successfully in {target_dir}/")

        # Recommendation: user needs to add this folder to sys.path in __init__.py
        # We could automate this, but for now just log it.
        return True
    except (OSError, subprocess.SubprocessError) as e:
        logger.error(f"❌ Unexpected error installing dependencies: {e}")
        return False
