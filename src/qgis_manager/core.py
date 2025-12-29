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
from datetime import datetime
from pathlib import Path
from typing import Any

from .discovery import get_plugin_metadata, get_source_files

logger = logging.getLogger(__name__)


def get_qgis_plugin_dir(profile: str = "default") -> Path:
    """Detect the QGIS plugin directory based on the OS."""
    if sys.platform == "linux":
        return (
            Path.home() / f".local/share/QGIS/QGIS3/profiles/{profile}/python/plugins"
        )
    elif sys.platform == "darwin":
        return (
            Path.home()
            / "Library/Application Support/QGIS/QGIS3/profiles"
            / profile
            / "python/plugins"
        )
    elif sys.platform == "win32":
        return (
            Path(os.environ["APPDATA"])
            / f"QGIS/QGIS3/profiles/{profile}/python/plugins"
        )
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")


def deploy_plugin(
    project_root: Path,
    dest_dir: Path | None = None,
    no_backup: bool = False,
    profile: str = "default",
    callback: Callable[[int], Any] | None = None,
):
    """Deploy the plugin to the QGIS directory."""
    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]

    if dest_dir is None:
        dest_dir = get_qgis_plugin_dir(profile)

    target_path = dest_dir / slug

    print(f"🚀 Deploying '{metadata['name']}' ({slug}) to {target_path}")

    # Backup
    if target_path.exists() and not no_backup:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = target_path.parent / f"{slug}.bak.{timestamp}"
        backup_path = target_path.parent / f"{slug}.bak.{timestamp}"
        logger.info(f"📦 Creating backup at: {backup_path}")
        shutil.copytree(target_path, backup_path)

    # Clean target
    if target_path.exists():
        shutil.rmtree(target_path)
    target_path.mkdir(parents=True, exist_ok=True)

    # Exclusions for copytree
    def ignore_func(directory, contents):
        exclude_set = {
            "__pycache__",
            ".git",
            ".venv",
            ".agent",
            ".ai-context",
            "tests",
            "research",
            "tools",
            "scripts",
        }
        return [c for c in contents if c in exclude_set or c.endswith(".pyc")]

    # Copy files
    source_files = list(get_source_files(project_root))
    if callback:
        callback(len(source_files))

    for item in source_files:
        dest_item = target_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item, ignore=ignore_func, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest_item)

        if callback:
            callback(1)
        logger.debug(f"  ✅ {item.name}")

    logger.info("✨ Deployment complete.")


def compile_qt_resources(project_root: Path, res_type="all"):
    """Compile Qt resources and translations."""
    if res_type in ["resources", "all"]:
        # Look for .qrc files
        qrc_files = list(project_root.rglob("*.qrc"))
        for qrc in qrc_files:
            py_file = qrc.with_suffix(".py")
            logger.info(
                f"🔨 Compiling resource: {qrc.relative_to(project_root)} -> "
                f"{py_file.relative_to(project_root)}"
            )
            try:
                subprocess.run(
                    ["pyrcc5", "-o", str(py_file), str(qrc)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                logger.info("  ✅ Done.")
            except subprocess.CalledProcessError as e:
                logger.error(f"  ❌ Error compiling {qrc.name}: {e.stderr}")
            except FileNotFoundError:
                logger.error("  ❌ pyrcc5 not found. Is it installed?")

    if res_type in ["translations", "all"]:
        # Look for .ts files
        ts_files = list(project_root.rglob("*.ts"))
        for ts in ts_files:
            logger.info(f"🌍 Compiling translation: {ts.relative_to(project_root)}")
            try:
                subprocess.run(
                    ["lrelease", str(ts)], check=True, capture_output=True, text=True
                )
                logger.info("  ✅ Done.")
            except subprocess.CalledProcessError as e:
                logger.error(f"  ❌ Error compiling {ts.name}: {e.stderr}")
            except FileNotFoundError:
                logger.error("  ❌ lrelease not found. Is it installed?")


def clean_artifacts(project_root: Path):
    """Clean build artifacts."""
    logger.info("Cleaning artifacts...")
    for item in project_root.rglob("__pycache__"):
        shutil.rmtree(item)
        logger.debug(f"  🗑️ {item.relative_to(project_root)}")

    for item in project_root.rglob("*.pyc"):
        item.unlink()
        logger.debug(f"  🗑️ {item.relative_to(project_root)}")
    logger.info("✨ Clean complete.")


def create_plugin_package(
    project_root: Path,
    output_dir: Path | None = None,
    include_dev: bool = False,
    callback: Callable[[int], Any] | None = None,
) -> Path:
    """
    Create a distributable ZIP package for the plugin.

    Args:
        project_root: Root directory of the plugin project
        output_dir: Output directory for the ZIP file (default: project_root/dist)
        include_dev: Include development files in the package

    Returns:
        Path to the created ZIP file
    """
    import hashlib

    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]
    version = metadata.get("version", "0.0.0")

    # Determine output directory
    if output_dir is None:
        output_dir = project_root / "dist"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create ZIP filename
    zip_filename = f"{slug}.{version}.zip"
    zip_path = output_dir / zip_filename

    logger.info(f"📦 Creating package: {zip_filename}")

    # Files/directories to exclude
    exclude_patterns = {
        "__pycache__",
        ".git",
        ".venv",
        ".agent",
        ".ai-context",
        "venv",
        "env",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "*.pyc",
        "*.bak*",
        "dist",
        "build",
        "*.egg-info",
    }

    if not include_dev:
        exclude_patterns.update(
            {"tests", "research", "tools", "scripts", "docs", ".github"}
        )

    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded from package."""
        # Check if any parent or the path itself matches exclude patterns
        for part in path.parts:
            if part in exclude_patterns:
                return True
            # Check wildcard patterns
            if any(path.match(p) for p in exclude_patterns if "*" in p):
                return True
        return False

    # Collect items for ZIP
    items_to_zip = []
    for item in get_source_files(project_root):
        if should_exclude(item):
            continue

        if item.is_file():
            items_to_zip.append((item, f"{slug}/{item.name}"))
        elif item.is_dir():
            for file_path in item.rglob("*"):
                if file_path.is_file() and not should_exclude(file_path):
                    arcname = f"{slug}/{file_path.relative_to(project_root)}"
                    items_to_zip.append((file_path, arcname))

    if callback:
        callback(len(items_to_zip))

    # Create ZIP file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item, arcname in items_to_zip:
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
) -> None:
    """
    Initialize a new QGIS plugin project with basic scaffolding.

    Args:
        path: Directory where the project will be created
        name: Name of the plugin
        author: Author name
        email: Author email
        description: Short description of the plugin
    """
    from .discovery import slugify

    slug = slugify(name)
    project_dir = path / slug
    project_dir.mkdir(parents=True, exist_ok=False)

    logger.info(f"🚀 Initializing new QGIS plugin: {name} in {project_dir}")

    # 1. Create metadata.txt
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
    logger.debug("  ✅ Created metadata.txt")

    # 2. Create __init__.py
    init_py_content = f"""\"\"\"
{name} initialization.
\"\"\"

def classFactory(iface):
    \"\"\"Load the plugin class.\"\"\"
    from .{slug} import {name.replace(" ", "")}
    return {name.replace(" ", "")}(iface)
"""
    with open(project_dir / "__init__.py", "w") as f:
        f.write(init_py_content)
    logger.debug("  ✅ Created __init__.py")

    # 3. Create main plugin file
    class_name = name.replace(" ", "")
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
    logger.debug(f"  ✅ Created {slug}.py")

    # 4. Create empty resources.qrc
    qrc_content = f"""<RCC>
    <qroot prefix="/plugins/{slug}">
    </qroot>
</RCC>
"""
    with open(project_dir / "resources.qrc", "w") as f:
        f.write(qrc_content)
    logger.debug("  ✅ Created resources.qrc")

    logger.info(f"✨ Project {name} initialized successfully.")
