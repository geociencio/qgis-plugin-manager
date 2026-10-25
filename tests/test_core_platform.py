import unittest
from pathlib import Path
from unittest.mock import patch

from qgis_manager.core import (
    get_qgis_plugin_dir,
)


class TestCorePlatform(unittest.TestCase):
    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux(self):
        expected_v3 = (
            Path.home() / ".local/share/QGIS/QGIS3/profiles/default/python/plugins"
        )
        expected_v4 = (
            Path.home() / ".local/share/QGIS/QGIS4/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "linux")
    def test_get_qgis_plugin_dir_linux_custom_profile(self):
        expected = Path.home() / ".local/share/QGIS/QGIS3/profiles/prod/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="prod", version=3), expected)

    @patch("sys.platform", "darwin")
    def test_get_qgis_plugin_dir_darwin(self):
        expected_v3 = (
            Path.home()
            / "Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
        )
        expected_v4 = (
            Path.home()
            / "Library/Application Support/QGIS/QGIS4/profiles/default/python/plugins"
        )
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "win32")
    @patch("os.environ", {})
    def test_get_qgis_plugin_dir_win32_missing_appdata(self):
        with self.assertRaisesRegex(OSError, "APPDATA"):
            get_qgis_plugin_dir()

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32(self):
        expected_v3 = Path("/appdata") / "QGIS/QGIS3/profiles/default/python/plugins"
        expected_v4 = Path("/appdata") / "QGIS/QGIS4/profiles/default/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(version=3), expected_v3)
        self.assertEqual(get_qgis_plugin_dir(version=4), expected_v4)

    @patch("sys.platform", "win32")
    @patch("os.environ", {"APPDATA": "/appdata"})
    def test_get_qgis_plugin_dir_win32_custom(self):
        expected = Path("/appdata") / "QGIS/QGIS3/profiles/test/python/plugins"
        self.assertEqual(get_qgis_plugin_dir(profile="test", version=3), expected)

    @patch("sys.platform", "unknown")
    def test_get_qgis_plugin_dir_unsupported(self):
        with self.assertRaisesRegex(OSError, "Unsupported platform"):
            get_qgis_plugin_dir()
