import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qgis_manager.config import Settings, load_config, load_project_config


class TestConfig(unittest.TestCase):
    def test_settings_defaults(self):
        settings = Settings()
        self.assertEqual(settings.profile, "default")
        self.assertTrue(settings.backup)
        self.assertTrue(settings.auto_compile)
        self.assertEqual(settings.hooks, {})

    def test_load_project_config(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            pyproject = tmp_path / "pyproject.toml"
            pyproject.write_text(
                """
[tool.qgis-manager]
profile = "prod"
backup = false
auto_compile = false
[tool.qgis-manager.hooks]
pre_deploy = "echo 1"
""",
                encoding="utf-8",
            )

            settings = Settings()
            settings = load_project_config(tmp_path, settings)

            self.assertEqual(settings.profile, "prod")
            self.assertFalse(settings.backup)
            self.assertFalse(settings.auto_compile)
            self.assertEqual(settings.hooks["pre_deploy"], "echo 1")

    @patch("pathlib.Path.home")
    def test_load_config_no_file(self, mock_home):
        mock_home.return_value = Path("/nonexistent")
        settings = load_config()
        self.assertEqual(settings.profile, "default")

    @patch("pathlib.Path.home")
    def test_load_config_with_file(self, mock_home):
        with tempfile.TemporaryDirectory() as tmp_dir:
            home = Path(tmp_dir)
            cfg = home / ".config" / "qgis-manager" / "config.toml"
            cfg.parent.mkdir(parents=True)
            cfg.write_text(
                '[defaults]\nprofile = "prod"\nqgis_version = 4\n'
                "backup = false\nmax_backups = 5\nauto_compile = false\n",
                encoding="utf-8",
            )
            mock_home.return_value = home

            settings = load_config()

            self.assertEqual(settings.profile, "prod")
            self.assertEqual(settings.qgis_version, 4)
            self.assertFalse(settings.backup)
            self.assertEqual(settings.max_backups, 5)
            self.assertFalse(settings.auto_compile)


if __name__ == "__main__":
    unittest.main()
