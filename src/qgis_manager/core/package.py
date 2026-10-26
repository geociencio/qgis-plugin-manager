"""ZIP packaging, build-metadata stamping and git information helpers."""

import hashlib
import logging
import os
import re
import subprocess
import zipfile
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any

from ..discovery import get_source_files
from ..ignore import IgnoreMatcher
from ..metadata import get_plugin_metadata, update_general_keys
from ..naming import validate_slug

logger = logging.getLogger(__name__)


def is_prerelease(version: str) -> bool:
    """Return True if the version looks like a pre-release (rc, alpha, beta, dev)."""
    return bool(re.search(r"[-.](?:rc|alpha|beta|dev)\d*", version, re.IGNORECASE))


def get_git_info(project_root: Path) -> tuple[str | None, int | None]:
    """Return the (commit SHA, commit count) from git, or (None, None)."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root,
        ).stdout.strip()
        count_raw = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root,
        ).stdout.strip()
        return (sha or None, int(count_raw) if count_raw else None)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return (None, None)


def _build_metadata_updates(
    version: str | None,
    commit_sha: str | None,
    commit_number: int | None,
    timestamp: str | None,
    experimental: bool | None,
) -> dict[str, str]:
    """Collect the metadata keys to inject, skipping ``None`` values."""
    updates: dict[str, str] = {}
    if version is not None:
        updates["version"] = version
    if experimental is not None:
        updates["experimental"] = "True" if experimental else "False"
    if commit_sha is not None:
        updates["commitSha1"] = commit_sha
    if commit_number is not None:
        updates["commitNumber"] = str(commit_number)
    if timestamp is not None:
        updates["dateTime"] = timestamp
    return updates


def stamp_metadata_text(
    text: str,
    version: str | None = None,
    commit_sha: str | None = None,
    commit_number: int | None = None,
    timestamp: str | None = None,
    experimental: bool | None = None,
) -> str:
    """Patch a metadata.txt string with build metadata, preserving formatting.

    Existing keys in the ``[general]`` section are updated in place; new keys are
    appended at the end of that section. Comments, blank lines and other sections
    are left untouched.
    """
    updates = _build_metadata_updates(
        version, commit_sha, commit_number, timestamp, experimental
    )
    return update_general_keys(text, updates)


def _build_stamped_metadata(project_root: Path, version: str) -> str | None:
    """Return the stamped metadata.txt content, or None when no file exists."""
    metadata_path = project_root / "metadata.txt"
    if not metadata_path.exists():
        return None
    commit_sha, commit_number = get_git_info(project_root)
    timestamp = datetime.now(timezone.utc).strftime(  # noqa: UP017
        "%Y-%m-%dT%H:%M:%SZ"
    )
    content = stamp_metadata_text(
        metadata_path.read_text(encoding="utf-8"),
        version=version,
        commit_sha=commit_sha,
        commit_number=commit_number,
        timestamp=timestamp,
        experimental=is_prerelease(version),
    )
    logger.info("  🏷️  Stamped build metadata into metadata.txt")
    return content


def _is_packable(path: Path, matcher: IgnoreMatcher) -> bool:
    """Return True if a file should be added to the package ZIP."""
    return path.is_file() and not path.is_symlink() and not matcher.should_exclude(path)


def _zip_arcname(project_root: PurePath, file_path: PurePath, slug: str) -> str:
    """Return a POSIX ZIP member name (ZIP uses ``/`` on every platform)."""
    return f"{slug}/{file_path.relative_to(project_root).as_posix()}"


def _iter_package_files(directory: Path) -> Iterator[Path]:
    """Yield files under ``directory`` without following symlinks."""
    for current, dirnames, filenames in os.walk(directory, followlinks=False):
        root = Path(current)
        dirnames[:] = sorted(
            name for name in dirnames if not (root / name).is_symlink()
        )
        for name in sorted(filenames):
            path = root / name
            if not path.is_symlink():
                yield path


def _collect_zip_items(
    project_root: Path, matcher: IgnoreMatcher, slug: str, include_dev: bool
) -> list[tuple[Path, str]]:
    """Gather ``(path, arcname)`` tuples to write into the ZIP."""
    items: list[tuple[Path, str]] = []
    for item in get_source_files(project_root, include_dev=include_dev):
        if item.is_file():
            items.append((item, _zip_arcname(project_root, item, slug)))
        elif item.is_dir():
            for file_path in _iter_package_files(item):
                if _is_packable(file_path, matcher):
                    arcname = _zip_arcname(project_root, file_path, slug)
                    items.append((file_path, arcname))
    return items


def _zip_date_time() -> tuple[int, int, int, int, int, int]:
    """Return a deterministic ZIP timestamp, honoring SOURCE_DATE_EPOCH."""
    raw = os.environ.get("SOURCE_DATE_EPOCH")
    if raw:
        try:
            stamp = datetime.fromtimestamp(int(raw), tz=timezone.utc)  # noqa: UP017
        except (ValueError, OSError, OverflowError):
            pass
        else:
            if stamp.year >= 1980:
                return (
                    stamp.year,
                    stamp.month,
                    stamp.day,
                    stamp.hour,
                    stamp.minute,
                    stamp.second,
                )
    return (1980, 1, 1, 0, 0, 0)


def _write_zip(
    zip_path: Path,
    items: list[tuple[Path, str]],
    metadata_path: Path,
    metadata_content: str | None,
    callback: Callable[[int], Any] | None,
    normalize_permissions: bool = False,
) -> None:
    """Write the package ZIP, injecting stamped metadata when provided."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item, arcname in items:
            if normalize_permissions:
                mode = 0o755 if item.stat().st_mode & 0o100 else 0o644
                info = zipfile.ZipInfo(arcname, date_time=_zip_date_time())
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                data = (
                    metadata_content.encode("utf-8")
                    if metadata_content is not None and item == metadata_path
                    else item.read_bytes()
                )
                zipf.writestr(info, data)
            elif metadata_content is not None and item == metadata_path:
                zipf.writestr(arcname, metadata_content)
            else:
                zipf.write(item, arcname)
            if callback:
                callback(1)
            logger.debug(f"  ✅ {arcname}")


def _write_checksum(zip_path: Path, checksum_file: Path, zip_filename: str) -> str:
    """Write the SHA256 checksum file and return the hex digest."""
    sha256_hash = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    checksum = sha256_hash.hexdigest()
    with open(checksum_file, "w") as cf:
        cf.write(f"{checksum}  {zip_filename}\n")
    return checksum


def create_plugin_package(
    project_root: Path,
    output_dir: Path | None = None,
    include_dev: bool = False,
    callback: Callable[[int], Any] | None = None,
    stamp: bool = False,
    release_version: str | None = None,
    normalize_permissions: bool = False,
) -> Path:
    """
    Create a distributable ZIP package for the plugin.

    Args:
        project_root: Root directory of the plugin project
        output_dir: Output directory for the ZIP file (default: project_root/dist)
        include_dev: Include development files in the package
        stamp: Inject build metadata (version, git SHA, datetime, experimental)
            into the packaged metadata.txt without modifying the source file
        release_version: Override the version used for the ZIP name and stamping
        normalize_permissions: Normalize ZIP modes to 0644/0755 and timestamps

    Returns:
        Path to the created ZIP file
    """
    metadata = get_plugin_metadata(project_root)
    slug = validate_slug(str(metadata["slug"]), source="plugin metadata")
    version = release_version or metadata.get("version", "0.0.0")
    if any(separator in version for separator in ("/", "\\")) or version in {
        "",
        ".",
        "..",
    }:
        raise ValueError(f"Unsafe package version: {version!r}")

    metadata_content = _build_stamped_metadata(project_root, version) if stamp else None

    if output_dir is None:
        output_dir = project_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"{slug}.{version}.zip"
    zip_path = output_dir / zip_filename
    logger.info(f"📦 Creating package: {zip_filename}")

    matcher = IgnoreMatcher(project_root, include_dev=include_dev)
    items_to_zip = _collect_zip_items(project_root, matcher, slug, include_dev)
    if callback:
        callback(len(items_to_zip))

    metadata_path = project_root / "metadata.txt"
    _write_zip(
        zip_path,
        items_to_zip,
        metadata_path,
        metadata_content,
        callback,
        normalize_permissions=normalize_permissions,
    )

    checksum_file = output_dir / f"{zip_filename}.sha256"
    checksum = _write_checksum(zip_path, checksum_file, zip_filename)

    logger.info(f"✨ Package created: {zip_path}")
    logger.info(f"🔒 Checksum saved: {checksum_file}")
    logger.info(f"📊 SHA256: {checksum}")

    return zip_path
