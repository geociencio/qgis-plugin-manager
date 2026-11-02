"""Removal of build artifacts, caches and compiled outputs."""

import logging
import os
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path

logger = logging.getLogger(__name__)

_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "libs",
    "node_modules",
    "venv",
}
_CACHE_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache"}


def _walk_project(
    project_root: Path, include_cache_dirs: bool = False
) -> Iterator[tuple[Path, list[str], list[str]]]:
    """Yield (root, cache_dirs, filenames) without entering excluded dirs."""
    for current, dirnames, filenames in os.walk(project_root, topdown=True):
        root = Path(current)
        cache_dirs = (
            [name for name in dirnames if name in _CACHE_DIRS]
            if include_cache_dirs
            else []
        )
        dirnames[:] = sorted(
            name
            for name in dirnames
            if (include_cache_dirs and name in _CACHE_DIRS)
            or (name not in _EXCLUDED_DIRS and not (root / name).is_symlink())
        )
        yield root, cache_dirs, filenames


def _remove_cache_dirs(project_root: Path, dry_run: bool, actions: list[str]) -> None:
    """Remove tool cache directories outside environments/dependencies."""
    for root, cache_dirs, _filenames in _walk_project(
        project_root, include_cache_dirs=True
    ):
        for name in cache_dirs:
            path = root / name
            actions.append(f"remove {path.relative_to(project_root)}")
            if not dry_run:
                shutil.rmtree(path)
                logger.debug(f"  🗑️ {path.relative_to(project_root)}")


def _remove_cache_files(project_root: Path, dry_run: bool, actions: list[str]) -> None:
    """Remove compiled bytecode and QGIS sidecar files."""
    for root, _cache_dirs, filenames in _walk_project(project_root):
        for name in filenames:
            if not name.endswith((".pyc", ".qpj", ".cpg")):
                continue
            path = root / name
            actions.append(f"remove {path.relative_to(project_root)}")
            if not dry_run:
                path.unlink()
                logger.debug(f"  🗑️ {path.relative_to(project_root)}")


def _is_tracked(project_root: Path, path: Path) -> bool:
    """Return True when Git tracks ``path``; False if Git is unavailable."""
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(project_root),
                "ls-files",
                "--error-unmatch",
                str(path.relative_to(project_root)),
            ],
            capture_output=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def _remove_compiled_outputs(
    project_root: Path,
    dry_run: bool,
    keep_generated: bool,
    actions: list[str],
) -> None:
    """Remove Python modules generated from ``.ui``/``.qrc`` sources."""
    for root, _cache_dirs, filenames in _walk_project(project_root):
        for name in filenames:
            suffix = Path(name).suffix.lower()
            if suffix not in {".ui", ".qrc"}:
                continue
            compiled = root / f"{Path(name).stem}.py"
            if not compiled.is_file():
                continue
            if keep_generated:
                actions.append(f"keep {compiled.relative_to(project_root)}")
                continue
            if _is_tracked(project_root, compiled):
                actions.append(
                    f"warning: {compiled.relative_to(project_root)} is tracked by Git; "
                    "use --keep-generated to preserve it"
                )
            actions.append(f"remove {compiled.relative_to(project_root)}")
            if not dry_run:
                compiled.unlink()
                logger.debug(f"  🗑️ {compiled.relative_to(project_root)}")


def _remove_docs_output(project_root: Path, dry_run: bool, actions: list[str]) -> None:
    """Remove compiled Sphinx documentation output."""
    for docs_dir in ("help/html", "help/build"):
        target = project_root / docs_dir
        if target.is_dir():
            actions.append(f"remove {docs_dir}")
            if not dry_run:
                shutil.rmtree(target)
                logger.debug(f"  🗑️ {docs_dir}")


def clean_artifacts(
    project_root: Path,
    dry_run: bool = False,
    keep_generated: bool = False,
) -> list[str]:
    """Clean build artifacts: caches, compiled UI/resources and docs output.

    Args:
        project_root: Project root to clean.
        dry_run: Report actions without deleting anything.
        keep_generated: Preserve ``.py`` files generated from ``.ui``/``.qrc``.

    Returns:
        Human-readable actions that were applied or would be applied.
    """
    logger.info("Cleaning artifacts...")
    actions: list[str] = []
    _remove_cache_dirs(project_root, dry_run, actions)
    _remove_cache_files(project_root, dry_run, actions)
    _remove_compiled_outputs(project_root, dry_run, keep_generated, actions)
    _remove_docs_output(project_root, dry_run, actions)
    logger.info("✨ Clean complete.")
    return actions
