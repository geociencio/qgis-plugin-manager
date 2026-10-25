"""Plugin deployment, backup rotation and smart directory synchronization."""

import logging
import shutil
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from ..ignore import IgnoreMatcher
from ..metadata import get_plugin_metadata
from ..naming import validate_slug
from .platform import get_qgis_plugin_dir

logger = logging.getLogger(__name__)


def uninstall_plugin(
    project_root: Path,
    profile: str = "default",
    qgis_version: int = 3,
) -> Path | None:
    """Remove the deployed plugin from the QGIS plugins directory.

    Args:
        project_root: Root directory of the plugin project.
        profile: QGIS profile name.
        qgis_version: Major QGIS version (3 or 4).

    Returns:
        The removed directory, or None if the plugin was not deployed.

    Raises:
        ValueError: If the plugin metadata produces an unsafe/empty slug.
    """
    metadata = get_plugin_metadata(project_root)
    slug = validate_slug(str(metadata["slug"]), source="plugin metadata")
    plugins_dir = get_qgis_plugin_dir(profile, version=qgis_version)
    plugin_dir = plugins_dir / slug
    if plugin_dir.parent != plugins_dir:
        raise ValueError(f"Refusing to remove unsafe path: {plugin_dir}")
    if plugin_dir.is_symlink():
        plugin_dir.unlink()
        return plugin_dir
    if plugin_dir.exists():
        shutil.rmtree(plugin_dir)
        return plugin_dir
    return None


def rotate_backups(parent_dir: Path, slug: str, limit: int) -> None:
    """Keep only the N most recent backups for a plugin."""
    if limit <= 0:
        return

    # Find all backup directories for this slug
    backups = []
    for item in parent_dir.iterdir():
        if (
            item.is_dir()
            and not item.is_symlink()
            and item.name.startswith(f"{slug}.bak.")
        ):
            backups.append(item)

    # Sort by name (which contains timestamp) descending
    backups.sort(key=lambda x: x.name, reverse=True)

    # Remove those exceeding the limit
    if len(backups) > limit:
        cols = backups[limit:]
        for old_bak in cols:
            logger.debug(f"🧹 Removing old backup: {old_bak.name}")
            shutil.rmtree(old_bak)


def purge_backups(parent_dir: Path, slug: str) -> int:
    """Remove every backup directory for ``slug``.

    Args:
        parent_dir: Directory containing the plugin and its backups.
        slug: Plugin slug whose backups should be removed.

    Returns:
        Number of backup directories removed.
    """
    validate_slug(slug, source="backup")
    if not parent_dir.exists():
        return 0

    removed = 0
    for item in parent_dir.iterdir():
        if (
            item.is_dir()
            and not item.is_symlink()
            and item.name.startswith(f"{slug}.bak.")
        ):
            logger.debug(f"🧹 Purging backup: {item.name}")
            shutil.rmtree(item)
            removed += 1
    return removed


def _is_same_or_nested(item: Path, dst: Path) -> bool:
    """Return True if ``item`` is the destination or contains it.

    Prevents infinite recursion when deploying into a subfolder of the project.
    """
    try:
        resolved = item.resolve()
        dst_resolved = dst.resolve()
        return resolved == dst_resolved or dst_resolved.is_relative_to(resolved)
    except Exception:
        return False


def _needs_copy(src: Path, dst: Path) -> bool:
    """Return True if ``src`` differs from ``dst`` (size or mtime)."""
    if not dst.exists():
        return True
    src_stat = src.stat()
    dst_stat = dst.stat()
    return not (
        src_stat.st_size == dst_stat.st_size and src_stat.st_mtime == dst_stat.st_mtime
    )


def _cleanup_destination(src: Path, dst: Path, matcher: IgnoreMatcher) -> None:
    """Remove destination entries that no longer exist in the source.

    Only non-ignored entries are removed, so development files such as ``.git``
    are preserved.
    """
    for item in dst.iterdir():
        if item.is_symlink():
            item.unlink()
            logger.debug(f"  🗑️ {item.name} (destination symlink)")
            continue
        source_item = src / item.name
        if source_item.exists() or matcher.should_exclude(source_item):
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
        logger.debug(f"  🗑️ {item.name} (removed from target)")


def sync_directory(src: Path, dst: Path, matcher: IgnoreMatcher) -> None:
    """Sync source to destination only copying changed files (rsync-like)."""
    if not dst.exists():
        dst.mkdir(parents=True)

    # 1. Copy/update files from source. Never follow symlinks: a plugin
    #    must not be able to read or copy files outside its project root.
    for item in src.iterdir():
        if item.is_symlink():
            logger.warning(f"Skipping symlink in source: {item}")
            continue
        if matcher.should_exclude(item):
            continue
        if _is_same_or_nested(item, dst):
            continue

        dest_item = dst / item.name
        if dest_item.is_symlink():
            dest_item.unlink()
            logger.warning(f"Removing destination symlink: {dest_item}")
        if item.is_dir():
            sync_directory(item, dest_item, matcher)
        elif _needs_copy(item, dest_item):
            shutil.copy2(item, dest_item)
            logger.debug(f"  ✅ {item.name} (updated)")

    # 2. Cleanup entries in destination that no longer exist in source
    _cleanup_destination(src, dst, matcher)


def deploy_plugin(
    project_root: Path,
    dest_dir: Path | None = None,
    no_backup: bool = False,
    profile: str = "default",
    qgis_version: int = 3,
    callback: Callable[[int], Any] | None = None,
    max_backups: int = 3,
) -> None:
    """Deploy the plugin to the QGIS directory.

    Raises:
        ValueError: If the plugin metadata produces an unsafe/empty slug or the
            resolved target is not a direct child of ``dest_dir``.
    """
    metadata = get_plugin_metadata(project_root)
    slug = validate_slug(str(metadata["slug"]), source="plugin metadata")

    if dest_dir is None:
        dest_dir = get_qgis_plugin_dir(profile, version=qgis_version)

    target_path = dest_dir / slug
    if target_path.is_symlink():
        raise ValueError(f"Refusing to deploy to symlink target: {target_path}")
    if target_path == dest_dir or target_path.parent != dest_dir:
        raise ValueError(
            f"Refusing to deploy outside the plugin directory: {target_path}"
        )

    # Pre-deployment backup
    if target_path.exists() and not no_backup:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = target_path.parent / f"{slug}.bak.{timestamp}"
        logger.info(f"📦 Creating backup at: {backup_path.name}")
        shutil.copytree(target_path, backup_path, symlinks=True)

        # Rotate backups
        rotate_backups(target_path.parent, slug, max_backups)

    # Deployment using smart sync
    target_path.mkdir(parents=True, exist_ok=True)

    # Load ignore patterns
    matcher = IgnoreMatcher(project_root, include_dev=False)

    # Automatically ignore the target_path if it's inside project_root
    # to avoid infinite recursion
    try:
        if target_path.resolve().is_relative_to(project_root.resolve()):
            rel_target = target_path.resolve().relative_to(project_root.resolve())
            matcher.patterns.append(str(rel_target))
            matcher.patterns.append(f"/{rel_target}")
    except Exception:
        pass

    logger.info(f"🚀 Syncing files to {target_path}")
    sync_directory(project_root, target_path, matcher)

    if callback:
        callback(100)  # Simple completion signal

    logger.info("✨ Deployment complete.")
