import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from qgis_manager.core import (
    compile_docs,
    compile_qt_resources,
    compile_ui_files,
    count_compile_steps,
    get_uic_tool,
    patch_ui_file,
)
from qgis_manager.core.compile import (
    CompileContext,
    _run_sphinx,
    _sphinx_command,
    verify_resource_patch,
)


class TestCoreCompile(unittest.TestCase):
    @patch("subprocess.run")
    @patch("qgis_manager.core.compile.get_rcc_tool", return_value="pyside6-rcc")
    def test_compile_qt_resources(self, mock_get_tool, mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            qrc_file = tmp_path / "resources.qrc"
            qrc_file.touch()

            # Execute
            self.assertTrue(compile_qt_resources(tmp_path, res_type="resources"))

            # Verify
            self.assertEqual(mock_run.call_count, 1)
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "pyside6-rcc")
            self.assertEqual(args[-1], str(qrc_file))

    @patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "rcc"),
    )
    @patch("qgis_manager.core.compile.get_rcc_tool", return_value="pyside6-rcc")
    def test_compile_qt_resources_reports_failure(self, _mock_get_tool, _mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "resources.qrc").touch()

            self.assertFalse(compile_qt_resources(tmp_path, res_type="resources"))

    @patch(
        "qgis_manager.core.compile.shutil.which", return_value="/usr/bin/sphinx-build"
    )
    @patch("subprocess.Popen")
    def test_compile_docs(self, mock_popen, _mock_which):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            docs_source = tmp_path / "docs" / "source"
            docs_source.mkdir(parents=True)
            (docs_source / "conf.py").touch()

            mock_process = MagicMock()
            mock_process.stdout = ["line 1", "line 2"]
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            # Execute
            self.assertTrue(compile_docs(tmp_path))

            # Verify
            mock_popen.assert_called_once()
            args = mock_popen.call_args[1].get("args") or mock_popen.call_args[0][0]
            self.assertEqual(args[0], "/usr/bin/sphinx-build")
            self.assertIn("-b", args)
            self.assertTrue((tmp_path / "help" / "html").is_dir())

            # A pyproject.toml must not force `uv run`
            (tmp_path / "pyproject.toml").touch()
            self.assertTrue(compile_docs(tmp_path))
            self.assertEqual(mock_popen.call_count, 2)
            args = mock_popen.call_args[1].get("args") or mock_popen.call_args[0][0]
            self.assertEqual(args[0], "/usr/bin/sphinx-build")
            self.assertNotIn("uv", args)

    @patch(
        "qgis_manager.core.compile.shutil.which", return_value="/usr/bin/sphinx-build"
    )
    @patch("subprocess.Popen")
    def test_compile_docs_with_callback(self, mock_popen, _mock_which):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            docs_source = tmp_path / "docs" / "source"
            docs_source.mkdir(parents=True)
            (docs_source / "conf.py").touch()

            mock_process = MagicMock()
            mock_process.stdout = ["building documents...", "done"]
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            callback_lines = []

            def callback(line):
                callback_lines.append(line)

            # Execute
            self.assertTrue(compile_docs(tmp_path, callback=callback))

            # Verify
            self.assertIn("PROGRESS:building documents...", callback_lines)
            self.assertIn("PROGRESS:done", callback_lines)
            self.assertIn("DONE:Documentation", callback_lines)
            self.assertIn("START:Documentation (html)", callback_lines)

    def test_count_compile_steps(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "resources.qrc").touch()
            (root / "dialog.ui").touch()
            (root / "translations.ts").touch()
            (root / "docs").mkdir()
            (root / "docs" / "source").mkdir()
            (root / "docs" / "source" / "conf.py").touch()

            self.assertEqual(count_compile_steps(root, "all"), 4)
            self.assertEqual(count_compile_steps(root, "resources"), 2)
            self.assertEqual(count_compile_steps(root, "translations"), 1)
            self.assertEqual(count_compile_steps(root, "docs"), 1)

    @patch("qgis_manager.core.compile.get_rcc_tool", return_value=None)
    @patch("subprocess.run")
    def test_compile_qt_resources_no_rcc_tool(self, mock_run, _mock_get_tool):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "resources.qrc").touch()

            self.assertFalse(compile_qt_resources(tmp_path, res_type="resources"))
            mock_run.assert_not_called()

    @patch(
        "qgis_manager.core.compile.shutil.which", return_value="/usr/bin/sphinx-build"
    )
    @patch("subprocess.Popen")
    def test_compile_docs_failure_preserves_previous_output(
        self, mock_popen, _mock_which
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docs_source = tmp_path / "docs" / "source"
            docs_source.mkdir(parents=True)
            (docs_source / "conf.py").touch()
            previous = tmp_path / "help" / "html" / "index.html"
            previous.parent.mkdir(parents=True)
            previous.write_text("previous docs", encoding="utf-8")

            mock_process = MagicMock()
            mock_process.stdout = []
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            self.assertFalse(compile_docs(tmp_path))

            mock_popen.assert_called_once()
            self.assertTrue(previous.exists())
            self.assertEqual(previous.read_text(encoding="utf-8"), "previous docs")

    @patch("qgis_manager.core.compile.importlib.util.find_spec", return_value=None)
    @patch("qgis_manager.core.compile.shutil.which", return_value=None)
    def test_compile_docs_without_sphinx_returns_false(
        self, _mock_which, _mock_find_spec
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docs_source = tmp_path / "docs" / "source"
            docs_source.mkdir(parents=True)
            (docs_source / "conf.py").touch()

            self.assertFalse(compile_docs(tmp_path))

    def test_patch_resource_file_verification_failure(self):
        from qgis_manager.core import patch_resource_file

        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "resources_rc.py"
            py_file.write_text(
                "from PyQt5 import QtCore\n    import resources_rc\n",
                encoding="utf-8",
            )

            result = patch_resource_file(py_file)

            self.assertTrue(result)

    @patch("shutil.which")
    def test_get_uic_tool(self, mock_which):
        mock_which.side_effect = lambda t: t if t == "pyuic5" else None
        self.assertEqual(get_uic_tool(), "pyuic5")

    @patch("shutil.which")
    def test_get_uic_tool_prefers_pyuic6(self, mock_which):
        mock_which.side_effect = lambda t: t if t in ("pyuic6", "pyuic5") else None
        self.assertEqual(get_uic_tool(), "pyuic6")

    def test_patch_ui_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "ui_dialog.py"
            py_file.write_text(
                "from PySide6 import QtCore, QtWidgets\n", encoding="utf-8"
            )
            self.assertTrue(patch_ui_file(py_file))
            self.assertIn(
                "from qgis.PyQt import QtCore, QtWidgets", py_file.read_text()
            )

    def test_patch_ui_file_pyqt6(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "ui_dialog.py"
            py_file.write_text(
                "from PyQt6 import QtCore, QtWidgets\n", encoding="utf-8"
            )
            self.assertTrue(patch_ui_file(py_file))
            content = py_file.read_text(encoding="utf-8")
            self.assertIn("from qgis.PyQt import QtCore, QtWidgets", content)
            self.assertNotIn("PyQt6", content)

    def test_patch_ui_file_no_change(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "ui_dialog.py"
            content = "from qgis.PyQt import QtCore\n"
            py_file.write_text(content, encoding="utf-8")
            self.assertFalse(patch_ui_file(py_file))
            self.assertEqual(py_file.read_text(), content)

    @patch("qgis_manager.core.compile.patch_ui_file")
    @patch("qgis_manager.core.compile.get_uic_tool", return_value="pyuic5")
    @patch("subprocess.run")
    def test_compile_ui_files(self, mock_run, _mock_get_tool, mock_patch):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "dialog.ui").touch()

            compile_ui_files(root)

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "pyuic5")
            self.assertEqual(args[1], "-o")
            self.assertEqual(args[-1], str(root / "dialog.ui"))
            mock_patch.assert_called_once()

    @patch("qgis_manager.core.compile.get_uic_tool", return_value="pyuic5")
    @patch("subprocess.run")
    def test_compile_ui_files_up_to_date(self, mock_run, _mock_get_tool):
        import os
        import time

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            ui = root / "dialog.ui"
            ui.touch()
            py = root / "dialog.py"
            py.write_text("compiled", encoding="utf-8")
            future = time.time() + 100
            os.utime(py, (future, future))

            compile_ui_files(root)

            mock_run.assert_not_called()

    @patch("qgis_manager.core.compile.get_uic_tool", return_value=None)
    def test_compile_ui_files_no_tool(self, _mock_get_tool):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "dialog.ui").touch()

            self.assertFalse(compile_ui_files(root))

    @patch(
        "qgis_manager.core.compile.subprocess.run",
        side_effect=FileNotFoundError(),
    )
    def test_compile_context_missing_tool(self, _mock_run):
        context = CompileContext(Path("."))
        self.assertFalse(context.run(["missing"], "missing"))

    @patch(
        "qgis_manager.core.compile.subprocess.run",
        side_effect=subprocess.TimeoutExpired("tool", 1),
    )
    def test_compile_context_timeout(self, _mock_run):
        context = CompileContext(Path("."))
        self.assertFalse(context.run(["slow"], "slow"))

    @patch(
        "qgis_manager.core.compile.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "tool"),
    )
    def test_compile_context_nonzero(self, _mock_run):
        context = CompileContext(Path("."))
        self.assertFalse(context.run(["tool"], "tool"))

    @patch(
        "qgis_manager.core.compile.importlib.util.find_spec", side_effect=ImportError
    )
    @patch("qgis_manager.core.compile.shutil.which", return_value=None)
    def test_sphinx_command_handles_find_spec_error(self, _which, _find_spec):
        self.assertIsNone(_sphinx_command())

    def test_sphinx_timeout_kills_process(self):
        process = MagicMock()
        process.stdout = []
        process.wait.side_effect = subprocess.TimeoutExpired("sphinx", 1)
        with patch("qgis_manager.core.compile.subprocess.Popen", return_value=process):
            with self.assertRaises(subprocess.TimeoutExpired):
                _run_sphinx(["sphinx-build"], None)
        process.kill.assert_called_once()

    def test_verify_resource_patch_missing_file(self):
        self.assertFalse(verify_resource_patch(Path("/nonexistent/resources.py")))

    def test_patch_ui_file_read_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "dialog.py"
            py_file.write_text("x", encoding="utf-8")
            with patch("pathlib.Path.read_text", side_effect=OSError("denied")):
                self.assertFalse(patch_ui_file(py_file))

    @patch("qgis_manager.core.compile.subprocess.run")
    def test_compile_translations(self, mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "translations.ts").touch()
            self.assertTrue(compile_qt_resources(root, res_type="translations"))
            mock_run.assert_called_once()
            self.assertEqual(mock_run.call_args[0][0][0], "lrelease")

    @patch("qgis_manager.core.compile._compile_qrc_files", return_value=True)
    @patch("qgis_manager.core.compile.compile_ui_files", return_value=False)
    def test_compile_resources_aggregates_failure(self, mock_ui, mock_qrc):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.assertFalse(compile_qt_resources(root, res_type="resources"))
            mock_ui.assert_called_once()
            mock_qrc.assert_called_once()

    def test_compile_all_with_no_sources_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertTrue(compile_qt_resources(Path(tmp_dir), res_type="all"))

    @patch("qgis_manager.core.compile.subprocess.run")
    def test_compile_translations_skips_fresh_qm(self, mock_run):
        import os
        import time

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            ts = root / "translations.ts"
            ts.touch()
            qm = root / "translations.qm"
            qm.write_text("qm", encoding="utf-8")
            future = time.time() + 100
            os.utime(qm, (future, future))

            self.assertTrue(compile_qt_resources(root, res_type="translations"))
            mock_run.assert_not_called()

    @patch("qgis_manager.core.compile.get_rcc_tool", return_value="pyside6-rcc")
    @patch("qgis_manager.core.compile.subprocess.run")
    def test_compile_qrc_does_not_rewrite_identical_output(self, mock_run, _mock_tool):
        def fake_run(command, **_kwargs):
            Path(command[2]).write_text("same", encoding="utf-8")
            return MagicMock()

        mock_run.side_effect = fake_run
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "resources.qrc").touch()
            py_file = root / "resources.py"
            py_file.write_text("same", encoding="utf-8")
            before = py_file.stat().st_mtime_ns

            self.assertTrue(compile_qt_resources(root, res_type="resources"))

            self.assertEqual(py_file.stat().st_mtime_ns, before)
