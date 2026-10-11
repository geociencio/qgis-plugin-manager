"""Removal of build artifacts, caches and compiled outputs."""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


def _remove_cache_dirs(project_root: Path) -> None:
    """Remove tool cache directories (``__pycache__``, pytest, ruff)."""
    for dir_name in ("__pycache__", ".pytest_cache", ".ruff_cache"):
        for item in project_root.rglob(dir_name):
            if item.is_dir():
                shutil.rmtree(item)
                logger.debug(f"  🗑️ {item.relative_to(project_root)}")


def _remove_cache_files(project_root: Path) -> None:
    """Remove compiled bytecode and QGIS sidecar files."""
    for pattern in ("*.pyc", "*.qpj", "*.cpg"):
        for item in project_root.rglob(pattern):
            if item.is_file():
                item.unlink()
                logger.debug(f"  🗑️ {item.relative_to(project_root)}")


def _remove_compiled_outputs(project_root: Path) -> None:
    """Remove Python modules generated from ``.ui``/``.qrc`` sources."""
    for pattern in ("*.ui", "*.qrc"):
        for source in project_root.rglob(pattern):
            compiled = source.with_suffix(".py")
            if compiled.is_file():
                compiled.unlink()
                logger.debug(f"  🗑️ {compiled.relative_to(project_root)}")


def _remove_docs_output(project_root: Path) -> None:
    """Remove compiled Sphinx documentation output."""
    for docs_dir in ("help/html", "help/build"):
        target = project_root / docs_dir
        if target.is_dir():
            shutil.rmtree(target)
            logger.debug(f"  🗑️ {docs_dir}")


def clean_artifacts(project_root: Path):
    """Clean build artifacts: caches, compiled UI/resources and docs output."""
    logger.info("Cleaning artifacts...")
    _remove_cache_dirs(project_root)
    _remove_cache_files(project_root)
    _remove_compiled_outputs(project_root)
    _remove_docs_output(project_root)
    logger.info("✨ Clean complete.")
