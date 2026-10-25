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
