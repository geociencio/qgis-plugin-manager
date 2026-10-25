import tempfile
from pathlib import Path
from unittest.mock import patch

from qgis_manager.config import Settings

from .command_test_base import _CommandTestBase


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
    @patch("qgis_manager.cli.base.find_project_root")
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
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_uses_configured_profile(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        settings = Settings(profile="production")
        settings.auto_compile = False
        mock_load_config.return_value = settings
        mock_load_project.side_effect = lambda _root, value: value
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())

        exit_code, _, _ = self._invoke(["deploy"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_dir.call_args.args[0], "production")

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_cli_profile_overrides_config(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        settings = Settings(profile="production")
        settings.auto_compile = False
        mock_load_config.return_value = settings
        mock_load_project.side_effect = lambda _root, value: value
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())

        exit_code, _, _ = self._invoke(["deploy", "--profile", "staging"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_dir.call_args.args[0], "staging")

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
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

    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_no_project(self, mock_find):
        mock_find.side_effect = FileNotFoundError("No project found")
        exit_code, _, _ = self._invoke(["deploy"])
        self.assertEqual(exit_code, 1)

    @patch("qgis_manager.cli.commands.deploy.compile_qt_resources", return_value=False)
    @patch("qgis_manager.cli.commands.deploy.count_compile_steps", return_value=1)
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_aborts_when_compile_fails(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        _mock_count,
        _mock_compile,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_load_config.return_value.auto_compile = True
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())

        exit_code, _, stderr = self._invoke(["deploy"])

        self.assertEqual(exit_code, 1)
        mock_deploy.assert_not_called()
        self.assertIn("Compilation failed", stderr)

    @patch("qgis_manager.core.purge_backups", return_value=2)
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_purge_backups(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_purge,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())
        mock_confirm.side_effect = [True, True]

        exit_code, output, _ = self._invoke(["deploy", "--purge-backups"])

        self.assertEqual(exit_code, 0)
        mock_purge.assert_called_once()
        mock_deploy.assert_called_once()
        self.assertIn("Backups purged", output)
        self.assertIn("2", output)

    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_purge_backups_abort(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())
        mock_confirm.side_effect = [True, False]

        exit_code, _, _ = self._invoke(["deploy", "--purge-backups"])

        self.assertEqual(exit_code, 0)
        mock_deploy.assert_not_called()

    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_creates_missing_target_dir(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        missing = root / "plugins"
        mock_dir.return_value = missing
        mock_confirm.return_value = True

        exit_code, _, _ = self._invoke(["deploy"])

        self.assertEqual(exit_code, 0)
        self.assertTrue(missing.exists())
        self.assertEqual(mock_deploy.call_args.kwargs["dest_dir"], missing)

    @patch("qgis_manager.cli.commands.deploy.click.prompt")
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_manual_path(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_prompt,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = root / "missing"
        mock_confirm.return_value = False
        mock_prompt.return_value = "/custom/plugins"

        exit_code, _, _ = self._invoke(["deploy"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            mock_deploy.call_args.kwargs["dest_dir"], Path("/custom/plugins")
        )

    @patch("qgis_manager.cli.commands.deploy.click.prompt")
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_abort_no_manual_path(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_prompt,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = root / "missing"
        mock_confirm.return_value = False
        mock_prompt.return_value = ""

        exit_code, _, _ = self._invoke(["deploy"])

        self.assertEqual(exit_code, 1)
        mock_deploy.assert_not_called()

    @patch("qgis_manager.cli.commands.deploy.run_hook")
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_runs_hooks(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_run_hook,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())
        mock_confirm.return_value = True
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    return True\n", encoding="utf-8"
        )
        mock_run_hook.return_value = True

        exit_code, _, _ = self._invoke(["deploy", "--trust"])

        self.assertEqual(exit_code, 0)
        hook_names = [c.args[0] for c in mock_run_hook.call_args_list]
        self.assertIn("pre_deploy", hook_names)
        self.assertIn("post_deploy", hook_names)

    @patch("qgis_manager.cli.commands.deploy.run_hook")
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_pre_hook_failure(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_run_hook,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())
        (root / "plugin_hooks.py").write_text(
            "def pre_deploy(context):\n    return False\n", encoding="utf-8"
        )
        mock_run_hook.return_value = False

        exit_code, _, _ = self._invoke(["deploy", "--trust"])

        self.assertEqual(exit_code, 1)
        mock_deploy.assert_not_called()

    @patch("qgis_manager.core.purge_backups", return_value=2)
    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_purge_backups_yes(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
        mock_purge,
    ):
        self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = Path(tempfile.mkdtemp())

        exit_code, output, _ = self._invoke(["deploy", "--purge-backups", "--yes"])

        self.assertEqual(exit_code, 0)
        mock_confirm.assert_not_called()
        mock_purge.assert_called_once()
        mock_deploy.assert_called_once()
        self.assertIn("Backups purged", output)

    @patch("qgis_manager.cli.commands.deploy.click.confirm")
    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_yes_creates_missing_target(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
        mock_confirm,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        missing = root / "plugins"
        mock_dir.return_value = missing

        exit_code, _, _ = self._invoke(["deploy", "--yes"])

        self.assertEqual(exit_code, 0)
        mock_confirm.assert_not_called()
        self.assertTrue(missing.exists())
        self.assertEqual(mock_deploy.call_args.kwargs["dest_dir"], missing)

    def test_deploy_yes_conflicts_with_interactive(self):
        exit_code, _, stderr = self._invoke(["deploy", "--yes", "--interactive"])
        self.assertEqual(exit_code, 1)
        self.assertIn("cannot be used together", stderr)

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_no_manifest(
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
        exit_code, _, _ = self._invoke(["deploy", "--no-manifest"])
        self.assertEqual(exit_code, 0)
        self.assertFalse(mock_deploy.call_args.kwargs["use_manifest"])

    @patch("qgis_manager.cli.commands.deploy.deploy_plugin")
    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_dry_run_mutates_nothing(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
        mock_deploy,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        (root / "plugin.py").write_text("x=1\n", encoding="utf-8")
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        target = root / "plugins"
        mock_dir.return_value = target

        exit_code, output, _ = self._invoke(["deploy", "--dry-run"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Dry run", output)
        self.assertIn("Files to copy", output)
        mock_deploy.assert_not_called()
        self.assertFalse(target.exists())

    @patch("qgis_manager.cli.commands.deploy.get_qgis_plugin_dir")
    @patch("qgis_manager.cli.commands.deploy.get_plugin_metadata")
    @patch("qgis_manager.cli.commands.deploy.load_project_config")
    @patch("qgis_manager.cli.commands.deploy.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_deploy_dry_run_reports_purge_and_hooks(
        self,
        mock_find,
        mock_load_config,
        mock_load_project,
        mock_meta,
        mock_dir,
    ):
        root = self._patch_common(mock_find, mock_load_config, mock_load_project)
        target = root / "plugins"
        target.mkdir()
        (target / "test.bak.1").mkdir()
        (root / "plugin_hooks.py").write_text("def pre_deploy(ctx): pass\n")
        mock_meta.return_value = {"name": "Test", "slug": "test"}
        mock_dir.return_value = target

        exit_code, output, _ = self._invoke(
            ["deploy", "--dry-run", "--purge-backups", "--trust"]
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Backups to purge", output)
        self.assertIn("would run", output)
        self.assertTrue((target / "test.bak.1").exists())


class TestDCleanCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.dclean.uninstall_plugin")
    @patch("qgis_manager.cli.commands.dclean.load_project_config")
    @patch("qgis_manager.cli.commands.dclean.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_dclean_success(
        self, mock_find, mock_load_config, mock_load_project, mock_uninstall
    ):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        mock_load_config.return_value = Settings()
        mock_load_project.side_effect = lambda _r, s: s
        mock_uninstall.return_value = root / "removed"

        exit_code, output, _ = self._invoke(["dclean", "--yes"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Removed", output)
        mock_uninstall.assert_called_once()

    @patch("qgis_manager.cli.commands.dclean.uninstall_plugin")
    @patch("qgis_manager.cli.commands.dclean.load_project_config")
    @patch("qgis_manager.cli.commands.dclean.load_config")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_dclean_not_deployed(
        self, mock_find, mock_load_config, mock_load_project, mock_uninstall
    ):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        mock_load_config.return_value = Settings()
        mock_load_project.side_effect = lambda _r, s: s
        mock_uninstall.return_value = None

        exit_code, output, _ = self._invoke(["dclean", "--yes"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Nothing to remove", output)
