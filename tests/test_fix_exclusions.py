import zipfile
from pathlib import Path

from qgis_manager.core import create_plugin_package, deploy_plugin


def test_deploy_preserves_nested_tools(tmp_path: Path):
    """Test that deploy_plugin preserves nested 'tools' while ignoring root ones."""
    # Setup mock project
    project_root = tmp_path / "my_plugin"
    project_root.mkdir()
    (project_root / "metadata.txt").write_text("[general]\nname=My Plugin\nversion=0.1")

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
    assert (deploy_path / "gui" / "tools" / "util.py").exists()

    # Verify root tools are EXCLUDED
    assert not (deploy_path / "tools").exists()


def test_package_preserves_nested_tools(tmp_path: Path):
    """Test that create_plugin_package preserves nested 'tools' directories."""
    # Setup mock project
    project_root = tmp_path / "my_plugin"
    project_root.mkdir()
    (project_root / "metadata.txt").write_text("[general]\nname=My Plugin\nversion=0.1")

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
        assert "my_plugin/gui/tools/util.py" in names
        assert "my_plugin/tools/dev_tool.py" not in names
