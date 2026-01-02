import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def run_hook(name: str, command: str, project_root: Path) -> bool:
    """Run a shell command as a hook."""
    if not command:
        return True

    logger.info(f"🪝 Running hook: {name} ({command})")
    logger.info(f"🪝 Running hook: {name} ({command})")

    # Check if command is a python script
    is_python = command.strip().endswith(".py")
    env = os.environ.copy()
    env["QGIS_PROJECT_ROOT"] = str(project_root)

    try:
        if is_python:
            # Run via current python interpreter
            full_cmd = [sys.executable, command]
            is_shell = False
        else:
            full_cmd = command
            is_shell = True

        result = subprocess.run(
            full_cmd,
            shell=is_shell,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            env=env
        )

        if result.returncode != 0:
            logger.error(f"❌ Hook '{name}' failed (exit code {result.returncode})")
            if result.stdout:
                logger.error(f"STDOUT: {result.stdout}")
            if result.stderr:
                logger.error(f"STDERR: {result.stderr}")
            return False

        logger.debug(f"✅ Hook '{name}' finished successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error running hook '{name}': {e}")
        return False
