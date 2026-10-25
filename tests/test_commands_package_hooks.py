import tempfile
from pathlib import Path
from unittest.mock import patch

from qgis_manager.validation import ValidationResult

from .command_test_base import _CommandTestBase


class TestPackageCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.base.find_project_root")
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
    @patch("qgis_manager.cli.base.find_project_root")
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
    @patch("qgis_manager.cli.base.find_project_root")
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
    @patch("qgis_manager.cli.base.find_project_root")
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

    @patch(
        "qgis_manager.cli.commands.package.install_external_libs", return_value=False
    )
    @patch("qgis_manager.cli.base.find_project_root")
    def test_package_fails_when_dependency_install_fails(
        self, mock_find, _mock_install
    ):
        mock_find.return_value = Path(tempfile.mkdtemp())

        exit_code, _, stderr = self._invoke(["package"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Dependency installation failed", stderr)

    @patch("qgis_manager.validation.validate_project_structure")
    @patch("qgis_manager.validation.validate_official_compliance")
    @patch("qgis_manager.validation.validate_metadata")
    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_package_installs_before_compliance(
        self, mock_find, mock_package, mock_install, mock_meta, mock_repo, mock_struct
    ):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        calls: list[str] = []
        mock_install.side_effect = lambda _root: calls.append("install") or True
        mock_repo.side_effect = lambda *_args: (
            calls.append("compliance") or ValidationResult(True, [], [])
        )
        mock_meta.return_value = ValidationResult(True, [], [])
        mock_struct.return_value = ValidationResult(True, [], [])
        mock_package.return_value = root / "dist" / "demo.zip"

        exit_code, _, _ = self._invoke(["package", "--repo-check"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(calls[:2], ["install", "compliance"])


class TestHooksCommand(_CommandTestBase):
    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_list_empty(self, mock_find):
        mock_find.return_value = Path(tempfile.mkdtemp())
        exit_code, output, _ = self._invoke(["hooks", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("No hooks found", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_init(self, mock_find):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        exit_code, _, _ = self._invoke(["hooks", "init"])
        self.assertEqual(exit_code, 0)
        self.assertTrue((root / "plugin_hooks.py").exists())

    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_test(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    return True\n", encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(["hooks", "test", "pre_deploy"])
        self.assertEqual(exit_code, 0)
        self.assertIn("executed successfully", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_test_failure(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    return False\n", encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, _, _ = self._invoke(["hooks", "test", "pre_deploy"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_list_with_native_hooks(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    pass\n", encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(["hooks", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("pre_deploy", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_list_with_toml_hooks(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / "pyproject.toml").write_text(
            '[tool.qgis-manager.hooks]\npost_deploy = "echo hi"\n', encoding="utf-8"
        )
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(["hooks", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("post_deploy", output)

    @patch("qgis_manager.cli.commands.hooks.click.confirm")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_init_overwrite(self, mock_find, mock_confirm):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text("original\n", encoding="utf-8")
        mock_find.return_value = root
        mock_confirm.return_value = True

        exit_code, _, _ = self._invoke(["hooks", "init"])

        self.assertEqual(exit_code, 0)
        self.assertNotIn(
            "original", (root / "plugin_hooks.py").read_text(encoding="utf-8")
        )

    @patch("qgis_manager.cli.commands.hooks.click.confirm")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_hooks_init_declined(self, mock_find, mock_confirm):
        root = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text("original\n", encoding="utf-8")
        mock_find.return_value = root
        mock_confirm.return_value = False

        exit_code, _, _ = self._invoke(["hooks", "init"])

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "original", (root / "plugin_hooks.py").read_text(encoding="utf-8")
        )

    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_package_rejects_release_version_mismatch(
        self, mock_find, mock_package, _mock_install
    ):
        root = Path(tempfile.mkdtemp())
        (root / "metadata.txt").write_text(
            "[general]\nname=Test Plugin\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root

        exit_code, _, stderr = self._invoke(["package", "--release-version", "9.9.9"])

        self.assertEqual(exit_code, 1)
        self.assertIn("does not match metadata.txt", stderr)
        mock_package.assert_not_called()

    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_package_release_version_with_stamp(
        self, mock_find, mock_package, _mock_install
    ):
        root = Path(tempfile.mkdtemp())
        metadata = root / "metadata.txt"
        metadata.write_text(
            "[general]\nname=Test Plugin\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root
        mock_package.return_value = root / "dist" / "test_plugin.9.9.9.zip"

        exit_code, _, _ = self._invoke(
            ["package", "--stamp", "--release-version", "9.9.9"]
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_package.call_args.kwargs["release_version"], "9.9.9")
        self.assertIn("version=1.0.0", metadata.read_text(encoding="utf-8"))
