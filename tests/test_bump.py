import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qgis_manager.cli.app import CLIApp


class TestBumpCommand(unittest.TestCase):
    def setUp(self):
        self.app = CLIApp()

    def _invoke(self, args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exit_code = self.app.run(args)
            except SystemExit as e:
                exit_code = e.code
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def _make_project(self, version: str) -> Path:
        tmp_path = Path(tempfile.mkdtemp())
        (tmp_path / "pyproject.toml").write_text(
            f'[project]\nname = "demo"\nversion = "{version}"\n', encoding="utf-8"
        )
        (tmp_path / "metadata.txt").write_text(
            f"[general]\nname = demo\nversion = {version}\n", encoding="utf-8"
        )
        return tmp_path

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_patch(self, mock_find):
        root = self._make_project("1.2.3")
        mock_find.return_value = root

        exit_code, output, _ = self._invoke(["bump", "patch"])

        self.assertEqual(exit_code, 0)
        self.assertIn('version = "1.2.4"', (root / "pyproject.toml").read_text())
        self.assertIn("version=1.2.4", (root / "metadata.txt").read_text())
        self.assertIn("1.2.3 -> 1.2.4", output)

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_minor(self, mock_find):
        root = self._make_project("1.2.3")
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["bump", "minor"])

        self.assertEqual(exit_code, 0)
        self.assertIn('version = "1.3.0"', (root / "pyproject.toml").read_text())

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_major(self, mock_find):
        root = self._make_project("1.2.3")
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["bump", "major"])

        self.assertEqual(exit_code, 0)
        self.assertIn('version = "2.0.0"', (root / "pyproject.toml").read_text())

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_sync(self, mock_find):
        root = self._make_project("1.2.3")
        mock_find.return_value = root
        (root / "metadata.txt").write_text(
            "[general]\nname = demo\nversion = 0.9.0\n", encoding="utf-8"
        )

        exit_code, _, _ = self._invoke(["bump", "sync"])

        self.assertEqual(exit_code, 0)
        self.assertIn("version=1.2.3", (root / "metadata.txt").read_text())

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_no_subcommand(self, mock_find):
        root = self._make_project("1.2.3")
        mock_find.return_value = root

        exit_code, output, _ = self._invoke(["bump"])

        self.assertEqual(exit_code, 1)
        self.assertIn("No subcommand", output)

    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_invalid_version(self, mock_find):
        root = self._make_project("not.a.version")
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["bump", "patch"])

        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.commands.bump.save_plugin_metadata")
    @patch("qgis_manager.cli.commands.bump.find_project_root")
    def test_bump_metadata_update_failure(self, mock_find, mock_save):
        root = self._make_project("1.2.3")
        mock_find.return_value = root
        mock_save.side_effect = OSError("permission denied")

        exit_code, _, _ = self._invoke(["bump", "patch"])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
