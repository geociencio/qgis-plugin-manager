import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from qgis_manager.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_cli_help(self):
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Commands:", result.output)
        self.assertIn("deploy", result.output)
        self.assertIn("compile", result.output)
        self.assertIn("clean", result.output)
        self.assertIn("package", result.output)
        self.assertIn("validate", result.output)
        self.assertIn("init", result.output)

    def test_cli_init_success(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                main,
                [
                    "init",
                    "Test Plugin",
                    "--author",
                    "Author",
                    "--email",
                    "email@example.com",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn(
                "Plugin 'Test Plugin' initialized successfully", result.output
            )
            self.assertTrue(Path("test_plugin/metadata.txt").exists())

    def test_cli_validate_no_project(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["validate"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error:", result.output)

    def test_cli_package_no_project(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["package"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Error:", result.output)

    @patch("qgis_manager.cli.compile_qt_resources")
    @patch("qgis_manager.cli.find_project_root")
    def test_cli_compile_docs(self, mock_find_root, mock_compile):
        tmp_path = Path("/tmp/fake_root")
        mock_find_root.return_value = tmp_path

        result = self.runner.invoke(main, ["compile", "--type", "docs"])
        self.assertEqual(result.exit_code, 0)
        # Verify call with ANY for the callback since it's defined
        # inside compile command
        mock_compile.assert_called_once_with(
            tmp_path, "docs", callback=unittest.mock.ANY
        )


if __name__ == "__main__":
    unittest.main()
