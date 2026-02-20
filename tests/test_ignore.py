import tempfile
import unittest
from pathlib import Path

from qgis_manager.ignore import IgnoreMatcher


class TestIgnoreMatcher(unittest.TestCase):
    def test_default_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            matcher = IgnoreMatcher(tmp_path)

            # Default: __pycache__ should be excluded
            pycache = tmp_path / "__pycache__"
            self.assertTrue(matcher.should_exclude(pycache))

            # Default: tests should be excluded if include_dev=False
            tests = tmp_path / "tests"
            self.assertTrue(matcher.should_exclude(tests))

            # Random file should NOT be excluded
            plugin_py = tmp_path / "plugin.py"
            self.assertFalse(matcher.should_exclude(plugin_py))

    def test_qgisignore_overrides(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            qgisignore = tmp_path / ".qgisignore"
            qgisignore.write_text("secret.txt\ndata/*.log\n", encoding="utf-8")

            matcher = IgnoreMatcher(tmp_path)

            secret = tmp_path / "secret.txt"
            self.assertTrue(matcher.should_exclude(secret))

            # Wildcard in specific folder
            log1 = tmp_path / "data" / "debug.log"
            self.assertTrue(matcher.should_exclude(log1))

            # Log outside data should NOT be excluded (unless pattern is global)
            # Actually our current simple matcher treats patterns globally if no /
            # (In v0.6.0, *.log is recursive by default)

            qgisignore.write_text("my_data/\nfolder/sub/file.py\n", encoding="utf-8")
            matcher = IgnoreMatcher(tmp_path)

            my_data = tmp_path / "my_data" / "config.json"
            self.assertTrue(matcher.should_exclude(my_data))

            specific_file = tmp_path / "folder" / "sub" / "file.py"
            self.assertTrue(matcher.should_exclude(specific_file))

    def test_include_dev(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            matcher = IgnoreMatcher(tmp_path, include_dev=True)

            tests = tmp_path / "tests"
            self.assertFalse(matcher.should_exclude(tests))

            # __pycache__ is still excluded
            pycache = tmp_path / "__pycache__"
            self.assertTrue(matcher.should_exclude(pycache))

    def test_exclusive_qgisignore(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create a .gitignore that ignores 'should_be_included.txt'
            gitignore = tmp_path / ".gitignore"
            gitignore.write_text("should_be_included.txt\n", encoding="utf-8")

            # Create a .qgisignore that ignores 'should_be_excluded.txt'
            qgisignore = tmp_path / ".qgisignore"
            qgisignore.write_text("should_be_excluded.txt\n", encoding="utf-8")

            matcher = IgnoreMatcher(tmp_path)

            # Because .qgisignore exists, .gitignore should be ignored entirely.
            # So 'should_be_included.txt' must NOT be excluded.
            included = tmp_path / "should_be_included.txt"
            self.assertFalse(matcher.should_exclude(included))

            # And 'should_be_excluded.txt' must be excluded.
            self.assertTrue(matcher.should_exclude(tmp_path / "should_be_excluded.txt"))

    def test_implicit_recursion(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            qgisignore = tmp_path / ".qgisignore"
            # Pattern 'logs/debug' without wildcards
            qgisignore.write_text("logs/debug\n", encoding="utf-8")

            matcher = IgnoreMatcher(tmp_path)

            # A deep file inside logs/debug should be excluded
            deep_file = tmp_path / "logs" / "debug" / "nested" / "file.txt"
            self.assertTrue(matcher.should_exclude(deep_file))

            # A directory matching exactly should be excluded
            exact_dir = tmp_path / "logs" / "debug"
            self.assertTrue(matcher.should_exclude(exact_dir))


if __name__ == "__main__":
    unittest.main()
