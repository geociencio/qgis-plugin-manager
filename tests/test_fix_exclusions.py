import tempfile
import unittest
import zipfile
from pathlib import Path

from qgis_manager.core import create_plugin_package, deploy_plugin


class TestExclusions(unittest.TestCase):
    def test_deploy_preserves_nested_tools(self):
        """Test that deploy_plugin preserves nested 'tools' while ignoring root ones."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup mock project
            project_root = tmp_path / "my_plugin"
            project_root.mkdir()
            (project_root / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=0.1"
            )

            gui_dir = project_root / "gui"
            gui_dir.mkdir()
            (gui_dir / "main.py").touch()

            # Nested tools (should be preserved)
            nested_tools = gui_dir / "tools"
            nested_tools.mkdir()
            (nested_tools / "util.py").touch()

            # Root tools (should be excluded)
            root_tools = project_root / "tools"
            root_tools.mkdir()
            (root_tools / "dev_tool.py").touch()

            # Mock QGIS plugin dir
            dest_dir = tmp_path / "qgis_plugins"
            dest_dir.mkdir()

            # Run deployment
            deploy_plugin(project_root, dest_dir=dest_dir)

            deploy_path = dest_dir / "my_plugin"

            # Verify nested tools exist
            self.assertTrue((deploy_path / "gui" / "tools" / "util.py").exists())

            # Verify root tools are EXCLUDED
            self.assertFalse((deploy_path / "tools").exists())

    def test_package_preserves_nested_tools(self):
        """Test that create_plugin_package preserves nested 'tools' directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup mock project
            project_root = tmp_path / "my_plugin"
            project_root.mkdir()
            (project_root / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=0.1"
            )

            gui_dir = project_root / "gui"
            gui_dir.mkdir()
            (gui_dir / "main.py").touch()

            # Nested tools
            nested_tools = gui_dir / "tools"
            nested_tools.mkdir()
            (nested_tools / "util.py").touch()

            # Root tools
            root_tools = project_root / "tools"
            root_tools.mkdir()
            (root_tools / "dev_tool.py").touch()

            output_dir = tmp_path / "dist"

            # Run packaging
            zip_path = create_plugin_package(project_root, output_dir=output_dir)

            # Verify ZIP content
            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
                self.assertIn("my_plugin/gui/tools/util.py", names)
                self.assertNotIn("my_plugin/tools/dev_tool.py", names)

    def test_package_excludes_nested_wildcard_directories(self):
        """Test that nested directories matching wildcard patterns are excluded."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup project structure
            project_root = tmp_path / "test_plugin_wildcard"
            project_root.mkdir()

            # Metadata
            metadata_content = """[general]
name=Test Plugin Wildcard
qgisMinimumVersion=3.0
description=Test
version=0.1
author=Me
email=me@example.com
"""
            (project_root / "metadata.txt").write_text(metadata_content)

            # Valid source file
            src_dir = project_root / "src"
            src_dir.mkdir()
            (src_dir / "plugin.py").write_text("print('hello')")

            # Nested ignored directory (matching *.egg-info)
            bad_dir = src_dir / "my_lib.egg-info"
            bad_dir.mkdir()
            (bad_dir / "PKG-INFO").write_text("trash")

            # Run packing
            zip_path = create_plugin_package(project_root, output_dir=tmp_path / "dist")

            self.assertTrue(zip_path.exists())

            # Verify zip content
            with zipfile.ZipFile(zip_path, "r") as zf:
                files = zf.namelist()
                slug = "test_plugin_wildcard"

                # Valid file should be there
                self.assertIn(f"{slug}/src/plugin.py", files)

                # Wildcard match exclusion checks
                self.assertNotIn(f"{slug}/src/my_lib.egg-info/PKG-INFO", files)


if __name__ == "__main__":
    unittest.main()
