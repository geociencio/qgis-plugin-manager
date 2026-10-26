import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from .command_test_base import _CommandTestBase


class TestCleanCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.clean.clean_artifacts")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_clean_success(self, mock_find, mock_clean):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_clean.return_value = []
        exit_code, output, _ = self._invoke(["clean"])
        self.assertEqual(exit_code, 0)
        mock_clean.assert_called_once()
        self.assertIn("Cleanup complete", output)

    @patch("qgis_manager.cli.commands.clean.clean_artifacts")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_clean_dry_run(self, mock_find, mock_clean):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_clean.return_value = ["remove cache", "warning: tracked"]
        exit_code, output, _ = self._invoke(["clean", "--dry-run"])
        self.assertEqual(exit_code, 0)
        self.assertIn("remove cache", output)
        self.assertIn("Dry run", output)

    @patch("qgis_manager.cli.commands.clean.clean_artifacts")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_clean_prints_tracked_warning(self, mock_find, mock_clean):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_clean.return_value = ["warning: resources.py is tracked by Git"]
        exit_code, _, error = self._invoke(["clean"])
        self.assertEqual(exit_code, 0)
        self.assertIn("tracked by Git", error)


class TestInstallDepsCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.install_deps.install_external_libs")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_install_deps_success(self, mock_find, mock_install):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_install.return_value = True
        exit_code, output, _ = self._invoke(["install-deps"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Dependencies ready", output)

    @patch("qgis_manager.cli.commands.install_deps.install_external_libs")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_install_deps_failure(self, mock_find, mock_install):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_install.return_value = False
        exit_code, _, _ = self._invoke(["install-deps"])
        self.assertEqual(exit_code, 1)


class TestAnalyzeCommand(_CommandTestBase):
    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_analyze_direct(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, _, _ = self._invoke(["analyze"])
        self.assertEqual(exit_code, 0)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_analyze_fallback_to_uv(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.side_effect = [FileNotFoundError(), Mock(returncode=0)]
        exit_code, _, _ = self._invoke(["analyze"])
        self.assertEqual(exit_code, 0)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_analyze_failure(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 2
        exit_code, output, _ = self._invoke(["analyze"])
        self.assertEqual(exit_code, 2)
        self.assertIn("Analysis failed", output)


class TestSecurityCommand(_CommandTestBase):
    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_success(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, output, _ = self._invoke(["security"])
        self.assertEqual(exit_code, 0)
        self.assertIn("security scan", output.lower())
        # qgis-analyzer invoked with --deep
        last_call = mock_run.call_args_list[-1][0][0]
        self.assertIn("security", last_call)
        self.assertIn("--deep", last_call)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_failure(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 1
        exit_code, _, _ = self._invoke(["security"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_strict_with_output(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, _, _ = self._invoke(["security", "--strict", "-o", "reports"])
        self.assertEqual(exit_code, 0)
        argv = mock_run.call_args_list[-1][0][0]
        self.assertIn("--strict", argv)
        self.assertIn("-o", argv)
        self.assertIn("reports", argv)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_analyze_max_cc_passthrough(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, _, _ = self._invoke(["analyze", "--max-cc", "10"])
        self.assertEqual(exit_code, 0)
        argv = mock_run.call_args_list[-1][0][0]
        self.assertIn("--max-cc", argv)
        self.assertIn("10", argv)

    @patch("qgis_manager.cli.analyzer.subprocess.run")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_analyze_json_output(self, mock_find, mock_run):
        import json

        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, output, _ = self._invoke(["analyze", "--json"])
        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["command"], "analyze")
        self.assertTrue(payload["success"])

    @patch("qgis_manager.cli.commands.security.run_qgis_analyzer_output")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_portal_json(self, mock_find, mock_run):
        import json

        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (0, json.dumps({"schema": 1, "findings": []}))
        exit_code, output, _ = self._invoke(
            ["security", "--portal", "--json", "--exclude", "tests"]
        )
        self.assertEqual(exit_code, 0)
        call_args = mock_run.call_args.args
        self.assertIn("--tools", call_args)
        self.assertIn("native,bandit,detect-secrets,flake8", call_args)
        self.assertIn("--exclude", call_args)
        self.assertIn("tests", call_args)
        payload = json.loads(output)
        self.assertEqual(payload["command"], "security")
        self.assertEqual(payload["data"]["analyzer"]["schema"], 1)

    @patch("qgis_manager.cli.commands.security.run_qgis_analyzer_output")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_portal_invalid_json(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (2, "not-json")
        exit_code, _, stderr = self._invoke(["security", "--portal"])
        self.assertEqual(exit_code, 2)
        self.assertIn("invalid JSON", stderr)

    @patch("qgis_manager.cli.commands.security.run_qgis_analyzer_output")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_portal_without_json_prints_payload(self, mock_find, mock_run):
        import json

        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (0, json.dumps({"schema": 1, "findings": []}))
        exit_code, output, _ = self._invoke(["security", "--portal"])
        self.assertEqual(exit_code, 0)
        self.assertIn('"schema": 1', output)

    @patch("qgis_manager.cli.commands.security.run_qgis_analyzer_output")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_security_json_empty_analyzer_output(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value = (1, "")
        exit_code, output, _ = self._invoke(["security", "--json"])
        self.assertEqual(exit_code, 1)
        self.assertIn('"success": false', output)
