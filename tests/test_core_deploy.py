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
from qgis_manager.core.deploy import _backup_path, _is_same_or_nested
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

    @patch("qgis_manager.core.deploy.get_plugin_metadata")
    @patch("qgis_manager.core.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.core.deploy.sync_directory")
    def test_deploy_uses_detected_plugins_dir(
        self, mock_sync, mock_plugins_dir, mock_meta
    ):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "project"
            root.mkdir()
            dest = Path(tmp_dir) / "plugins"
            dest.mkdir()
            mock_meta.return_value = {"name": "Test", "slug": "test_plugin"}
            mock_plugins_dir.return_value = dest

            deploy_plugin(root, no_backup=True)

            mock_plugins_dir.assert_called_once()
            mock_sync.assert_called_once()

    @patch(
        "qgis_manager.core.deploy.get_plugin_metadata",
        return_value={"name": "Test", "slug": "test_plugin"},
    )
    def test_deploy_rejects_symlink_target(self, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "project"
            root.mkdir()
            dest = Path(tmp_dir) / "plugins"
            dest.mkdir()
            real = Path(tmp_dir) / "real"
            real.mkdir()
            try:
                (dest / "test_plugin").symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")

            with self.assertRaises(ValueError):
                deploy_plugin(root, dest_dir=dest)

    def test_backup_path_collision_adds_suffix(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            parent = Path(tmp_dir)
            (parent / "plugin.bak.stamp").mkdir()
            with patch("qgis_manager.core.deploy.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "stamp"
                path = _backup_path(parent, "plugin")
            self.assertEqual(path.name, "plugin.bak.stamp-1")

    def test_is_same_or_nested_returns_false_on_resolve_error(self):
        with patch("pathlib.Path.resolve", side_effect=OSError("bad path")):
            self.assertFalse(_is_same_or_nested(Path("a"), Path("b")))

    def test_sync_skips_source_symlink(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            src = root / "src"
            dst = root / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "real.txt").write_text("ok", encoding="utf-8")
            target = root / "outside.txt"
            target.write_text("outside", encoding="utf-8")
            try:
                (src / "link.txt").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")

            sync_directory(src, dst, IgnoreMatcher(src))

            self.assertTrue((dst / "real.txt").exists())
            self.assertFalse((dst / "link.txt").exists())

    def test_sync_removes_destination_symlink_and_stale_entries(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            src = root / "src"
            dst = root / "dst"
            src.mkdir()
            dst.mkdir()
            (src / "keep.txt").write_text("keep", encoding="utf-8")
            (dst / "keep.txt").write_text("old", encoding="utf-8")
            (dst / "stale.txt").write_text("stale", encoding="utf-8")
            (dst / "stale_dir").mkdir()
            target = root / "outside.txt"
            target.write_text("outside", encoding="utf-8")
            try:
                (dst / "link.txt").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")

            sync_directory(src, dst, IgnoreMatcher(src))

            self.assertTrue((dst / "keep.txt").exists())
            self.assertFalse((dst / "stale.txt").exists())
            self.assertFalse((dst / "stale_dir").exists())
            self.assertFalse((dst / "link.txt").exists())

    @patch(
        "qgis_manager.core.deploy.get_plugin_metadata",
        return_value={"slug": "test_plugin"},
    )
    def test_uninstall_plugin_symlink(self, _mock_meta):
        with tempfile.TemporaryDirectory() as tmp_dir:
            plugins = Path(tmp_dir) / "plugins"
            plugins.mkdir()
            real = Path(tmp_dir) / "real"
            real.mkdir()
            link = plugins / "test_plugin"
            try:
                link.symlink_to(real, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with patch(
                "qgis_manager.core.deploy.get_qgis_plugin_dir",
                return_value=plugins,
            ):
                removed = uninstall_plugin(Path("."))
            self.assertEqual(removed, link)
            self.assertFalse(link.exists())
            self.assertTrue(real.exists())
