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
from .ignore import PathFilter, load_ignore_patterns

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


def sync_directory(src: Path, dst: Path, matcher: PathFilter):
    """Sync source to destination only copying changed files (rsync-like)."""
    if not dst.exists():
        dst.mkdir(parents=True)

    # 1. Copy/Update files from source
    for item in src.iterdir():
        if matcher.should_exclude(item):
            continue

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
        # (Though matcher is based on project_root, so relative paths matter)
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
    callback: Callable[[int], Any] | None = None,
    max_backups: int = 3,
):
    """Deploy the plugin to the QGIS directory."""
    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]

    if dest_dir is None:
        dest_dir = get_qgis_plugin_dir(profile)

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

    spec = load_ignore_patterns(project_root, include_dev=False)
    matcher = PathFilter(project_root, spec)

    # Use a set for callback progress if we use iterative sync
    # For now, we'll keep it simple and sync everything.
    logger.info(f"🚀 Syncing files to {target_path}")
    sync_directory(project_root, target_path, matcher)

    if callback:
        callback(100)  # Simple completion signal

    logger.info("✨ Deployment complete.")


def compile_docs(project_root: Path, callback: Callable[[str], Any] | None = None):
    """Compila la documentación Sphinx si el proyecto tiene una carpeta docs/source."""
    docs_source = project_root / "docs" / "source"
    if not (docs_source / "conf.py").exists():
        return

    # Ruta estándar para la ayuda en plugins de QGIS
    help_target = project_root / "help" / "html"

    if callback:
        callback(f"START:Documentación ({help_target.name})")
    logger.debug(f"📚 Compilando documentación: {docs_source} -> {help_target}")

    try:
        # Limpiar y regenerar carpeta destino
        if help_target.exists():
            shutil.rmtree(help_target)
        help_target.mkdir(parents=True, exist_ok=True)

        # Intentamos con uv run si detectamos entorno uv, o sphinx-build directamente
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

        # Limpieza de archivos innecesarios para el despliegue
        shutil.rmtree(help_target / "_sources", ignore_errors=True)
        (help_target / ".buildinfo").unlink(missing_ok=True)

        if callback:
            callback("DONE:Documentación")
        logger.debug("  ✅ Documentación compilada con éxito.")
    except Exception as e:
        logger.error(f"  ❌ Error al compilar documentación: {e}")


def get_rcc_tool() -> str | None:
    """Find the best available RCC tool."""
    tools = ["pyside6-rcc", "pyside2-rcc", "pyrcc5"]
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, check=False)
            return tool
        except FileNotFoundError:
            continue
    return None


def patch_resource_file(py_file: Path) -> bool:
    """Patch the generated .py resource file to use relative imports.

    RCC sometimes generates 'import resources_rc' which fails in a plugin package.
    """
    if not py_file.exists():
        return False

    try:
        content = py_file.read_text(encoding="utf-8")
        # Pattern often found: 'import resources_rc' or similar
        # We look for imports of other resource files that might have been compiled
        # In a typical QGIS plugin, we might have multiple .qrc files.
        import re

        # Fix 'import <name>_rc' to 'from . import <name>_rc'
        # This is a common issue when multiple resource files are used.
        patched_content = re.sub(
            r"^import (\w+_rc)", r"from . import \1", content, flags=re.MULTILINE
        )

        if patched_content != content:
            py_file.write_text(patched_content, encoding="utf-8")
            logger.debug(f"  ✅ Patched imports in {py_file.name}")
            return True
    except Exception as e:
        logger.warning(f"  ⚠️  Failed to patch {py_file.name}: {e}")

    return False


def compile_qt_resources(
    project_root: Path,
    res_type: str = "all",
    callback: Callable[[str], Any] | None = None,
):
    """Compile Qt resources, translations, and documentation."""
    if res_type in ["resources", "all"]:
        # Look for .qrc files
        qrc_files = list(project_root.rglob("*.qrc"))
        if qrc_files:
            rcc_tool = get_rcc_tool()
            if not rcc_tool:
                logger.error(
                    "  ❌ No RCC tool found (pyside6-rcc, pyside2-rcc, pyrcc5)."
                )
                return

            for qrc in qrc_files:
                py_file = qrc.with_suffix(".py")
                rel_qrc = qrc.relative_to(project_root)
                if callback:
                    callback(f"START:Recurso {rel_qrc.name}")
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
                        callback(f"DONE:Recurso {rel_qrc.name}")
                    logger.debug("  ✅ Done.")
                except subprocess.CalledProcessError as e:
                    logger.error(f"  ❌ Error compiling {qrc.name}: {e.stderr}")

    if res_type in ["translations", "all"]:
        # Look for .ts files
        ts_files = list(project_root.rglob("*.ts"))
        for ts in ts_files:
            rel_ts = ts.relative_to(project_root)
            if callback:
                callback(f"START:Trad {rel_ts.name}")
            logger.debug(f"🌍 Compiling translation: {rel_ts}")

            try:
                subprocess.run(
                    ["lrelease", str(ts)], check=True, capture_output=True, text=True
                )
                if callback:
                    callback(f"DONE:Trad {rel_ts.name}")
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

    spec = load_ignore_patterns(project_root, include_dev=include_dev)
    matcher = PathFilter(project_root, spec)

    # Collect items for ZIP
    items_to_zip = []
    for item in get_source_files(project_root, include_dev=include_dev):
        if item.is_file():
            items_to_zip.append((item, f"{slug}/{item.name}"))
        elif item.is_dir():
            for file_path in item.rglob("*"):
                if file_path.is_file() and not matcher.should_exclude(file_path):
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
    template: str = "default",
) -> None:
    """
    Initialize a new QGIS plugin project with scaffolding.

    Args:
        path: Directory where the project will be created
        name: Name of the plugin
        author: Author name
        email: Author email
        description: Short description of the plugin
        template: Template name to use (default, processing, dockwidget)
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

    # Template data
    class_name = name.replace(" ", "")
    context = {
        "name": name,
        "author": author,
        "email": email,
        "description": description,
        "slug": slug,
        "class_name": class_name,
    }

    template_base = Path(__file__).parent / "templates" / template
    if not template_base.exists():
        # Fallback to default if template not found
        logger.warning(f"Template '{template}' not found, falling back to 'default'")
        template_base = Path(__file__).parent / "templates" / "default"

    # Minimal implementation: we still handle some files manually if template
    # folder is empty but the goal is to favor the folder.

    def render_template(content: str, ctx: dict) -> str:
        for k, v in ctx.items():
            content = content.replace(f"{{{{ {k} }}}}", str(v))
        return content

    # 1. metadata.txt
    meta_tmpl = template_base / "metadata.txt.tmpl"
    if meta_tmpl.exists():
        with open(meta_tmpl) as f:
            content = render_template(f.read(), context)
        with open(project_dir / "metadata.txt", "w") as f:
            f.write(content)
        logger.debug("  ✅ Created metadata.txt from template")
    else:
        # Fallback to hardcoded if no template
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
        logger.debug("  ✅ Created metadata.txt (hardcoded)")

    # 2. __init__.py
    init_tmpl = template_base / "__init__.py.tmpl"
    if init_tmpl.exists():
        with open(init_tmpl) as f:
            content = render_template(f.read(), context)
        with open(project_dir / "__init__.py", "w") as f:
            f.write(content)
        logger.debug("  ✅ Created __init__.py from template")
    else:
        # Fallback to hardcoded if no template
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
        logger.debug("  ✅ Created __init__.py (hardcoded)")

    # 3. Main plugin file
    plugin_tmpl = template_base / "plugin.py.tmpl"
    if plugin_tmpl.exists():
        with open(plugin_tmpl) as f:
            content = render_template(f.read(), context)
        # Use slug as filename for the main login
        with open(project_dir / f"{slug}.py", "w") as f:
            f.write(content)
        logger.debug(f"  ✅ Created {slug}.py from template")
    else:
        # Fallback to hardcoded if no template
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
        logger.debug(f"  ✅ Created {slug}.py (hardcoded)")

    # 4. Create empty resources.qrc
    qrc_content = f"""<RCC>
    <qresource prefix="/plugins/{slug}">
    </qresource>
</RCC>
"""
    with open(project_dir / "resources.qrc", "w") as f:
        f.write(qrc_content)
    logger.debug("  ✅ Created resources.qrc")

    logger.info(f"✨ Project {name} initialized successfully.")
