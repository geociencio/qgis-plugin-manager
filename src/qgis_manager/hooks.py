import importlib.util
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def execute_python_hook(
    project_root: Path, hook_name: str, context: dict[str, Any]
) -> bool:
    """
    Execute a native Python hook from plugin_hooks.py if it exists.

    Args:
        project_root: Root directory of the plugin
        hook_name: Name of the hook (e.g., 'pre-deploy')
        context: Dictionary with project context

    Returns:
        True if the hook succeeded or didn't exist, False on failure.
    """
    hooks_file = project_root / "plugin_hooks.py"
    if not hooks_file.exists():
        return True

    # Normalize hook name: 'pre-deploy' -> 'pre_deploy'
    func_name = hook_name.replace("-", "_")

    try:
        # Dynamic import
        spec = importlib.util.spec_from_file_location("plugin_hooks", hooks_file)
        if spec is None or spec.loader is None:
            return True

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, func_name):
            func = getattr(module, func_name)
            logger.info(f"🪝 Executing native Python hook: {func_name}")

            # Execute function
            result = func(context)

            # If function returns explicitly False, the hook failed
            if result is False:
                logger.error(f"❌ Native hook '{func_name}' reported failure.")
                return False

            logger.debug(f"✅ Native hook '{func_name}' finished successfully.")
            return True

        return True  # Function not found is not an error, just skip
    except Exception as e:
        logger.error(f"❌ Error executing native hook '{func_name}': {e}")
        return False


def run_hook(
    name: str,
    command: str | None,
    project_root: Path,
    context: dict[str, Any] | None = None,
) -> bool:
    """
    Run a hook, prioritizing native Python hooks then falling back to command.
    """
    # 1. Try native Python hook first
    ctx = context or {"project_root": project_root}
    if not execute_python_hook(project_root, name, ctx):
        return False

    # 2. Run configured shell/script command if any
    if not command:
        return True

    logger.info(f"🪝 Running configured hook command: {name} ({command})")

    # Check if command is a python script (legacy script execution)
    is_python = command.strip().endswith(".py")
    env = os.environ.copy()
    env["QGIS_PROJECT_ROOT"] = str(project_root)

    full_cmd: str | list[str]
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
            env=env,
        )

        if result.returncode != 0:
            logger.error(
                f"❌ Hook command '{name}' failed " f"(exit code {result.returncode})"
            )
            if result.stdout:
                logger.error(f"STDOUT: {result.stdout}")
            if result.stderr:
                logger.error(f"STDERR: {result.stderr}")
            return False

        logger.debug(f"✅ Hook command '{name}' finished successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error running hook command '{name}': {e}")
        return False
