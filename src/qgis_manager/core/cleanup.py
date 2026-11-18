"""Removal of build artifacts, caches and compiled outputs."""

import logging
import shutil
import subprocess
from pathlib import Path

from ..paths import PathPolicy, ProjectWalker

logger = logging.getLogger(__name__)


def _walker(project_root: Path, *, include_cache_dirs: bool = False) -> ProjectWalker:
    return ProjectWalker(
        project_root,
        PathPolicy.for_purpose("clean"),
        include_cache_dirs=include_cache_dirs,
    )


def _remove_cache_dirs(project_root: Path, dry_run: bool, actions: list[str]) -> None:
    """Remove tool cache directories outside environments/dependencies."""
    for entry in _walker(project_root, include_cache_dirs=True).entries():
        for name in entry.cache_dirs:
            path = entry.root / name
            actions.append(f"remove {path.relative_to(project_root)}")
            if not dry_run:
                shutil.rmtree(path)
                logger.debug(f"  🗑️ {path.relative_to(project_root)}")


def _remove_cache_files(project_root: Path, dry_run: bool, actions: list[str]) -> None:
    """Remove compiled bytecode and QGIS sidecar files."""
    for path in _walker(project_root).files():
        if not path.name.endswith((".pyc", ".qpj", ".cpg")):
            continue
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
    for source in _walker(project_root).files():
        suffix = source.suffix.lower()
        if suffix not in {".ui", ".qrc"}:
            continue
        compiled = source.with_suffix(".py")
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
