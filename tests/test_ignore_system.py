import unittest
from pathlib import Path

from src.qgis_manager.ignore import IgnoreMatcher, load_ignore_patterns


class TestIgnoreSystem(unittest.TestCase):
    def setUp(self):
        self.test_root = Path("test_project_temp")
        self.test_root.mkdir(exist_ok=True)
        (self.test_root / "metadata.txt").write_text("name=Test Plugin")
        (self.test_root / ".gitignore").write_text("*.tmp\n/secret/")

    def tearDown(self):
        import shutil

        if self.test_root.exists():
            shutil.rmtree(self.test_root)

    def test_gitignore_patterns(self):
        spec = load_ignore_patterns(self.test_root)
        matcher = IgnoreMatcher(self.test_root, spec)

        # Should ignore by extension
        self.assertTrue(matcher.should_exclude(self.test_root / "test.tmp"))
        self.assertFalse(matcher.should_exclude(self.test_root / "test.py"))

        # Should ignore directory (must exist for is_dir() to work in IgnoreMatcher)
        secret_dir = self.test_root / "secret"
        secret_dir.mkdir(exist_ok=True)
        self.assertTrue(matcher.should_exclude(secret_dir / "data.txt"))
        self.assertTrue(matcher.should_exclude(secret_dir))

    def test_pyproject_patterns(self):
        # pyproject.toml expects tool.qgis-manager.ignore as a list of strings
        pyproject_content = """
[tool.qgis-manager]
ignore = ["*.ignored_by_tool", "custom_dir/"]
"""
        (self.test_root / "pyproject.toml").write_bytes(pyproject_content.encode())

        spec = load_ignore_patterns(self.test_root)
        matcher = IgnoreMatcher(self.test_root, spec)

        # Files
        self.assertTrue(matcher.should_exclude(self.test_root / "test.ignored_by_tool"))

        # Directories
        custom_dir = self.test_root / "custom_dir"
        custom_dir.mkdir(exist_ok=True)
        self.assertTrue(matcher.should_exclude(custom_dir / "anything.py"))
        self.assertTrue(matcher.should_exclude(custom_dir))


if __name__ == "__main__":
    unittest.main()
