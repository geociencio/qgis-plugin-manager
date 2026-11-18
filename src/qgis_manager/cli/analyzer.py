"""Helpers to invoke the external qgis-plugin-analyzer tool."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_ANALYZER_TIMEOUT_SECONDS = 300
_ANALYZER_AVAILABLE: bool | None = None


def reset_analyzer_cache() -> None:
    """Reset the cached analyzer availability probe."""
    global _ANALYZER_AVAILABLE
    _ANALYZER_AVAILABLE = None


def _analyzer_available() -> bool:
    global _ANALYZER_AVAILABLE
    if _ANALYZER_AVAILABLE is None:
        try:
            subprocess.run(
                ["qgis-analyzer", "--version"],
                capture_output=True,
                check=True,
                timeout=10,
            )
        except (
            FileNotFoundError,
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            OSError,
        ):
            _ANALYZER_AVAILABLE = False
        else:
            _ANALYZER_AVAILABLE = True
    return _ANALYZER_AVAILABLE


def _build_command(root: Path, subcommand: str, args: tuple[str, ...]) -> list[str]:
    prefix = (
        ["qgis-analyzer"]
        if _analyzer_available()
        else [
            "uv",
            "run",
            "qgis-analyzer",
        ]
    )
    return [*prefix, subcommand, *args, str(root)]


def _run(
    command: list[str],
    *,
    capture: bool,
    timeout: int,
) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=capture,
            text=capture,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.error("Analyzer timed out after %s seconds.", timeout)
    except (FileNotFoundError, OSError) as exc:
        logger.error("Could not start analyzer: %s", exc)
    return None


def run_qgis_analyzer(
    root: Path,
    subcommand: str,
    *args: str,
    capture: bool = False,
    timeout: int = _ANALYZER_TIMEOUT_SECONDS,
) -> int:
    """Run ``qgis-analyzer``, falling back to ``uv run`` when not installed."""
    result = _run(
        _build_command(root, subcommand, args),
        capture=capture,
        timeout=timeout,
    )
    return result.returncode if result is not None else 124


def run_qgis_analyzer_output(
    root: Path,
    subcommand: str,
    *args: str,
    timeout: int = _ANALYZER_TIMEOUT_SECONDS,
) -> tuple[int, str]:
    """Run the analyzer and return ``(exit_code, stdout)``."""
    result = _run(
        _build_command(root, subcommand, args),
        capture=True,
        timeout=timeout,
    )
    if result is None:
        return 124, ""
    return result.returncode, result.stdout
