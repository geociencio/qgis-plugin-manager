import tempfile
import unittest
from pathlib import Path

from qgis_manager.toml_utils import (
    get_project_version,
    load_toml,
    set_project_version,
)


class TestTomlUtils(unittest.TestCase):
    def _write(self, tmp_path: Path, content: str) -> Path:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(content, encoding="utf-8")
        return pyproject

    def test_load_toml_valid(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(
                Path(tmp_dir), '[project]\nname = "demo"\nversion = "1.0.0"\n'
            )
            data = load_toml(pyproject)
            self.assertEqual(data["project"]["version"], "1.0.0")

    def test_load_toml_missing_file(self):
        self.assertEqual(load_toml(Path("/nonexistent/pyproject.toml")), {})

    def test_load_toml_malformed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(Path(tmp_dir), "not valid toml [[[")
            self.assertEqual(load_toml(pyproject), {})

    def test_get_project_version(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(
                Path(tmp_dir), '[project]\nname = "demo"\nversion = "1.2.3"\n'
            )
            self.assertEqual(get_project_version(pyproject), "1.2.3")

    def test_get_project_version_missing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(Path(tmp_dir), '[project]\nname = "demo"\n')
            self.assertIsNone(get_project_version(pyproject))

    def test_set_project_version_preserves_content(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(
                Path(tmp_dir),
                '[build-system]\nrequires = ["hatchling"]\n\n'
                '[project]\nname = "demo"\nversion = "0.1.0"  # comment\n\n'
                '[tool.qgis-manager]\nqgis_version = 4\n',
            )
            self.assertTrue(set_project_version(pyproject, "0.2.0"))
            content = pyproject.read_text(encoding="utf-8")
            self.assertIn('version = "0.2.0"  # comment', content)
            self.assertIn('[build-system]', content)
            self.assertIn("qgis_version = 4", content)

    def test_set_project_version_missing_file(self):
        self.assertFalse(
            set_project_version(Path("/nonexistent/pyproject.toml"), "1.0.0")
        )

    def test_set_project_version_no_project_section(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(
                Path(tmp_dir), '[tool.qgis-manager]\nqgis_version = 3\n'
            )
            self.assertFalse(set_project_version(pyproject, "1.0.0"))

    def test_set_project_version_no_version_key(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            pyproject = self._write(Path(tmp_dir), '[project]\nname = "demo"\n')
            self.assertFalse(set_project_version(pyproject, "1.0.0"))


if __name__ == "__main__":
    unittest.main()
