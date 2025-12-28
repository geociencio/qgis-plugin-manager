from pathlib import Path

import pytest

from qgis_manager.discovery import find_project_root, get_plugin_metadata, slugify


def test_slugify():
    assert slugify("My Plugin") == "my_plugin"
    assert slugify("Plugin  With   Spaces") == "plugin_with_spaces"
    assert slugify("Plugin@#$") == "plugin"
    assert slugify("Café Plugin") == "café_plugin"


def test_find_project_root_success(tmp_path):
    # Setup
    (tmp_path / "metadata.txt").touch()

    # Execute
    root = find_project_root(tmp_path)

    # Verify
    assert root == tmp_path


def test_find_project_root_nested(tmp_path):
    # Setup
    (tmp_path / "metadata.txt").touch()
    nested = tmp_path / "src" / "subfolder"
    nested.mkdir(parents=True)

    # Execute
    root = find_project_root(nested)

    # Verify
    assert root == tmp_path


def test_find_project_root_failure(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_project_root(tmp_path)


def test_get_plugin_metadata(tmp_path):
    metadata_file = tmp_path / "metadata.txt"
    metadata_file.write_text(
        "[general]\nname = Test Plugin\nversion = 1.0", encoding="utf-8"
    )

    meta = get_plugin_metadata(tmp_path)
    assert meta["name"] == "Test Plugin"
    assert meta["slug"] == "test_plugin"
    assert meta["version"] == "1.0"


def test_get_source_files(tmp_path: Path):
    from qgis_manager.discovery import get_source_files

    # Setup structure
    (tmp_path / "plugin.py").touch()
    (tmp_path / "metadata.txt").touch()
    (tmp_path / "resources.qrc").touch()

    files = get_source_files(tmp_path)
    basenames = [f.name for f in files]

    assert "plugin.py" in basenames
    assert "metadata.txt" in basenames
    assert "resources.qrc" in basenames
