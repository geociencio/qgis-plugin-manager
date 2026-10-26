import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from qgis_manager.cli.app import CLIApp


class TestCLI(unittest.TestCase):
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

    def test_cli_help(self):
        exit_code, output, _ = self._invoke(["--help"])
        self.assertEqual(exit_code, 0)
        self.assertIn("usage:", output.lower())
        self.assertIn("deploy", output)
        self.assertIn("compile", output)
        self.assertIn("clean", output)
        self.assertIn("package", output)
        self.assertIn("validate", output)
        self.assertIn("init", output)

    def test_cli_init_success(self):
        with patch("qgis_manager.cli.commands.init.init_plugin_project") as mock_init:
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = True
                exit_code, output, _ = self._invoke(
                    [
                        "init",
                        "Test Plugin",
                        "--author",
                        "Author",
                        "--email",
                        "email@example.com",
                    ]
                )
                self.assertEqual(exit_code, 0)
                self.assertIn("Plugin 'Test Plugin' initialized successfully", output)
                mock_init.assert_called_once()

    def test_cli_package_no_project(self):
        with patch("qgis_manager.cli.base.find_project_root") as mock_find:
            mock_find.side_effect = FileNotFoundError("No project found")
            exit_code, output, error = self._invoke(["package"])
            self.assertEqual(exit_code, 1)
            self.assertIn("Error:", output + error)

    def test_cli_validate_no_project(self):
        with patch("qgis_manager.cli.base.find_project_root") as mock_find:
            mock_find.side_effect = FileNotFoundError("No project found")
            exit_code, output, error = self._invoke(["validate"])
            self.assertEqual(exit_code, 1)
            self.assertIn("Error:", output + error)

    @patch("qgis_manager.cli.commands.compile.compile_qt_resources")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_cli_compile_docs(self, mock_find_root, mock_compile):
        tmp_path = Path("/tmp/fake_root")
        mock_find_root.return_value = tmp_path

        exit_code, output, _ = self._invoke(["compile", "--type", "docs"])
        self.assertEqual(exit_code, 0)
        mock_compile.assert_called_once_with(
            tmp_path, "docs", callback=unittest.mock.ANY, jobs=1
        )

    def test_cli_no_command(self):
        exit_code, output, _ = self._invoke([])
        self.assertEqual(exit_code, 0)
        self.assertIn("usage:", output.lower())

    @patch("qgis_manager.cli.commands.deploy.DeployCommand.execute")
    def test_cli_keyboard_interrupt(self, mock_exec):
        mock_exec.side_effect = KeyboardInterrupt
        exit_code, _, _ = self._invoke(["deploy"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.commands.deploy.DeployCommand.execute")
    def test_cli_generic_exception(self, mock_exec):
        mock_exec.side_effect = RuntimeError("boom")
        exit_code, _, error = self._invoke(["deploy"])
        self.assertEqual(exit_code, 1)
        self.assertIn("boom", error)

    def test_external_command_entry_point(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        from qgis_manager.cli.base import BaseCommand
        from qgis_manager.cli.registry import build_commands

        class ExternalCommand(BaseCommand):
            @property
            def name(self):
                return "external"

            @property
            def help(self):
                return "External command"

            def configure_parser(self, parser):
                pass

            def execute(self, args):
                return 0

        entry = SimpleNamespace(name="external", load=lambda: ExternalCommand)
        with patch("qgis_manager.cli.registry.entry_points", return_value=[entry]):
            classes = build_commands()
        self.assertTrue(
            any(isinstance(command, ExternalCommand) for command in classes)
        )

    def test_duplicate_external_command_is_rejected(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        from qgis_manager.cli.commands.deploy import DeployCommand
        from qgis_manager.cli.registry import build_commands

        entry = SimpleNamespace(name="duplicate", load=lambda: DeployCommand)
        with patch("qgis_manager.cli.registry.entry_points", return_value=[entry]):
            with self.assertRaises(ValueError):
                build_commands()

    def test_command_registry_is_complete_and_unique(self):
        from qgis_manager.cli.base import BaseCommand
        from qgis_manager.cli.registry import COMMAND_CLASSES

        names = [command().name for command in COMMAND_CLASSES]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(
            all(issubclass(command, BaseCommand) for command in COMMAND_CLASSES)
        )

    @patch("qgis_manager.cli.commands.deploy.DeployCommand.__init__", return_value=None)
    def test_commands_are_instantiated_once(self, mock_init):
        CLIApp()
        self.assertEqual(mock_init.call_count, 1)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_cli_verbose(self, mock_find):
        mock_find.side_effect = FileNotFoundError("No project found")
        exit_code, _, _ = self._invoke(["--verbose", "deploy"])
        self.assertEqual(exit_code, 1)

    def test_main_entrypoint_exits_with_app_code(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        from qgis_manager.cli import main

        fake_app = SimpleNamespace(run=lambda: 7)
        with (
            patch("qgis_manager.cli.CLIApp", return_value=fake_app),
            patch("qgis_manager.cli.sys.exit") as mock_exit,
        ):
            main()
        mock_exit.assert_called_once_with(7)

    def test_version_fallback_when_package_missing(self):
        import importlib
        from importlib.metadata import PackageNotFoundError
        from unittest.mock import patch

        import qgis_manager

        with patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError("qgis-manage"),
        ):
            importlib.reload(qgis_manager)
            self.assertEqual(qgis_manager.__version__, "0.0.0-unknown")
        importlib.reload(qgis_manager)

    def test_app_run_with_argv_none(self):
        with patch("sys.argv", ["qgis-manage"]):
            exit_code, output, _ = self._invoke(None)
        self.assertEqual(exit_code, 0)
        self.assertIn("usage:", output.lower())

    @patch("qgis_manager.cli.app.logging.FileHandler")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_app_log_file_handler(self, mock_find, mock_handler):
        mock_find.side_effect = FileNotFoundError("No project found")
        exit_code, _, _ = self._invoke(
            ["--verbose", "--log-file", "/tmp/qgis-test.log", "deploy"]
        )
        self.assertEqual(exit_code, 1)
        mock_handler.assert_called_once_with("/tmp/qgis-test.log")

    @patch("qgis_manager.cli.app.CLIApp._setup_logging")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_app_unexpected_error_after_parse(self, _mock_find, mock_setup):
        mock_setup.side_effect = RuntimeError("logging failed")
        exit_code, _, error = self._invoke(["deploy"])
        self.assertEqual(exit_code, 1)
        self.assertIn("logging failed", error)

    def test_registry_skips_broken_and_non_command_entry_points(self):
        from types import SimpleNamespace
        from unittest.mock import patch

        from qgis_manager.cli.registry import build_commands

        class NotACommand:
            pass

        broken = SimpleNamespace(
            name="broken", load=lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        )
        invalid = SimpleNamespace(name="invalid", load=lambda: NotACommand)
        with patch(
            "qgis_manager.cli.registry.entry_points",
            return_value=[broken, invalid],
        ):
            commands = build_commands()
        self.assertTrue(commands)
        self.assertFalse(any(command.name == "broken" for command in commands))


if __name__ == "__main__":
    unittest.main()

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    def test_analyzer_output_falls_back_to_uv(self, mock_run):
        from qgis_manager.cli.analyzer import run_qgis_analyzer_output

        mock_run.side_effect = [
            FileNotFoundError(),
            unittest.mock.Mock(returncode=0, stdout="{}"),
        ]
        code, output = run_qgis_analyzer_output(Path("."), "security")
        self.assertEqual(code, 0)
        self.assertEqual(output, "{}")
