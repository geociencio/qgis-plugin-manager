import tempfile
import unittest
from pathlib import Path

from qgis_manager.discovery import (
    find_project_root,
    get_plugin_metadata,
    save_plugin_metadata,
    slugify,
    sync_metadata_version,
)


class TestDiscovery(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(slugify("My Plugin"), "my_plugin")
        self.assertEqual(slugify("Plugin  With   Spaces"), "plugin_with_spaces")
        self.assertEqual(slugify("Plugin@#$"), "plugin")
        self.assertEqual(slugify("Café Plugin"), "café_plugin")

    def test_find_project_root_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").touch()
            root = find_project_root(tmp_path)
            self.assertEqual(root, tmp_path)

    def test_find_project_root_nested(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").touch()
            nested = tmp_path / "src" / "subfolder"
            nested.mkdir(parents=True)
            root = find_project_root(nested)
            self.assertEqual(root, tmp_path)

    def test_find_project_root_failure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            with self.assertRaises(FileNotFoundError):
                find_project_root(tmp_path)

    def test_get_plugin_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            metadata_file = tmp_path / "metadata.txt"
            metadata_file.write_text(
                "[general]\nname = Test Plugin\nversion = 1.0", encoding="utf-8"
            )

            meta = get_plugin_metadata(tmp_path)
            self.assertEqual(meta["name"], "Test Plugin")
            self.assertEqual(meta["slug"], "test_plugin")
            self.assertEqual(meta["version"], "1.0")

    def test_get_source_files(self):
        from qgis_manager.discovery import get_source_files

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup structure
            (tmp_path / "plugin.py").touch()
            (tmp_path / "metadata.txt").touch()
            (tmp_path / "resources.qrc").touch()

            files = get_source_files(tmp_path)
            basenames = [f.name for f in files]

            self.assertIn("plugin.py", basenames)
            self.assertIn("metadata.txt", basenames)
            self.assertIn("resources.qrc", basenames)

    def test_sync_metadata_version_updates(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8"
            )
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname = demo\nversion = 1.0.0\n", encoding="utf-8"
            )

            self.assertTrue(sync_metadata_version(tmp_path))
            metadata = get_plugin_metadata(tmp_path)
            self.assertEqual(metadata["version"], "1.2.3")

    def test_sync_metadata_version_already_in_sync(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "demo"\nversion = "1.2.3"\n', encoding="utf-8"
            )
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname = demo\nversion = 1.2.3\n", encoding="utf-8"
            )

            self.assertFalse(sync_metadata_version(tmp_path))

    def test_sync_metadata_version_no_version(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "demo"\n', encoding="utf-8"
            )
            self.assertFalse(sync_metadata_version(tmp_path))

    def test_save_plugin_metadata_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname = demo\n", encoding="utf-8"
            )

            metadata = get_plugin_metadata(tmp_path)
            metadata["version"] = "2.0.0"
            metadata["slug"] = "should_not_persist"
            save_plugin_metadata(tmp_path, metadata)

            content = (tmp_path / "metadata.txt").read_text(encoding="utf-8")
            self.assertIn("version=2.0.0", content)
            self.assertNotIn("slug", content)


if __name__ == "__main__":
    unittest.main()
