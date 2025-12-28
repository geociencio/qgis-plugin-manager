import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def run_hook(name: str, command: str, project_root: Path) -> bool:
    """Run a shell command as a hook."""
    if not command:
        return True

    logger.info(f"🪝 Running hook: {name} ({command})")
    try:
        # Run command in shell, with project root as cwd
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False
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
