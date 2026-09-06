import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.cli.app import CLIApp
from qgis_manager.config import Settings
from qgis_manager.validation import ValidationResult


class _CommandTestBase(unittest.TestCase):
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


class TestCleanCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.clean.clean_artifacts")
    @patch("qgis_manager.cli.commands.clean.find_project_root")
    def test_clean_success(self, mock_find, mock_clean):
        mock_find.return_value = Path(tempfile.mkdtemp())
        exit_code, output, _ = self._invoke(["clean"])
        self.assertEqual(exit_code, 0)
        mock_clean.assert_called_once()
        self.assertIn("Cleanup complete", output)


class TestInstallDepsCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.install_deps.install_external_libs")
    @patch("qgis_manager.cli.commands.install_deps.find_project_root")
    def test_install_deps_success(self, mock_find, mock_install):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_install.return_value = True
        exit_code, output, _ = self._invoke(["install-deps"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Dependencies ready", output)

    @patch("qgis_manager.cli.commands.install_deps.install_external_libs")
    @patch("qgis_manager.cli.commands.install_deps.find_project_root")
    def test_install_deps_failure(self, mock_find, mock_install):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_install.return_value = False
        exit_code, _, _ = self._invoke(["install-deps"])
        self.assertEqual(exit_code, 1)


class TestAnalyzeCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.analyze.subprocess.run")
    @patch("qgis_manager.cli.commands.analyze.find_project_root")
    def test_analyze_direct(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.return_value.returncode = 0
        exit_code, _, _ = self._invoke(["analyze"])
        self.assertEqual(exit_code, 0)

    @patch("qgis_manager.cli.commands.analyze.subprocess.run")
    @patch("qgis_manager.cli.commands.analyze.find_project_root")
    def test_analyze_fallback_to_uv(self, mock_find, mock_run):
        mock_find.return_value = Path(tempfile.mkdtemp())
        mock_run.side_effect = [FileNotFoundError(), Mock(returncode=0)]
        exit_code, _, _ = self._invoke(["analyze"])
        self.assertEqual(exit_code, 0)


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

    @patch("qgis_manager.cli.commands.validate.find_project_root")
    def test_validate_success(self, mock_find):
        root = self._make_project()
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, output, _ = self._invoke(["validate"])
        self.assertEqual(exit_code, 0)
        self.assertIn("passed", output)

    @patch("qgis_manager.cli.commands.validate.find_project_root")
    def test_validate_strict_fails_on_warnings(self, mock_find):
        root = self._make_project()
        self._write_metadata(root, include_recommended=False)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate", "--strict"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.commands.validate.find_project_root")
    def test_validate_missing_init_py(self, mock_find):
        root = Path(tempfile.mkdtemp())
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.commands.validate.find_project_root")
    def test_validate_repo_flag(self, mock_find):
        root = self._make_project()
        self._write_metadata(root)
        mock_find.return_value = root

        exit_code, _, _ = self._invoke(["validate", "--repo"])
        self.assertEqual(exit_code, 1)  # no LICENSE file in temp project


class TestPackageCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.commands.package.find_project_root")
    def test_package_success(self, mock_find, mock_package, mock_install):
        root = Path(tempfile.mkdtemp())
        (root / "metadata.txt").write_text(
            "[general]\nname=Test Plugin\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root
        mock_package.return_value = root / "dist" / "test_plugin.1.0.0.zip"

        exit_code, output, _ = self._invoke(["package"])
        self.assertEqual(exit_code, 0)
        self.assertIn("Package created", output)
        mock_package.assert_called_once()

    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.commands.package.find_project_root")
    def test_package_sync_version(self, mock_find, mock_package, mock_install):
        root = Path(tempfile.mkdtemp())
        (root / "pyproject.toml").write_text(
            '[project]\nname = "demo"\nversion = "2.0.0"\n', encoding="utf-8"
        )
        (root / "metadata.txt").write_text(
            "[general]\nname=demo\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root
        mock_package.return_value = root / "dist" / "demo.2.0.0.zip"

        exit_code, _, _ = self._invoke(["package", "--sync-version"])
        self.assertEqual(exit_code, 0)
        self.assertIn("version=2.0.0", (root / "metadata.txt").read_text())

    @patch("qgis_manager.validation.validate_project_structure")
    @patch("qgis_manager.validation.validate_official_compliance")
    @patch("qgis_manager.validation.validate_metadata")
    @patch("qgis_manager.cli.commands.package.find_project_root")
    def test_package_repo_check_fails(
        self, mock_find, mock_meta, mock_repo, mock_struct
    ):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        mock_meta.return_value = ValidationResult(True, [], [])
        mock_repo.return_value = ValidationResult(False, ["Forbidden binary found"], [])
        mock_struct.return_value = ValidationResult(True, [], [])

        exit_code, output, _ = self._invoke(["package", "--repo-check"])
        self.assertEqual(exit_code, 1)
        self.assertIn("compliance failed", output)

    @patch("qgis_manager.validation.validate_project_structure")
    @patch("qgis_manager.validation.validate_official_compliance")
    @patch("qgis_manager.validation.validate_metadata")
    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.commands.package.find_project_root")
    def test_package_repo_check_passes(
        self, mock_find, mock_package, mock_install, mock_meta, mock_repo, mock_struct
    ):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        mock_meta.return_value = ValidationResult(True, [], [])
        mock_repo.return_value = ValidationResult(True, [], [])
        mock_struct.return_value = ValidationResult(True, [], [])
        mock_package.return_value = root / "dist" / "demo.zip"

        exit_code, _, _ = self._invoke(["package", "--repo-check"])
        self.assertEqual(exit_code, 0)


class TestHooksCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.hooks.find_project_root")
    def test_hooks_list_empty(self, mock_find):
        mock_find.return_value = Path(tempfile.mkdtemp())
        exit_code, output, _ = self._invoke(["hooks", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("No hooks found", output)

    @patch("qgis_manager.cli.commands.hooks.find_project_root")
    def test_hooks_init(self, mock_find):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        exit_code, _, _ = self._invoke(["hooks", "init"])
        self.assertEqual(exit_code, 0)
        self.assertTrue((root / "plugin_hooks.py").exists())

    @patch("qgis_manager.cli.commands.hooks.find_project_root")
    def test_hooks_test(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    return True\n", encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(["hooks", "test", "pre_deploy"])
        self.assertEqual(exit_code, 0)
        self.assertIn("executed successfully", output)


class TestDeployCommand(_CommandTestBase):
    def _patch_common(self, mock_find, mock_load_config, mock_load_project):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        settings = Settings()
        settings.auto_compile = False
        mock_load_config.return_value = settings
        mock_load_project.side_effect = lambda _root, s: s
        return root

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.commands.deploy.find_project_root")
    def test_deploy_success(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        dest = Path(tempfile.mkdtemp())
        mock_dir.return_value = dest

        exit_code, output, _ = self._invoke(["deploy"])

        self.assertEqual(exit_code, 0)
        mock_deploy.assert_called_once()
        self.assertEqual(mock_deploy.call_args.kwargs["dest_dir"], dest)
        self.assertIn("Deployment complete", output)

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.commands.deploy.find_project_root")
    def test_deploy_no_backup(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())

        exit_code, _, _ = self._invoke(["deploy", "--no-backup"])

        self.assertEqual(exit_code, 0)
        self.assertTrue(mock_deploy.call_args.kwargs["no_backup"])

    @patch("qgis_manager.cli.commands.deploy.find_project_root")
    def test_deploy_no_project(self, mock_find):
        mock_find.side_effect = FileNotFoundError("No project found")
        exit_code, _, _ = self._invoke(["deploy"])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
