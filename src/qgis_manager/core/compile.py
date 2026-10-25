"""Compilation of Qt resources, UI files, translations and documentation."""

import fnmatch
import importlib.util
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

#: Maximum time a single external compiler may run.
COMPILE_TIMEOUT_SECONDS = 300

#: Directories that never contain project sources to compile.
_COMPILE_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "libs",
    "node_modules",
    "venv",
}

#: Qt binding import prefixes emitted by uic/rcc that must be redirected to
#: the binding shipped with QGIS (PyQt5, PyQt6, PySide2 or PySide6).
_QT_IMPORT_PREFIXES = (
    "from PyQt5",
    "from PyQt6",
    "from PySide2",
    "from PySide6",
)


def _iter_compile_sources(project_root: Path, pattern: str) -> list[Path]:
    """Return matching source files, excluding vendor/build/cache directories."""
    matches: list[Path] = []
    for current, dirnames, filenames in os.walk(project_root):
        root = Path(current)
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in _COMPILE_EXCLUDED_DIRS and not (root / name).is_symlink()
        )
        for name in sorted(filenames):
            path = root / name
            if (
                fnmatch.fnmatch(name, pattern)
                and path.is_file()
                and not path.is_symlink()
            ):
                matches.append(path)
    return matches


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

    try:
        process.wait(timeout=COMPILE_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        raise
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
    except (OSError, subprocess.SubprocessError, shutil.Error) as e:
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
        total += len(_iter_compile_sources(project_root, "*.qrc"))
        total += len(_iter_compile_sources(project_root, "*.ui"))
    if res_type in ["translations", "all"]:
        total += len(_iter_compile_sources(project_root, "*.ts"))
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
    except (OSError, UnicodeDecodeError):
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

    except (OSError, UnicodeDecodeError) as e:
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
    except (OSError, UnicodeDecodeError) as e:
        logger.warning(f"  ⚠️  Failed to patch {py_file.name}: {e}")

    return False


@dataclass(frozen=True)
class CompileContext:
    """Shared state for bounded external compiler invocations."""

    project_root: Path
    callback: Callable[[str], Any] | None = None
    timeout: int = COMPILE_TIMEOUT_SECONDS

    def emit(self, message: str) -> None:
        if self.callback:
            self.callback(message)

    def run(self, command: list[str], label: str) -> bool:
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return True
        except FileNotFoundError:
            logger.error(f"  ❌ Tool not found: {command[0]}")
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            OSError,
        ) as exc:
            logger.error(f"  ❌ Error compiling {label}: {exc}")
        return False


def compile_ui_files(
    project_root: Path,
    callback: Callable[[str], Any] | None = None,
) -> bool:
    """Compile .ui files to Python using pyuic (PyQt5/PyQt6/PySide)."""
    ui_files = _iter_compile_sources(project_root, "*.ui")
    if not ui_files:
        return True

    uic_tool = get_uic_tool()
    if not uic_tool:
        logger.warning(
            "  ⚠️  No UIC tool found (pyuic6, pyuic5). Cannot compile UI files."
        )
        return False

    context = CompileContext(project_root, callback)
    success = True
    for ui in ui_files:
        py_file = ui.with_suffix(".py")
        rel_ui = ui.relative_to(project_root)
        context.emit(f"START:UI {rel_ui.name}")
        if not _is_stale(ui, py_file):
            logger.debug(f"  ⏭️  {rel_ui.name} up to date")
        else:
            logger.debug(
                f"🎨 Compiling UI: {rel_ui} -> {py_file.name} using {uic_tool}"
            )
            if context.run([uic_tool, "-o", str(py_file), str(ui)], ui.name):
                patch_ui_file(py_file)
            else:
                success = False
        context.emit(f"DONE:UI {rel_ui.name}")
    return success


def _compile_single_qrc(
    qrc: Path,
    context: CompileContext,
    rcc_tool: str,
) -> bool:
    """Compile a single .qrc file and patch the generated module."""
    py_file = qrc.with_suffix(".py")
    rel_qrc = qrc.relative_to(context.project_root)
    context.emit(f"START:Resource {rel_qrc.name}")
    logger.debug(f"🔨 Compiling resource: {rel_qrc} -> {py_file.name} using {rcc_tool}")
    if not context.run([rcc_tool, "-o", str(py_file), str(qrc)], qrc.name):
        return False
    patch_resource_file(py_file)
    context.emit(f"DONE:Resource {rel_qrc.name}")
    logger.debug("  ✅ Done.")
    return True


def _compile_qrc_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> bool:
    """Compile every .qrc file in the project using the detected RCC tool."""
    qrc_files = _iter_compile_sources(project_root, "*.qrc")
    if not qrc_files:
        return True
    rcc_tool = get_rcc_tool()
    if not rcc_tool:
        logger.error("  ❌ No RCC tool found (pyside6-rcc, pyside2-rcc, pyrcc5).")
        return False
    context = CompileContext(project_root, callback)
    success = True
    for qrc in qrc_files:
        if not _compile_single_qrc(qrc, context, rcc_tool):
            success = False
    return success


def _compile_single_ts(ts: Path, context: CompileContext) -> bool:
    """Compile a single .ts translation file with lrelease."""
    rel_ts = ts.relative_to(context.project_root)
    context.emit(f"START:Translation {rel_ts.name}")
    logger.debug(f"🌍 Compiling translation: {rel_ts}")
    if not context.run(["lrelease", str(ts)], ts.name):
        return False
    context.emit(f"DONE:Translation {rel_ts.name}")
    logger.debug("  ✅ Done.")
    return True


def _compile_ts_files(
    project_root: Path, callback: Callable[[str], Any] | None
) -> bool:
    """Compile every .ts translation file in the project."""
    context = CompileContext(project_root, callback)
    success = True
    for ts in _iter_compile_sources(project_root, "*.ts"):
        if not _compile_single_ts(ts, context):
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
