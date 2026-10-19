"""Compilation of Qt resources, UI files, translations and documentation."""

import importlib.util
import logging
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

#: Qt binding import prefixes emitted by uic/rcc that must be redirected to
#: the binding shipped with QGIS (PyQt5, PyQt6, PySide2 or PySide6).
_QT_IMPORT_PREFIXES = (
    "from PyQt5",
    "from PyQt6",
    "from PySide2",
    "from PySide6",
)


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


def _sphinx_command() -> list[str] | None:
    """Return the command prefix used to run Sphinx, or None if unavailable.

    A ``sphinx-build`` executable on ``PATH`` is preferred.  Otherwise the
    Sphinx module installed in the current interpreter is used.  The project's
    ``pyproject.toml`` is deliberately not consulted: forcing ``uv run`` made
    documentation compilation fail on machines without ``uv`` or without
    Sphinx in the project environment.
    """
    sphinx_build = shutil.which("sphinx-build")
    if sphinx_build:
        return [sphinx_build]

    try:
        if importlib.util.find_spec("sphinx") is not None:
            return [sys.executable, "-m", "sphinx"]
    except (ImportError, ValueError):
        pass
    return None


def compile_docs(
    project_root: Path, callback: Callable[[str], Any] | None = None
) -> bool:
    """Compile Sphinx documentation into ``help/html`` if configured.

    The build happens in a temporary directory that only replaces the existing
    ``help/html`` after a successful Sphinx run, so a failure never deletes the
    previous documentation.

    Args:
        project_root: Root directory of the plugin project.
        callback: Optional progress callback receiving ``START:``/``PROGRESS:``/
            ``DONE:`` lines.

    Returns:
        True when there is nothing to compile or compilation succeeded, False
        when Sphinx is unavailable or the build failed.
    """
    docs_source = project_root / "docs" / "source"
    if not (docs_source / "conf.py").exists():
        return True

    # Standard path for help in QGIS plugins
    help_target = project_root / "help" / "html"
    command = _sphinx_command()
    if command is None:
        logger.error(
            "  ❌ Sphinx not found. Install sphinx or add sphinx-build to PATH."
        )
        return False

    if callback:
        callback(f"START:Documentation ({help_target.name})")
    logger.debug(f"📚 Compiling documentation: {docs_source} -> {help_target}")

    help_parent = help_target.parent
    help_parent.mkdir(parents=True, exist_ok=True)
    build_dir = Path(tempfile.mkdtemp(prefix="html-", dir=help_parent))

    try:
        cmd = [*command, "-b", "html", str(docs_source), str(build_dir)]
        _run_sphinx(cmd, callback)

        # Clean up files not needed for deployment
        shutil.rmtree(build_dir / "_sources", ignore_errors=True)
        (build_dir / ".buildinfo").unlink(missing_ok=True)

        if help_target.exists():
            shutil.rmtree(help_target)
        shutil.move(str(build_dir), str(help_target))

        if callback:
            callback("DONE:Documentation")
        logger.debug("  ✅ Documentation compiled successfully.")
        return True
    except Exception as e:
        logger.error(f"  ❌ Error compiling documentation: {e}")
        shutil.rmtree(build_dir, ignore_errors=True)
        return False


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
        for prefix in _QT_IMPORT_PREFIXES:
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
        for prefix in _QT_IMPORT_PREFIXES:
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

    pyuic emits ``from PyQt5``/``from PyQt6``/``from PySide2``/``from PySide6``
    imports, which fail inside a QGIS plugin. Replace them with
    ``from qgis.PyQt``.
    """
    if not py_file.exists():
        return False

    try:
        content = py_file.read_text(encoding="utf-8")
        original_content = content

        for prefix in _QT_IMPORT_PREFIXES:
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
) -> bool:
    """Compile .ui files to Python using pyuic (PyQt5/PyQt6/PySide).

    Only files whose source changed (mtime/size) since the last compilation
    are recompiled.

    Args:
        project_root: Root directory of the plugin project.
        callback: Optional progress callback.

    Returns:
        True if there was nothing to compile or every file compiled, False when
        a tool is missing or a compilation failed.
    """
    ui_files = list(project_root.rglob("*.ui"))
    if not ui_files:
        return True

    uic_tool = get_uic_tool()
    if not uic_tool:
        logger.warning(
            "  ⚠️  No UIC tool found (pyuic6, pyuic5). Cannot compile UI files."
        )
        return False

    success = True
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
            except (subprocess.CalledProcessError, OSError) as e:
                logger.error(f"  ❌ Error compiling {ui.name}: {e}")
                success = False

        if callback:
            callback(f"DONE:UI {rel_ui.name}")

    return success


def _compile_single_qrc(
    qrc: Path,
    project_root: Path,
    rcc_tool: str,
    callback: Callable[[str], Any] | None,
) -> bool:
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
        return True
    except (subprocess.CalledProcessError, OSError) as e:
        logger.error(f"  ❌ Error compiling {qrc.name}: {e}")
        return False


def _compile_qrc_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> bool:
    """Compile every .qrc file in the project using the detected RCC tool."""
    qrc_files = list(project_root.rglob("*.qrc"))
    if not qrc_files:
        return True

    rcc_tool = get_rcc_tool()
    if not rcc_tool:
        logger.error("  ❌ No RCC tool found (pyside6-rcc, pyside2-rcc, pyrcc5).")
        return False

    success = True
    for qrc in qrc_files:
        if not _compile_single_qrc(qrc, project_root, rcc_tool, callback):
            success = False
    return success


def _compile_single_ts(
    ts: Path,
    project_root: Path,
    callback: Callable[[str], Any] | None,
) -> bool:
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
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"  ❌ Error compiling {ts.name}: {e}")
        return False
    except FileNotFoundError:
        logger.error("  ❌ lrelease not found. Is it installed?")
        return False


def _compile_ts_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> bool:
    """Compile every .ts translation file in the project."""
    success = True
    for ts in project_root.rglob("*.ts"):
        if not _compile_single_ts(ts, project_root, callback):
            success = False
    return success


def compile_qt_resources(
    project_root: Path,
    res_type: str = "all",
    callback: Callable[[str], Any] | None = None,
) -> bool:
    """Compile Qt resources, UI files, translations, and documentation.

    Args:
        project_root: Root directory of the plugin project.
        res_type: One of ``resources``, ``translations``, ``docs`` or ``all``.
        callback: Optional progress callback.

    Returns:
        True when every requested step succeeded (or there was nothing to do),
        False if any step failed.
    """
    success = True

    if res_type in ["resources", "all"]:
        # Compile .ui files to Python (pyuic) and .qrc resources to Python (rcc)
        success = compile_ui_files(project_root, callback=callback) and success
        success = _compile_qrc_files(project_root, callback) and success

    if res_type in ["translations", "all"]:
        success = _compile_ts_files(project_root, callback) and success

    if res_type in ["docs", "all"]:
        success = compile_docs(project_root, callback=callback) and success

    return success
