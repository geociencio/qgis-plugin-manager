import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from .discovery import get_plugin_metadata, get_source_files
import logging

logger = logging.getLogger(__name__)

def get_qgis_plugin_dir() -> Path:
    """Detect the QGIS plugin directory based on the OS."""
    if sys.platform == "linux":
        return Path.home() / ".local/share/QGIS/QGIS3/profiles/default/python/plugins"
    elif sys.platform == "darwin":
        return Path.home() / "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
    elif sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "QGIS/QGIS3/profiles/default/python/plugins"
    else:
        raise OSError(f"Unsupported platform: {sys.platform}")

def deploy_plugin(project_root: Path, dest_dir: Path = None, no_backup: bool = False):
    """Deploy the plugin to the QGIS directory."""
    metadata = get_plugin_metadata(project_root)
    slug = metadata["slug"]
    
    if dest_dir is None:
        dest_dir = get_qgis_plugin_dir()
    
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
             "__pycache__", ".git", ".venv", ".agent", ".ai-context", 
             "tests", "research", "tools", "scripts"
        }
        return [c for c in contents if c in exclude_set or c.endswith(".pyc")]

    # Copy files
    for item in get_source_files(project_root):
        dest_item = target_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item, ignore=ignore_func, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest_item)
            shutil.copy2(item, dest_item)
        logger.debug(f"  ✅ {item.name}")

    logger.info("✨ Deployment complete.")

def compile_qt_resources(project_root: Path, res_type="all"):
    """Compile Qt resources and translations."""
    if res_type in ["resources", "all"]:
        # Look for .qrc files
        qrc_files = list(project_root.rglob("*.qrc"))
        for qrc in qrc_files:
            py_file = qrc.with_suffix(".py")
            py_file = qrc.with_suffix(".py")
            logger.info(f"🔨 Compiling resource: {qrc.relative_to(project_root)} -> {py_file.relative_to(project_root)}")
            if os.system(f"pyrcc5 -o {py_file} {qrc}") == 0:
                logger.info("  ✅ Done.")
            else:
                logger.error("  ❌ Error.")

    if res_type in ["translations", "all"]:
        # Look for .ts files
        ts_files = list(project_root.rglob("*.ts"))
        for ts in ts_files:
            logger.info(f"🌍 Compiling translation: {ts.relative_to(project_root)}")
            if os.system(f"lrelease {ts}") == 0:
                logger.info("  ✅ Done.")
            else:
                logger.error("  ❌ Error.")

def clean_artifacts(project_root: Path):
    """Clean build artifacts."""
    logger.info("清理 artifacts...")
    for item in project_root.rglob("__pycache__"):
        shutil.rmtree(item)
        logger.debug(f"  🗑️ {item.relative_to(project_root)}")
    
    for item in project_root.rglob("*.pyc"):
        item.unlink()
        logger.debug(f"  🗑️ {item.relative_to(project_root)}")
    logger.info("✨ Clean complete.")
