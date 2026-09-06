# /***************************************************************************
#  QGIS Plugin Manager
#                                  A CLI Tool
#  Modern command-line interface for QGIS plugin development and deployment.
#                               -------------------
#         begin                : 2025-12-28
#         git sha              : $Format:%H$
#         copyright            : (C) 2025 by Juan M Bernales
#         email                : juanbernales@gmail.com
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Core functionality for QGIS plugin deployment and management.

This module provides functions to deploy QGIS plugins to local profiles,
compile Qt resources and translations, and clean build artifacts. It handles
cross-platform path detection for Linux, macOS, and Windows.

Functions:
    get_qgis_plugin_dir: Detect QGIS plugin directory based on OS and profile
    deploy_plugin: Deploy plugin with automatic backup and file copying
    compile_qt_resources: Compile .qrc resources and .ts translations
    clean_artifacts: Remove __pycache__ and .pyc files
    create_plugin_package: Create distributable ZIP package for plugin
    init_plugin_project: Scaffolding for a new QGIS plugin project
"""

import logging
import os
import shutil
import subprocess
import sys
import zipfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .discovery import get_plugin_metadata, get_source_files
from .ignore import IgnoreMatcher

logger = logging.getLogger(__name__)


def get_qgis_plugin_dir(profile: str = "default", version: int = 3) -> Path:
    """Detect the QGIS plugin directory based on the OS and version."""
    if sys.platform == "linux":
        return (
            Path.home()
            / f".local/share/QGIS/QGIS{version}/profiles/{profile}/python/plugins"
        )
    elif sys.platform == "darwin":
        return (
            Path.home()
            / f"Library/Application Support/QGIS/QGIS{version}/profiles"
            / profile
            / "python/plugins"
        )
    elif sys.platform == "win32":
        return (
            Path(os.environ["APPDATA"])
            / f"QGIS/QGIS{version}/profiles/{profile}/python/plugins"
        )
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")


def rotate_backups(parent_dir: Path, slug: str, limit: int):
    """Keep only the N most recent backups for a plugin."""
    if limit <= 0:
        return

    # Find all backup directories for this slug
    backups = []
    for item in parent_dir.iterdir():
        if item.is_dir() and item.name.startswith(f"{slug}.bak."):
            backups.append(item)

    # Sort by name (which contains timestamp) descending
    backups.sort(key=lambda x: x.name, reverse=True)

    # Remove those exceeding the limit
    if len(backups) > limit:
        cols = backups[limit:]
        for old_bak in cols:
            logger.debug(f"🧹 Removing old backup: {old_bak.name}")
            shutil.rmtree(old_bak)


def sync_directory(src: Path, dst: Path, matcher: IgnoreMatcher):
    """Sync source to destination only copying changed files (rsync-like)."""
    if not dst.exists():
        dst.mkdir(parents=True)

    # 1. Copy/Update files from source
    for item in src.iterdir():
        if matcher.should_exclude(item):
            continue

        # Safeguard: Do not copy the destination directory into itself
        # This prevents infinite recursion if deploying into a subfolder of the project
        try:
            is_same = item.resolve() == dst.resolve()
            is_nested = dst.resolve().is_relative_to(item.resolve())
            if is_same or is_nested:
                continue
        except Exception:
            pass

        dest_item = dst / item.name
        if item.is_dir():
            sync_directory(item, dest_item, matcher)
        else:
            # Check if we need to copy
            if dest_item.exists():
                src_stat = item.stat()
                dst_stat = dest_item.stat()
                # Skip if size and mtime match
                if (
                    src_stat.st_size == dst_stat.st_size
                    and src_stat.st_mtime == dst_stat.st_mtime
                ):
                    continue

            shutil.copy2(item, dest_item)
            logger.debug(f"  ✅ {item.name} (updated)")

    # 2. Cleanup files in destination that no longer exist in source
    # Important: only cleanup items NOT ignored (otherwise we'd delete things like .git)
    for item in dst.iterdir():
        source_item = src / item.name
        # If it doesn't exist in source AND is not ignored/dev file
        if not source_item.exists() and not matcher.should_exclude(source_item):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            logger.debug(f"  🗑️ {item.name} (removed from target)")


def deploy_plugin(
    project_root: Path,
    dest_dir: Path | None = None,
    no_backup: bool = False,
    profile: str = "default",
    qgis_version: int = 3,
    callback: Callable[[int], Any] | None = None,
    max_backups: int = 3,
):
    """Deploy the plugin to the QGIS directory."""
    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]

    if dest_dir is None:
        dest_dir = get_qgis_plugin_dir(profile, version=qgis_version)

    target_path = dest_dir / slug

    # Pre-deployment backup
    if target_path.exists() and not no_backup:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = target_path.parent / f"{slug}.bak.{timestamp}"
        logger.info(f"📦 Creating backup at: {backup_path.name}")
        shutil.copytree(target_path, backup_path)

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


def compile_docs(project_root: Path, callback: Callable[[str], Any] | None = None):
    """Compile Sphinx documentation if the project has a docs/source folder."""
    docs_source = project_root / "docs" / "source"
    if not (docs_source / "conf.py").exists():
        return

    # Standard path for help in QGIS plugins
    help_target = project_root / "help" / "html"

    if callback:
        callback(f"START:Documentation ({help_target.name})")
    logger.debug(f"📚 Compiling documentation: {docs_source} -> {help_target}")

    try:
        # Clean and regenerate the target folder
        if help_target.exists():
            shutil.rmtree(help_target)
        help_target.mkdir(parents=True, exist_ok=True)

        # Prefer `uv run` when a uv environment is detected, else sphinx-build
        cmd = ["sphinx-build", "-b", "html", str(docs_source), str(help_target)]
        if (project_root / "pyproject.toml").exists():
            # Recommendation to use uv if available for consistency with project rules
            cmd = ["uv", "run"] + cmd

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        if process.stdout:
            for line in process.stdout:
                line = line.strip()
                if line:
                    if callback:
                        callback(f"PROGRESS:{line}")
                    logger.debug(f"Sphinx: {line}")

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd)

        # Clean up files not needed for deployment
        shutil.rmtree(help_target / "_sources", ignore_errors=True)
        (help_target / ".buildinfo").unlink(missing_ok=True)

        if callback:
            callback("DONE:Documentation")
        logger.debug("  ✅ Documentation compiled successfully.")
    except Exception as e:
        logger.error(f"  ❌ Error compiling documentation: {e}")


def get_rcc_tool() -> str | None:
    """Find the best available RCC tool on the system PATH."""
    tools = ["pyside6-rcc", "pyside2-rcc", "pyrcc5"]
    for tool in tools:
        if shutil.which(tool):
            return tool
    return None


def get_uic_tool() -> str | None:
    """Find the best available UIC tool (pyuic6 preferred over pyuic5)."""
    tools = ["pyuic6", "pyuic5"]
    for tool in tools:
        if shutil.which(tool):
            return tool
    return None


def _is_stale(source: Path, target: Path) -> bool:
    """Return True if target is missing or older than source (by mtime).

    Compares only modification time: for compiled outputs (e.g. ``.ui`` ->
    ``.py``) the file sizes are inherently different, so size is not a
    meaningful signal.
    """
    try:
        return source.stat().st_mtime > target.stat().st_mtime
    except OSError:
        return True


def count_compile_steps(project_root: Path, res_type: str) -> int:
    """Count the number of compilation steps for a resource type.

    Args:
        project_root: Root directory of the plugin project.
        res_type: One of "resources", "translations", "docs", or "all".

    Returns:
        Total number of steps to compile.
    """
    total = 0
    if res_type in ["resources", "all"]:
        total += len(list(project_root.rglob("*.qrc")))
        total += len(list(project_root.rglob("*.ui")))
    if res_type in ["translations", "all"]:
        total += len(list(project_root.rglob("*.ts")))
    if res_type in ["docs", "all"]:
        if (project_root / "docs" / "source" / "conf.py").exists():
            total += 1
    return total


def verify_resource_patch(py_file: Path) -> bool:
    """Verify that a resource file contains correct imports."""
    try:
        content = py_file.read_text(encoding="utf-8")
        if (
            "import resources_rc" in content
            and "from . import resources_rc" not in content
        ):
            return False
        for prefix in ("from PyQt5", "from PySide2", "from PySide6"):
            if prefix in content:
                return False
        return True
    except Exception:
        return False


def patch_resource_file(py_file: Path) -> bool:
    """Patch the generated .py resource file to use relative imports.

    RCC sometimes generates 'import resources_rc' which fails in a plugin package.
    """
    if not py_file.exists():
        return False

    try:
        content = py_file.read_text(encoding="utf-8")
        original_content = content
        import re

        # Fix 'import <name>_rc' to 'from . import <name>_rc'
        # Only if not already relative
        if re.search(r"^import \w+_rc", content, flags=re.MULTILINE):
            content = re.sub(
                r"^import (\w+_rc)", r"from . import \1", content, flags=re.MULTILINE
            )

        # Fix Qt imports to the QGIS-compatible namespace
        for prefix in ("from PyQt5", "from PySide2", "from PySide6"):
            content = content.replace(prefix, "from qgis.PyQt")

        if content != original_content:
            py_file.write_text(content, encoding="utf-8")
            logger.debug(f"  ✅ Patched imports in {py_file.name}")

            # Verification step
            if not verify_resource_patch(py_file):
                logger.warning(
                    f"  ⚠️  Patch verification failed for {py_file.name}. "
                    "It may still contain invalid imports."
                )
            return True

    except Exception as e:
        logger.warning(f"  ⚠️  Failed to patch {py_file.name}: {e}")

    return False


def patch_ui_file(py_file: Path) -> bool:
    """Patch a pyuic-generated .py file to use the QGIS ``qgis.PyQt`` namespace.

    pyuic emits ``from PyQt5``/``from PySide2``/``from PySide6`` imports, which
    fail inside a QGIS plugin. Replace them with ``from qgis.PyQt``.
    """
    if not py_file.exists():
        return False

    try:
        content = py_file.read_text(encoding="utf-8")
        original_content = content

        for prefix in ("from PyQt5", "from PySide2", "from PySide6"):
            content = content.replace(prefix, "from qgis.PyQt")

        if content != original_content:
            py_file.write_text(content, encoding="utf-8")
            logger.debug(f"  ✅ Patched UI imports in {py_file.name}")
            return True
    except Exception as e:
        logger.warning(f"  ⚠️  Failed to patch {py_file.name}: {e}")

    return False


def compile_ui_files(
    project_root: Path,
    callback: Callable[[str], Any] | None = None,
):
    """Compile .ui files to Python using pyuic (PyQt5/PySide6).

    Only files whose source changed (mtime/size) since the last compilation
    are recompiled.
    """
    ui_files = list(project_root.rglob("*.ui"))
    if not ui_files:
        return

    uic_tool = get_uic_tool()
    if not uic_tool:
        logger.warning(
            "  ⚠️  No UIC tool found (pyuic6, pyuic5). Skipping UI compilation."
        )
        return

    for ui in ui_files:
        py_file = ui.with_suffix(".py")
        rel_ui = ui.relative_to(project_root)
        if callback:
            callback(f"START:UI {rel_ui.name}")

        if not _is_stale(ui, py_file):
            logger.debug(f"  ⏭️  {rel_ui.name} up to date")
        else:
            logger.debug(
                f"🎨 Compiling UI: {rel_ui} -> {py_file.name} using {uic_tool}"
            )
            try:
                subprocess.run(
                    [uic_tool, "-o", str(py_file), str(ui)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                patch_ui_file(py_file)
            except subprocess.CalledProcessError as e:
                logger.error(f"  ❌ Error compiling {ui.name}: {e.stderr}")

        if callback:
            callback(f"DONE:UI {rel_ui.name}")


def compile_qt_resources(
    project_root: Path,
    res_type: str = "all",
    callback: Callable[[str], Any] | None = None,
):
    """Compile Qt resources, translations, and documentation."""
    if res_type in ["resources", "all"]:
        # Compile .ui files to Python (pyuic)
        compile_ui_files(project_root, callback=callback)

        # Look for .qrc files
        qrc_files = list(project_root.rglob("*.qrc"))
        if qrc_files:
            rcc_tool = get_rcc_tool()
            if not rcc_tool:
                logger.error(
                    "  ❌ No RCC tool found (pyside6-rcc, pyside2-rcc, pyrcc5)."
                )
            else:
                for qrc in qrc_files:
                    py_file = qrc.with_suffix(".py")
                    rel_qrc = qrc.relative_to(project_root)
                    if callback:
                        callback(f"START:Resource {rel_qrc.name}")
                    logger.debug(
                        f"🔨 Compiling resource: {rel_qrc} -> {py_file.name} "
                        f"using {rcc_tool}"
                    )

                    try:
                        subprocess.run(
                            [rcc_tool, "-o", str(py_file), str(qrc)],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        # Apply patching
                        patch_resource_file(py_file)

                        if callback:
                            callback(f"DONE:Resource {rel_qrc.name}")
                        logger.debug("  ✅ Done.")
                    except subprocess.CalledProcessError as e:
                        logger.error(f"  ❌ Error compiling {qrc.name}: {e.stderr}")

    if res_type in ["translations", "all"]:
        # Look for .ts files
        ts_files = list(project_root.rglob("*.ts"))
        for ts in ts_files:
            rel_ts = ts.relative_to(project_root)
            if callback:
                callback(f"START:Translation {rel_ts.name}")
            logger.debug(f"🌍 Compiling translation: {rel_ts}")

            try:
                subprocess.run(
                    ["lrelease", str(ts)], check=True, capture_output=True, text=True
                )
                if callback:
                    callback(f"DONE:Translation {rel_ts.name}")
                logger.debug("  ✅ Done.")
            except subprocess.CalledProcessError as e:
                logger.error(f"  ❌ Error compiling {ts.name}: {e.stderr}")
            except FileNotFoundError:
                logger.error("  ❌ lrelease not found. Is it installed?")

    if res_type in ["docs", "all"]:
        compile_docs(project_root, callback=callback)


def clean_artifacts(project_root: Path):
    """Clean build artifacts."""
    logger.info("Cleaning artifacts...")

    # Directorios a eliminar
    cache_dirs = ["__pycache__", ".pytest_cache", ".ruff_cache"]
    for dir_name in cache_dirs:
        for item in project_root.rglob(dir_name):
            if item.is_dir():
                shutil.rmtree(item)
                logger.debug(f"  🗑️ {item.relative_to(project_root)}")

    # Archivos a eliminar
    cache_files = ["*.pyc", "*.qpj", "*.cpg"]
    for file_pattern in cache_files:
        for item in project_root.rglob(file_pattern):
            if item.is_file():
                item.unlink()
                logger.debug(f"  🗑️ {item.relative_to(project_root)}")

    logger.info("✨ Clean complete.")


def is_prerelease(version: str) -> bool:
    """Return True if the version looks like a pre-release (rc, alpha, beta, dev)."""
    import re

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
    import re

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

    if not updates:
        return text

    lines = text.split("\n")
    out: list[str] = []
    in_general = False
    applied: set[str] = set()
    general_tail = -1  # index in `out` right after the last [general] key

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_general = stripped == "[general]"
            out.append(line)
            continue

        if in_general:
            match = re.match(
                r"^(\s*)([A-Za-z][A-Za-z0-9_]*)\s*([=:])\s*(.*)$", line
            )
            if match:
                key = match.group(2)
                if key in updates:
                    indent = match.group(1)
                    sep = match.group(3)
                    out.append(f"{indent}{key}{sep}{updates[key]}")
                    applied.add(key)
                else:
                    out.append(line)
                general_tail = len(out)
                continue

        out.append(line)

    remaining = [k for k in updates if k not in applied]
    if remaining:
        if general_tail < 0:
            if out and out[-1].strip() != "":
                out.append("")
            out.append("[general]")
            general_tail = len(out)
        out[general_tail:general_tail] = [f"{k}={updates[k]}" for k in remaining]

    return "\n".join(out)


def create_plugin_package(
    project_root: Path,
    output_dir: Path | None = None,
    include_dev: bool = False,
    callback: Callable[[int], Any] | None = None,
    stamp: bool = False,
    release_version: str | None = None,
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

    Returns:
        Path to the created ZIP file
    """
    import hashlib

    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]
    version = release_version or metadata.get("version", "0.0.0")

    # Build the stamped metadata.txt content to write into the ZIP (in memory).
    metadata_content: str | None = None
    if stamp:
        metadata_path = project_root / "metadata.txt"
        if metadata_path.exists():
            commit_sha, commit_number = get_git_info(project_root)
            timestamp = datetime.now(timezone.utc).strftime(  # noqa: UP017
                "%Y-%m-%dT%H:%M:%SZ"
            )
            metadata_content = stamp_metadata_text(
                metadata_path.read_text(encoding="utf-8"),
                version=version,
                commit_sha=commit_sha,
                commit_number=commit_number,
                timestamp=timestamp,
                experimental=is_prerelease(version),
            )
            logger.info("  🏷️  Stamped build metadata into metadata.txt")

    # Determine output directory
    if output_dir is None:
        output_dir = project_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create ZIP filename
    zip_filename = f"{slug}.{version}.zip"
    zip_path = output_dir / zip_filename

    logger.info(f"📦 Creating package: {zip_filename}")

    matcher = IgnoreMatcher(project_root, include_dev=include_dev)

    # Collect items for ZIP
    items_to_zip = []
    for item in get_source_files(project_root, include_dev=include_dev):
        if item.is_file():
            items_to_zip.append((item, f"{slug}/{item.name}"))
        elif item.is_dir():
            for file_path in item.rglob("*"):
                if (
                    file_path.is_file()
                    and not file_path.is_symlink()
                    and not matcher.should_exclude(file_path)
                ):  # noqa: E501
                    arcname = f"{slug}/{file_path.relative_to(project_root)}"
                    items_to_zip.append((file_path, arcname))

    if callback:
        callback(len(items_to_zip))

    # Create ZIP file
    metadata_path = project_root / "metadata.txt"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item, arcname in items_to_zip:
            if metadata_content is not None and item == metadata_path:
                zipf.writestr(arcname, metadata_content)
            else:
                zipf.write(item, arcname)
            if callback:
                callback(1)
            logger.debug(f"  ✅ {arcname}")

    # Generate SHA256 checksum
    sha256_hash = hashlib.sha256()
    with open(zip_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    checksum = sha256_hash.hexdigest()
    checksum_file = output_dir / f"{zip_filename}.sha256"

    with open(checksum_file, "w") as cf:
        cf.write(f"{checksum}  {zip_filename}\n")

    logger.info(f"✨ Package created: {zip_path}")
    logger.info(f"🔒 Checksum saved: {checksum_file}")
    logger.info(f"📊 SHA256: {checksum}")

    return zip_path


def init_plugin_project(
    path: Path,
    name: str,
    author: str,
    email: str,
    description: str = "A QGIS plugin.",
    template: str = "default",
) -> None:
    """
    Initialize a new QGIS plugin project with scaffolding.
    """
    from .discovery import slugify

    slug = slugify(name)
    project_dir = path / slug
    if project_dir.exists():
        raise FileExistsError(f"Directory {project_dir} already exists.")

    project_dir.mkdir(parents=True)

    logger.info(
        f"🚀 Initializing new QGIS plugin: {name} in {project_dir} "
        f"(Template: {template})"
    )

    class_name = name.replace(" ", "")

    # 1. metadata.txt
    metadata_content = f"""; QGIS Plugin Metadata
[general]
name={name}
description={description}
about={description}
version=0.1
qgisMinimumVersion=3.0
author={author}
email={email}
repository=
tracker=
homepage=
category=Plugins
tags=
icon=icon.png
experimental=False
deprecated=False
"""
    with open(project_dir / "metadata.txt", "w") as f:
        f.write(metadata_content)

    # 2. __init__.py
    init_py_content = f"""\"\"\"
{name} initialization.
\"\"\"

def classFactory(iface):
    \"\"\"Load the plugin class.\"\"\"
    from .{slug} import {class_name}
    return {class_name}(iface)
"""
    with open(project_dir / "__init__.py", "w") as f:
        f.write(init_py_content)

    # 3. Main plugin file
    main_py_content = f"""\"\"\"
Main plugin class for {name}.
\"\"\"

class {class_name}:
    \"\"\"QGIS Plugin Implementation.\"\"\"

    def __init__(self, iface):
        \"\"\"Initialize the plugin.\"\"\"
        self.iface = iface

    def initGui(self):
        \"\"\"Initialize the GUI.\"\"\"
        pass

    def unload(self):
        \"\"\"Unload the plugin.\"\"\"
        pass
"""
    with open(project_dir / f"{slug}.py", "w") as f:
        f.write(main_py_content)

    # 4. Create empty resources.qrc
    qrc_content = f"""<RCC>
    <qresource prefix="/plugins/{slug}">
    </qresource>
</RCC>
"""
    with open(project_dir / "resources.qrc", "w") as f:
        f.write(qrc_content)

    logger.info(f"✨ Project {name} initialized successfully.")
