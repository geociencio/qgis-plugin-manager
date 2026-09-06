import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from qgis_manager.core import (
    clean_artifacts,
    compile_docs,
    compile_qt_resources,
    compile_ui_files,
    count_compile_steps,
    create_plugin_package,
    deploy_plugin,
    get_git_info,
    get_qgis_plugin_dir,
    get_uic_tool,
    init_plugin_project,
    is_prerelease,
    patch_ui_file,
    rotate_backups,
    stamp_metadata_text,
    sync_directory,
)
from qgis_manager.ignore import IgnoreMatcher


class TestCore(unittest.TestCase):
    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux(self):
        expected_v3 = (
            Path.home() / ".local/share/QGIS/QGIS3/profiles/default/python/plugins"
        )
        expected_v4 = (
            Path.home() / ".local/share/QGIS/QGIS4/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux_custom_profile(self):
        expected = Path.home() / ".local/share/QGIS/QGIS3/profiles/prod/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="prod", version=3), expected)

    @patch("sys.platform", "darwin")
    def test_get_qgis_plugin_dir_darwin(self):
        expected_v3 = (
            Path.home()
            / "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
        )
        expected_v4 = (
            Path.home()
            / "Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32(self):
        expected_v3 = Path("/appdata") / "QGIS/QGIS3/profiles/default/python/plugins"
        expected_v4 = Path("/appdata") / "QGIS/QGIS4/profiles/default/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32_custom(self):
        expected = Path("/appdata") / "QGIS/QGIS3/profiles/test/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="test", version=3), expected)

    @patch("sys.platform", "unknown")
    def test_get_qgis_plugin_dir_unsupported(self):
        with self.assertRaisesRegex(OSError, "Unsupported platform"):
            get_qgis_plugin_dir()

    @patch("qgis_manager.core.get_plugin_metadata")
    @patch("qgis_manager.core.sync_directory")
    def test_deploy_plugin(self, mock_sync, mock_get_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir)

            # Verify
            target_path = dest_dir / "test_plugin"
            self.assertTrue(target_path.exists())
            mock_sync.assert_called_once()

    @patch("qgis_manager.core.get_plugin_metadata")
    @patch("shutil.copytree")
    @patch("qgis_manager.core.datetime")
    @patch("qgis_manager.core.sync_directory")
    def test_deploy_plugin_with_backup(
        self, mock_sync, mock_datetime, mock_copytree, mock_get_meta
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata

            mock_datetime.now.return_value.strftime.return_value = "20230101"

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()
            (dest_dir / "test_plugin").mkdir()  # simulate existing

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir)

            # Verify backup was created
            mock_copytree.assert_called()

    @patch("subprocess.run")
    @patch("qgis_manager.core.get_rcc_tool", return_value="pyside6-rcc")
    def test_compile_qt_resources(self, mock_get_tool, mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            qrc_file = tmp_path / "resources.qrc"
            qrc_file.touch()

            # Execute
            compile_qt_resources(tmp_path, res_type="resources")

            # Verify
            self.assertEqual(mock_run.call_count, 1)
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "pyside6-rcc")
            self.assertEqual(args[-1], str(qrc_file))

    def test_clean_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            pycache = tmp_path / "__pycache__"
            pycache.mkdir()
            pyc_file = tmp_path / "file.pyc"
            pyc_file.touch()

            # Execute
            clean_artifacts(tmp_path)

            # Verify
            self.assertFalse(pycache.exists())
            self.assertFalse(pyc_file.exists())

    def test_init_plugin_project(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            plugin_name = "My New Plugin"
            author = "John Doe"
            email = "john@example.com"
            description = "Cool description"

            # Execute
            init_plugin_project(tmp_path, plugin_name, author, email, description)

            # Verify directory
            plugin_dir = tmp_path / "my_new_plugin"
            self.assertTrue(plugin_dir.exists())
            self.assertTrue(plugin_dir.is_dir())

            # Verify metadata.txt
            metadata_file = plugin_dir / "metadata.txt"
            self.assertTrue(metadata_file.exists())
            content = metadata_file.read_text()
            self.assertIn("name=My New Plugin", content)
            self.assertIn("author=John Doe", content)
            self.assertIn("email=john@example.com", content)
            self.assertIn("description=Cool description", content)

    @patch("qgis_manager.core.get_plugin_metadata")
    @patch("qgis_manager.core.sync_directory")
    def test_deploy_plugin_with_callback(self, mock_sync, mock_get_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()

            callback_calls = []

            def callback(n):
                callback_calls.append(n)

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir, callback=callback)

            # Verify
            self.assertEqual(callback_calls, [100])

    @patch("subprocess.Popen")
    def test_compile_docs(self, mock_popen):
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
            compile_docs(tmp_path)

            # Verify
            mock_popen.assert_called_once()
            args = mock_popen.call_args[1].get("args") or mock_popen.call_args[0][0]
            self.assertIn("sphinx-build", args)

            # Test with uv run
            (tmp_path / "pyproject.toml").touch()
            compile_docs(tmp_path)
            self.assertEqual(mock_popen.call_count, 2)
            args = mock_popen.call_args[1].get("args") or mock_popen.call_args[0][0]
            self.assertEqual(args[0], "uv")
            self.assertEqual(args[1], "run")
            self.assertEqual(args[2], "sphinx-build")

    @patch("subprocess.Popen")
    def test_compile_docs_with_callback(self, mock_popen):
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
            compile_docs(tmp_path, callback=callback)

            # Verify
            self.assertIn("PROGRESS:building documents...", callback_lines)
            self.assertIn("PROGRESS:done", callback_lines)
            self.assertIn("DONE:Documentation", callback_lines)
            self.assertIn("START:Documentation (html)", callback_lines)

    def test_create_plugin_package(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("print('hello')\n", encoding="utf-8")

            output = tmp_path / "out"
            zip_path = create_plugin_package(tmp_path, output_dir=output)

            self.assertTrue(zip_path.exists())
            self.assertTrue(zip_path.name.endswith(".zip"))
            # SHA256 checksum file
            checksum_file = Path(str(zip_path) + ".sha256")
            self.assertTrue(checksum_file.exists())
            # ZIP contains the plugin files under slug/
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
            self.assertTrue(any(n.endswith("plugin.py") for n in names))
            self.assertTrue(any(n.endswith("metadata.txt") for n in names))

    def test_sync_directory_skips_self_recursion(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            src = Path(tmp_dir) / "src"
            src.mkdir()
            (src / "file.txt").write_text("data", encoding="utf-8")
            # Destination inside source
            dst = src / "nested" / "dst"
            matcher = IgnoreMatcher(src)

            sync_directory(src, dst, matcher)

            # The nested dst should not have received a copy of itself
            self.assertFalse((dst / "nested").exists())

    def test_rotate_backups_no_limit(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            parent = Path(tmp_dir)
            (parent / "plugin.bak.1").mkdir()
            rotate_backups(parent, "plugin", 0)
            self.assertTrue((parent / "plugin.bak.1").exists())

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

    def test_create_plugin_package_callback(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("print('hello')\n", encoding="utf-8")

            calls = []
            create_plugin_package(tmp_path, callback=lambda n: calls.append(n))

            self.assertGreater(len(calls), 0)

    def test_create_plugin_package_include_dev(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "docs").mkdir()
            (tmp_path / "docs" / "readme.md").write_text("docs", encoding="utf-8")

            output = tmp_path / "out"
            zip_path = create_plugin_package(
                tmp_path, output_dir=output, include_dev=True
            )
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
            self.assertTrue(any("docs" in n for n in names))

    @patch("qgis_manager.core.get_rcc_tool", return_value=None)
    @patch("subprocess.run")
    def test_compile_qt_resources_no_rcc_tool(self, mock_run, _mock_get_tool):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "resources.qrc").touch()

            compile_qt_resources(tmp_path, res_type="resources")

            mock_run.assert_not_called()

    @patch("subprocess.Popen")
    def test_compile_docs_failure(self, mock_popen):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            docs_source = tmp_path / "docs" / "source"
            docs_source.mkdir(parents=True)
            (docs_source / "conf.py").touch()

            mock_process = MagicMock()
            mock_process.stdout = []
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            compile_docs(tmp_path)

            mock_popen.assert_called_once()

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

    def test_patch_ui_file_no_change(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            py_file = Path(tmp_dir) / "ui_dialog.py"
            content = "from qgis.PyQt import QtCore\n"
            py_file.write_text(content, encoding="utf-8")
            self.assertFalse(patch_ui_file(py_file))
            self.assertEqual(py_file.read_text(), content)

    @patch("qgis_manager.core.patch_ui_file")
    @patch("qgis_manager.core.get_uic_tool", return_value="pyuic5")
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

    @patch("qgis_manager.core.get_uic_tool", return_value="pyuic5")
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

    @patch("qgis_manager.core.get_uic_tool", return_value=None)
    def test_compile_ui_files_no_tool(self, _mock_get_tool):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "dialog.ui").touch()

            compile_ui_files(root)

    def test_is_prerelease(self):
        self.assertTrue(is_prerelease("1.0.0-rc1"))
        self.assertTrue(is_prerelease("1.0.0-beta2"))
        self.assertTrue(is_prerelease("1.0.0-alpha"))
        self.assertTrue(is_prerelease("1.0.0.dev0"))
        self.assertFalse(is_prerelease("1.0.0"))
        self.assertFalse(is_prerelease("2.3.4"))

    def test_stamp_metadata_text_updates_and_appends(self):
        text = "; comment\n[general]\nname=My Plugin\nversion=1.0.0\n"
        result = stamp_metadata_text(
            text,
            version="2.0.0",
            commit_sha="abc123",
            commit_number=42,
            timestamp="2026-01-01T00:00:00Z",
            experimental=False,
        )
        self.assertIn("version=2.0.0", result)
        self.assertIn("commitSha1=abc123", result)
        self.assertIn("commitNumber=42", result)
        self.assertIn("dateTime=2026-01-01T00:00:00Z", result)
        self.assertIn("experimental=False", result)
        self.assertIn("; comment", result)
        self.assertIn("name=My Plugin", result)

    def test_stamp_metadata_text_appends_before_next_section(self):
        text = "[general]\nname=X\nversion=1.0.0\n\n[tags]\nfoo=bar\n"
        result = stamp_metadata_text(text, commit_sha="abc")
        self.assertLess(result.index("version=1.0.0"), result.index("commitSha1=abc"))
        self.assertLess(result.index("commitSha1=abc"), result.index("[tags]"))

    def test_stamp_metadata_text_no_updates(self):
        text = "[general]\nname=X\n"
        self.assertEqual(stamp_metadata_text(text), text)

    @patch("qgis_manager.core.subprocess.run")
    def test_get_git_info(self, mock_run):
        mock_run.side_effect = [Mock(stdout="abc123\n"), Mock(stdout="42\n")]
        self.assertEqual(get_git_info(Path(".")), ("abc123", 42))

    @patch("qgis_manager.core.subprocess.run", side_effect=FileNotFoundError)
    def test_get_git_info_not_a_repo(self, _mock_run):
        self.assertEqual(get_git_info(Path(".")), (None, None))

    @patch("qgis_manager.core.get_git_info", return_value=("abc123", 10))
    def test_create_plugin_package_stamp(self, _mock_git):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("x=1\n", encoding="utf-8")

            zip_path = create_plugin_package(
                tmp_path, output_dir=tmp_path / "out", stamp=True
            )

            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                metadata_name = next(n for n in names if n.endswith("metadata.txt"))
                content = zf.read(metadata_name).decode("utf-8")

            self.assertIn("commitSha1=abc123", content)
            self.assertIn("commitNumber=10", content)
            self.assertIn("dateTime=", content)
            self.assertIn("experimental=False", content)
            self.assertIn("version=1.0.0", content)
            # Source metadata.txt must not be modified
            self.assertNotIn(
                "commitSha1", (tmp_path / "metadata.txt").read_text()
            )


if __name__ == "__main__":
    unittest.main()
