"""Compilation of Qt resources, UI files, translations and documentation."""

import logging
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _run_sphinx(cmd: list[str], callback: Callable[[str], Any] | None) -> None:
    """Run sphinx-build, streaming its output to the callback/logger."""
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

        _run_sphinx(cmd, callback)

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


def _compile_single_qrc(
    qrc: Path,
    project_root: Path,
    rcc_tool: str,
    callback: Callable[[str], Any] | None,
) -> None:
    """Compile a single .qrc file and patch the generated module."""
    py_file = qrc.with_suffix(".py")
    rel_qrc = qrc.relative_to(project_root)
    if callback:
        callback(f"START:Resource {rel_qrc.name}")
    logger.debug(f"🔨 Compiling resource: {rel_qrc} -> {py_file.name} using {rcc_tool}")

    try:
        subprocess.run(
            [rcc_tool, "-o", str(py_file), str(qrc)],
            check=True,
            capture_output=True,
            text=True,
        )
        patch_resource_file(py_file)
        if callback:
            callback(f"DONE:Resource {rel_qrc.name}")
        logger.debug("  ✅ Done.")
    except subprocess.CalledProcessError as e:
        logger.error(f"  ❌ Error compiling {qrc.name}: {e.stderr}")


def _compile_qrc_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> None:
    """Compile every .qrc file in the project using the detected RCC tool."""
    qrc_files = list(project_root.rglob("*.qrc"))
    if not qrc_files:
        return

    rcc_tool = get_rcc_tool()
    if not rcc_tool:
        logger.error("  ❌ No RCC tool found (pyside6-rcc, pyside2-rcc, pyrcc5).")
        return

    for qrc in qrc_files:
        _compile_single_qrc(qrc, project_root, rcc_tool, callback)


def _compile_single_ts(
    ts: Path,
    project_root: Path,
    callback: Callable[[str], Any] | None,
) -> None:
    """Compile a single .ts translation file with lrelease."""
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


def _compile_ts_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> None:
    """Compile every .ts translation file in the project."""
    for ts in project_root.rglob("*.ts"):
        _compile_single_ts(ts, project_root, callback)


def compile_qt_resources(
    project_root: Path,
    res_type: str = "all",
    callback: Callable[[str], Any] | None = None,
):
    """Compile Qt resources, UI files, translations, and documentation."""
    if res_type in ["resources", "all"]:
        # Compile .ui files to Python (pyuic) and .qrc resources to Python (rcc)
        compile_ui_files(project_root, callback=callback)
        _compile_qrc_files(project_root, callback)

    if res_type in ["translations", "all"]:
        _compile_ts_files(project_root, callback)

    if res_type in ["docs", "all"]:
        compile_docs(project_root, callback=callback)
