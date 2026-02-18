import tempfile
import unittest
from pathlib import Path

from qgis_manager.discovery import get_plugin_metadata, save_plugin_metadata


class TestV061Patch(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_bug1_case_sensitivity(self):
        """Verify that CamelCase keys like qgisMinimumVersion are preserved."""
        metadata_file = self.tmp_path / "metadata.txt"
        content = "[general]\nname=Test Plugin\nversion=1.0\nqgisMinimumVersion=3.0\n"
        metadata_file.write_text(content, encoding="utf-8")

        # Test Read
        meta = get_plugin_metadata(self.tmp_path)
        self.assertIn("qgisMinimumVersion", meta)
        self.assertEqual(meta["qgisMinimumVersion"], "3.0")

        # Test Write
        meta["qgisMinimumVersion"] = "3.22"
        save_plugin_metadata(self.tmp_path, meta)

        new_content = metadata_file.read_text(encoding="utf-8")
        self.assertIn("qgisMinimumVersion=3.22", new_content)
        # Ensure it didn't lowercase it
        self.assertNotIn("qgisminimumversion", new_content)

    def test_bug2_interpolation_percent(self):
        """Verify that % sign doesn't cause ConfigParser to crash."""
        metadata_file = self.tmp_path / "metadata.txt"
        # The % character in changelog used to crash ConfigParser due to interpolation
        content = (
            "[general]\nname=Test\nversion=1.0\n"
            "changelog=Performance improved by 50%\n"
        )
        metadata_file.write_text(content, encoding="utf-8")

        # Test Read (should not crash)
        try:
            meta = get_plugin_metadata(self.tmp_path)
            self.assertEqual(meta["changelog"], "Performance improved by 50%")
        except ValueError as e:
            self.fail(f"get_plugin_metadata crashed with ValueError: {e}")

        # Test Write (should not crash)
        meta["changelog"] = "Now 100% better"
        try:
            save_plugin_metadata(self.tmp_path, meta)
            new_content = metadata_file.read_text(encoding="utf-8")
            self.assertIn("changelog=Now 100% better", new_content)
        except ValueError as e:
            self.fail(f"save_plugin_metadata crashed with ValueError: {e}")

    def test_bug3_save_robustness(self):
        """Verify save_plugin_metadata robustness."""
        meta = {
            "name": "Robust Test",
            "version": "1.1.0",
            "description": "Testing save",
            "slug": "robust_test",  # Should be ignored by save_plugin_metadata
        }

        save_plugin_metadata(self.tmp_path, meta)
        metadata_file = self.tmp_path / "metadata.txt"
        self.assertTrue(metadata_file.exists())

        content = metadata_file.read_text(encoding="utf-8")
        self.assertIn("name=Robust Test", content)
        self.assertIn("version=1.1.0", content)
        self.assertNotIn("slug=", content)


if __name__ == "__main__":
    unittest.main()
