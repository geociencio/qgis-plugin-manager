import configparser
import shutil
import tempfile
import unittest
from pathlib import Path

from src.qgis_manager.validation import validate_metadata, validate_project_structure


class TestStructuralValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.metadata_file = self.test_dir / "metadata.txt"
        self.metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Author",
            "email": "author@example.com",
            "icon": "icon.png",
        }
        self.write_metadata()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def write_metadata(self):
        config = configparser.ConfigParser()
        config["general"] = self.metadata
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            config.write(f)

    def test_missing_init_py(self):
        # __init__.py is missing by default in setUp
        result = validate_project_structure(self.test_dir, self.metadata)
        self.assertFalse(result.is_valid)
        self.assertIn("Critical file missing: '__init__.py'", result.errors)

    def test_missing_icon(self):
        (self.test_dir / "__init__.py").write_text(
            "def classFactory(iface): pass", encoding="utf-8"
        )
        # icon.png is missing
        result = validate_project_structure(self.test_dir, self.metadata)
        self.assertTrue(result.is_valid)
        self.assertIn(
            "Recommended file missing: 'icon.png' (standard icon)",
            result.warnings,
        )

    def test_missing_custom_icon(self):
        (self.test_dir / "__init__.py").write_text(
            "def classFactory(iface): pass", encoding="utf-8"
        )
        self.metadata["icon"] = "custom_icon.png"
        # custom_icon.png is missing
        result = validate_project_structure(self.test_dir, self.metadata)
        self.assertFalse(result.is_valid)
        self.assertIn(
            "Specified icon file does not exist: 'custom_icon.png'",
            result.errors,
        )

    def test_illegal_name(self):
        self.metadata["name"] = "Test\nPlugin"
        result = validate_metadata(self.metadata)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("illegal characters" in e for e in result.errors))

    def test_valid_project(self):
        (self.test_dir / "__init__.py").write_text(
            "def classFactory(iface): pass", encoding="utf-8"
        )
        (self.test_dir / "icon.png").touch()
        (self.test_dir / "plugin.py").touch()
        result = validate_project_structure(self.test_dir, self.metadata)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)


if __name__ == "__main__":
    unittest.main()
