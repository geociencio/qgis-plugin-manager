"""Edge cases for metadata parsing and persistence."""

import configparser
from pathlib import Path
from unittest.mock import patch

from qgis_manager.metadata import (
    get_plugin_metadata,
    save_plugin_metadata,
    update_general_keys,
)


def test_update_general_keys_creates_missing_section(tmp_path: Path) -> None:
    result = update_general_keys("name=Demo\n", {"version": "1.0.0"})
    assert "[general]" in result
    assert "version=1.0.0" in result


def test_update_general_keys_empty_updates_is_noop() -> None:
    text = "[general]\nname=Demo\n"
    assert update_general_keys(text, {}) == text


def test_get_plugin_metadata_falls_back_to_latin1(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_bytes(
        "[general]\nname=Cañón\nversion=1.0.0\n".encode("latin-1")
    )
    metadata = get_plugin_metadata(tmp_path)
    assert metadata["name"] == "Cañón"
    assert metadata["version"] == "1.0.0"


def test_get_plugin_metadata_missing_general_section(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_text("[other]\nname=Demo\n", encoding="utf-8")
    metadata = get_plugin_metadata(tmp_path)
    assert metadata["name"] == tmp_path.name
    assert "version" not in metadata


def test_get_plugin_metadata_adds_missing_name(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_text(
        "[general]\nversion=1.0.0\n", encoding="utf-8"
    )
    metadata = get_plugin_metadata(tmp_path)
    assert metadata["name"] == tmp_path.name
    assert metadata["version"] == "1.0.0"


def test_get_plugin_metadata_read_error_falls_back(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_text("[general]\nname=Demo\n")
    with patch.object(
        configparser.ConfigParser,
        "read",
        side_effect=OSError("denied"),
    ):
        metadata = get_plugin_metadata(tmp_path)
    assert metadata["name"] == tmp_path.name


def test_save_plugin_metadata_unchanged_is_noop(tmp_path: Path) -> None:
    (tmp_path / "metadata.txt").write_text(
        "[general]\nname=Demo\nversion=1.0.0\n", encoding="utf-8"
    )
    with patch("qgis_manager.metadata.write_text_atomic") as mock_write:
        save_plugin_metadata(tmp_path, {"name": "Demo", "version": "1.0.0"})
    mock_write.assert_not_called()


def test_save_plugin_metadata_creates_missing_file(tmp_path: Path) -> None:
    save_plugin_metadata(tmp_path, {"name": "Demo", "version": "1.0.0"})
    assert "[general]" in (tmp_path / "metadata.txt").read_text(encoding="utf-8")
