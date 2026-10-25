import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qgis_manager.core import (
    deploy_plugin,
    rotate_backups,
    sync_directory,
    uninstall_plugin,
)
from qgis_manager.ignore import IgnoreMatcher


class TestCoreDeploy(unittest.TestCase):
    @patch("qgis_manager.core.deploy.get_plugin_metadata")
    @patch("qgis_manager.core.deploy.sync_directory")
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

    @patch("qgis_manager.core.deploy.get_plugin_metadata")
    @patch("shutil.copytree")
    @patch("qgis_manager.core.deploy.datetime")
    @patch("qgis_manager.core.deploy.sync_directory")
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

    @patch(
        "qgis_manager.core.deploy.get_plugin_metadata",
        return_value={"slug": "test_plugin"},
    )
    @patch("qgis_manager.core.deploy.get_qgis_plugin_dir")
    def test_uninstall_plugin(self, mock_dir, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugin_dir = Path(tmp_dir) / "test_plugin"
            plugin_dir.mkdir()
            (plugin_dir / "file.txt").write_text("x", encoding="utf-8")
            mock_dir.return_value = Path(tmp_dir)

            removed = uninstall_plugin(Path("."))

            self.assertEqual(removed, plugin_dir)
            self.assertFalse(plugin_dir.exists())

    @patch(
        "qgis_manager.core.deploy.get_plugin_metadata",
        return_value={"slug": "test_plugin"},
    )
    @patch("qgis_manager.core.deploy.get_qgis_plugin_dir")
    def test_uninstall_plugin_not_deployed(self, mock_dir, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            mock_dir.return_value = Path(tmp_dir)
            self.assertIsNone(uninstall_plugin(Path(".")))

    @patch("qgis_manager.core.deploy.get_plugin_metadata", return_value={"slug": ""})
    @patch("qgis_manager.core.deploy.get_qgis_plugin_dir")
    def test_uninstall_plugin_rejects_empty_slug(self, mock_dir, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins_dir = Path(tmp_dir)
            other = plugins_dir / "other_plugin"
            other.mkdir()
            (other / "keep.py").write_text("x", encoding="utf-8")
            mock_dir.return_value = plugins_dir

            with self.assertRaises(ValueError):
                uninstall_plugin(Path("."))

            self.assertTrue(other.exists())
            self.assertTrue(plugins_dir.exists())

    @patch("qgis_manager.core.deploy.get_plugin_metadata", return_value={"slug": ""})
    def test_deploy_plugin_rejects_empty_slug(self, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dest_dir = Path(tmp_dir) / "plugins"
            dest_dir.mkdir()
            other = dest_dir / "other_plugin"
            other.mkdir()

            with self.assertRaises(ValueError):
                deploy_plugin(Path("."), dest_dir=dest_dir)

            self.assertTrue(other.exists())
            self.assertEqual(list(dest_dir.iterdir()), [other])

    @patch("qgis_manager.core.deploy.get_plugin_metadata")
    @patch("qgis_manager.core.deploy.sync_directory")
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

    @patch(
        "qgis_manager.core.deploy.get_plugin_metadata",
        return_value={"name": "Test", "slug": "test_plugin"},
    )
    def test_deploy_twice_creates_distinct_backups(self, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "project"
            root.mkdir()
            (root / "plugin.py").write_text("print('x')\n", encoding="utf-8")
            dest = Path(tmp_dir) / "plugins"
            dest.mkdir()
            (dest / "test_plugin").mkdir()
            (dest / "test_plugin" / "old.py").write_text("old\n", encoding="utf-8")

            deploy_plugin(root, dest_dir=dest)
            deploy_plugin(root, dest_dir=dest)

            backups = sorted(dest.glob("test_plugin.bak.*"))
            self.assertGreaterEqual(len(backups), 2)
            self.assertTrue((dest / "test_plugin" / "plugin.py").exists())
