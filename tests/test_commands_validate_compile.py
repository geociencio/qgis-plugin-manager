import tempfile
from pathlib import Path
from unittest.mock import patch

from .command_test_base import _CommandTestBase


class TestValidateCommand(_CommandTestBase):
    def _make_project(self) -> Path:
        tmp_path = Path(tempfile.mkdtemp())
        (tmp_path / "__init__.py").write_text(
            "def classFactory(iface):\n    pass\n", encoding="utf-8"
        )
        return tmp_path

    def _write_metadata(self, tmp_path: Path, include_recommended: bool = True) -> None:
        fields = [
            "[general]",
            "name=Test Plugin",
            "description=Test description",
            "about=Longer test description",
            "version=1.0.0",
            "qgisMinimumVersion=3.0",
            "author=Tester",
            "email=test@test.com",
        ]
        if include_recommended:
            fields += [
                "homepage=https://example.com",
                "repository=https://example.com",
                "tags=test",
            ]
        (tmp_path / "metadata.txt").write_text(
            "\n".join(fields) + "\n", encoding="utf-8"
        )

    @patch("qgis_manager.cli.base.find_project_root")
    def test_validate_success(self, mock_find):
        root = self._make_project()
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, output, _ = self._invoke(["validate"])
        self.assertEqual(exit_code, 0)
        self.assertIn("passed", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_validate_strict_fails_on_warnings(self, mock_find):
        root = self._make_project()
        self._write_metadata(root, include_recommended=False)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate", "--strict"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_validate_missing_init_py(self, mock_find):
        root = Path(tempfile.mkdtemp())
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_validate_repo_flag(self, mock_find):
        root = self._make_project()
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate", "--repo"])
        self.assertEqual(exit_code, 1)  # no LICENSE file in temp project


class TestCompileCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.compile.compile_qt_resources", return_value=False)
    @patch("qgis_manager.cli.base.find_project_root")
    def test_compile_failure_returns_nonzero(self, mock_find, _mock_compile):
        mock_find.return_value = Path(tempfile.mkdtemp())

        exit_code, _, stderr = self._invoke(["compile", "--type", "resources"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Compilation failed", stderr)

    @patch("qgis_manager.cli.commands.compile.compile_qt_resources", return_value=True)
    @patch("qgis_manager.cli.base.find_project_root")
    def test_compile_repeated_types(self, mock_find, mock_compile):
        mock_find.return_value = Path(tempfile.mkdtemp())

        exit_code, _, _ = self._invoke(
            ["compile", "--type", "resources", "--type", "translations"]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_compile.call_args.args[1], ["resources", "translations"])

    @patch("qgis_manager.cli.base.find_project_root")
    def test_validate_json_output(self, mock_find):
        import json

        root = Path(tempfile.mkdtemp())
        (root / "metadata.txt").write_text(
            "[general]\nname=Demo\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(["validate", "--json"])
        self.assertEqual(exit_code, 1)
        payload = json.loads(output)
        self.assertEqual(payload["schema"], 1)
        self.assertEqual(payload["command"], "validate")
        self.assertFalse(payload["success"])
