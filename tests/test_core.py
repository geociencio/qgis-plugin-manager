import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from qgis_manager.core import (
    clean_artifacts,
    compile_docs,
    compile_qt_resources,
    deploy_plugin,
    get_qgis_plugin_dir,
    init_plugin_project,
)


class TestCore(unittest.TestCase):
    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux(self):
        expected = (
            Path.home() / ".local/share/QGIS/QGIS3/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(), expected)

    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux_custom_profile(self):
        expected = Path.home() / ".local/share/QGIS/QGIS3/profiles/prod/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="prod"), expected)

    @patch("sys.platform", "darwin")
    def test_get_qgis_plugin_dir_darwin(self):
        expected = (
            Path.home()
            / "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(), expected)

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32(self):
        expected = Path("/appdata") / "QGIS/QGIS3/profiles/default/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(), expected)

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32_custom(self):
        expected = Path("/appdata") / "QGIS/QGIS3/profiles/test/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="test"), expected)

    @patch("sys.platform", "unknown")
    def test_get_qgis_plugin_dir_unsupported(self):
        with self.assertRaisesRegex(OSError, "Unsupported platform"):
            get_qgis_plugin_dir()

    @patch("qgis_manager.core.get_plugin_metadata")
    @patch("qgis_manager.core.get_source_files")
    @patch("shutil.copy2")
    @patch("shutil.rmtree")
    def test_deploy_plugin(
        self, mock_rmtree, mock_copy2, mock_get_source, mock_get_meta
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata

            mock_source_file = MagicMock(spec=Path)
            mock_source_file.name = "source.py"
            mock_source_file.is_dir.return_value = False
            mock_get_source.return_value = [mock_source_file]

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir)

            # Verify
            target_path = dest_dir / "test_plugin"
            self.assertTrue(target_path.exists())
            mock_copy2.assert_called()

    @patch("qgis_manager.core.get_plugin_metadata")
    @patch("qgis_manager.core.get_source_files")
    @patch("shutil.copytree")
    @patch("qgis_manager.core.datetime")
    def test_deploy_plugin_with_backup(
        self, mock_datetime, mock_copytree, mock_get_source, mock_get_meta
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata
            mock_get_source.return_value = []

            mock_datetime.now.return_value.strftime.return_value = "20230101"

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()
            (dest_dir / "test_plugin").mkdir()  # simulate existing

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir)

            # Verify backup was created
            mock_copytree.assert_called()

    @patch("subprocess.run")
    def test_compile_qt_resources(self, mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            qrc_file = tmp_path / "resources.qrc"
            qrc_file.touch()

            # Execute
            compile_qt_resources(tmp_path, res_type="resources")

            # Verify
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            self.assertEqual(args[0], "pyrcc5")
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
    @patch("qgis_manager.core.get_source_files")
    @patch("shutil.copy2")
    @patch("shutil.rmtree")
    def test_deploy_plugin_with_callback(
        self, mock_rmtree, mock_copy2, mock_get_source, mock_get_meta
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Mocks
            mock_metadata = {"name": "Test Plugin", "slug": "test_plugin"}
            mock_get_meta.return_value = mock_metadata

            def mock_gen(_):
                file1 = MagicMock(spec=Path)
                file1.name = "f1.py"
                file1.is_dir.return_value = False
                yield file1

            mock_get_source.side_effect = mock_gen

            dest_dir = tmp_path / "plugins"
            dest_dir.mkdir()

            callback_calls = []
            def callback(n):
                callback_calls.append(n)

            # Execute
            deploy_plugin(tmp_path, dest_dir=dest_dir, callback=callback)

            # Verify
            self.assertEqual(callback_calls, [1, 1])

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
            args = mock_popen.call_args[1].get('args') or mock_popen.call_args[0][0]
            self.assertIn("sphinx-build", args)

            # Test with uv run
            (tmp_path / "pyproject.toml").touch()
            compile_docs(tmp_path)
            self.assertEqual(mock_popen.call_count, 2)
            args = mock_popen.call_args[1].get('args') or mock_popen.call_args[0][0]
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
            self.assertIn("DONE:Documentación", callback_lines)
            self.assertIn("START:Documentación (html)", callback_lines)


if __name__ == "__main__":
    unittest.main()
