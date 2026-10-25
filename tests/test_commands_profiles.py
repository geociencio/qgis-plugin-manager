"""Tests for the profiles list command."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from .command_test_base import _CommandTestBase


class TestProfilesCommand(_CommandTestBase):
    @patch("qgis_manager.cli.commands.profiles.get_qgis_plugin_dir")
    def test_profiles_list(self, mock_dir):
        root = Path(tempfile.mkdtemp()) / "profiles"
        default_plugins = root / "default" / "python" / "plugins"
        default_plugins.mkdir(parents=True)
        (default_plugins / "demo").mkdir()
        other_plugins = root / "production" / "python" / "plugins"
        other_plugins.mkdir(parents=True)
        mock_dir.return_value = default_plugins

        exit_code, output, _ = self._invoke(["profiles", "list"])

        self.assertEqual(exit_code, 0)
        self.assertIn("default", output)
        self.assertIn("production", output)
        self.assertIn("1 plugins", output)

    @patch("qgis_manager.cli.commands.profiles.get_qgis_plugin_dir")
    def test_profiles_missing(self, mock_dir):
        root = Path(tempfile.mkdtemp()) / "missing" / "python" / "plugins"
        mock_dir.return_value = root
        exit_code, output, _ = self._invoke(["profiles", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("No QGIS profiles found", output)

    def test_profiles_requires_action(self):
        exit_code, _, stderr = self._invoke(["profiles"])
        self.assertEqual(exit_code, 1)
        self.assertIn("profiles list", stderr)

    @patch("qgis_manager.cli.commands.profiles.get_qgis_plugin_dir")
    def test_profiles_without_plugins_dir(self, mock_dir):
        root = Path(tempfile.mkdtemp()) / "profiles"
        profile = root / "default"
        profile.mkdir(parents=True)
        mock_dir.return_value = profile / "python" / "plugins"
        exit_code, output, _ = self._invoke(["profiles", "list"])
        self.assertEqual(exit_code, 0)
        self.assertIn("0 plugins", output)
