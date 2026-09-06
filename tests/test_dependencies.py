import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.dependencies import get_dependencies, install_external_libs


class TestDependencies(unittest.TestCase):
    def test_get_dependencies_no_pyproject(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertEqual(get_dependencies(Path(tmp_dir)), [])

    def test_get_dependencies_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "demo"\n', encoding="utf-8"
            )
            self.assertEqual(get_dependencies(tmp_path), [])

    def test_get_dependencies_list(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[tool.qgis-manager]\ndependencies = ["requests", "numpy"]\n',
                encoding="utf-8",
            )
            self.assertEqual(get_dependencies(tmp_path), ["requests", "numpy"])

    def test_get_dependencies_malformed(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text("[[[ not toml", encoding="utf-8")
            self.assertEqual(get_dependencies(tmp_path), [])

    @patch("qgis_manager.dependencies.subprocess.run")
    def test_install_external_libs_no_dependencies(self, mock_run):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[project]\nname = "demo"\n', encoding="utf-8"
            )
            self.assertTrue(install_external_libs(tmp_path))
            mock_run.assert_not_called()

    @patch("qgis_manager.dependencies.subprocess.run")
    def test_install_external_libs_uv(self, mock_run):
        mock_run.return_value.returncode = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[tool.qgis-manager]\ndependencies = ["requests"]\n', encoding="utf-8"
            )
            self.assertTrue(install_external_libs(tmp_path))
            self.assertEqual(mock_run.call_count, 2)

    @patch("qgis_manager.dependencies.subprocess.run")
    def test_install_external_libs_fallback_to_pip(self, mock_run):
        mock_result = Mock(returncode=0)
        mock_run.side_effect = [FileNotFoundError(), mock_result]
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[tool.qgis-manager]\ndependencies = ["requests"]\n', encoding="utf-8"
            )
            self.assertTrue(install_external_libs(tmp_path))
            pip_cmd = mock_run.call_args_list[1][0][0]
            self.assertIn("-m", pip_cmd)

    @patch("qgis_manager.dependencies.subprocess.run")
    def test_install_external_libs_failure(self, mock_run):
        mock_result = Mock(returncode=1)
        mock_run.side_effect = [Mock(), mock_result]
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "pyproject.toml").write_text(
                '[tool.qgis-manager]\ndependencies = ["requests"]\n', encoding="utf-8"
            )
            self.assertFalse(install_external_libs(tmp_path))


if __name__ == "__main__":
    unittest.main()
