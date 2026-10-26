"""Tests for built-artifact validation."""

from __future__ import annotations

import struct
import zipfile
from pathlib import Path

import pytest

from qgis_manager.validation.artifact import ArtifactError, validate_artifact

METADATA = """[general]
name=Demo Plugin
description=Demo
about=Demo plugin
version=1.0.0
qgisMinimumVersion=3.0
author=Tester
email=test@example.com
repository=https://example.com/repo
icon=icon.png
"""


def _png(width: int = 32, height: int = 32) -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + b"IHDR"
        + struct.pack(">II", width, height)
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )


def _make_zip(
    tmp_path: Path,
    *,
    name: str = "demo.1.0.0.zip",
    metadata: str | None = METADATA,
    license_text: str | None = "GPL",
    readme: bool = True,
    icon: bytes | None = None,
    extra: dict[str, bytes] | None = None,
    mode: int = 0o644,
    root: str = "demo",
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    path = tmp_path / name
    files: dict[str, bytes] = {}
    if metadata is not None:
        files[f"{root}/metadata.txt"] = metadata.encode()
    if license_text is not None:
        files[f"{root}/LICENSE"] = license_text.encode()
    if readme:
        files[f"{root}/README.md"] = b"# Demo\n"
    if icon is not None:
        files[f"{root}/icon.png"] = icon
    files.update(extra or {})
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        for arcname, data in files.items():
            info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = (0o100000 | mode) << 16
            archive.writestr(info, data)
    return path


def test_valid_artifact_passes(tmp_path: Path) -> None:
    result = validate_artifact(_make_zip(tmp_path, icon=_png()))
    assert result.is_valid, result.errors
    assert result.root == "demo"
    assert not result.warnings


def test_missing_license_is_error(tmp_path: Path) -> None:
    result = validate_artifact(_make_zip(tmp_path, license_text=None, icon=_png()))
    assert any("ARTIFACT_LICENSE" in error for error in result.errors)


def test_multiple_roots_is_error(tmp_path: Path) -> None:
    result = validate_artifact(
        _make_zip(tmp_path, extra={"other/file.py": b"x"}, icon=_png())
    )
    assert any("ARTIFACT_ROOT" in error for error in result.errors)


def test_binary_and_dev_files_are_errors(tmp_path: Path) -> None:
    result = validate_artifact(
        _make_zip(
            tmp_path,
            extra={"demo/plugin.pyc": b"x", "demo/tests/test_x.py": b"x"},
            icon=_png(),
        )
    )
    errors = " ".join(result.errors)
    assert "ARTIFACT_BINARY" in errors
    assert "ARTIFACT_DEV_FILE" in errors


def test_size_limit_uses_zip_file(tmp_path: Path) -> None:
    path = _make_zip(
        tmp_path,
        icon=_png(),
        extra={"demo/big.bin": b"\0" * (26 * 1024 * 1024)},
        compression=zipfile.ZIP_STORED,
    )
    result = validate_artifact(path)
    assert any("ARTIFACT_SIZE" in error for error in result.errors)


def test_permission_warning_and_strict_error(tmp_path: Path) -> None:
    path = _make_zip(tmp_path, icon=_png(), mode=0o600)
    warning = validate_artifact(path)
    strict = validate_artifact(path, strict_permissions=True)
    assert any("ARTIFACT_PERMISSIONS" in warning for warning in warning.warnings)
    assert any("ARTIFACT_PERMISSIONS" in error for error in strict.errors)


def test_icon_and_readme_warnings(tmp_path: Path) -> None:
    result = validate_artifact(_make_zip(tmp_path, readme=False))
    warnings = " ".join(result.warnings)
    assert "ARTIFACT_ICON" in warnings
    assert "ARTIFACT_README" in warnings


def test_filename_version_mismatch_is_error(tmp_path: Path) -> None:
    result = validate_artifact(_make_zip(tmp_path, name="demo.9.9.9.zip", icon=_png()))
    assert any("ARTIFACT_METADATA" in error for error in result.errors)


def test_invalid_zip_raises_artifact_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.zip"
    path.write_bytes(b"not a zip")
    with pytest.raises(ArtifactError):
        validate_artifact(path)


def test_invalid_root_and_unsafe_member(tmp_path: Path) -> None:
    bad_root = validate_artifact(_make_zip(tmp_path, root="1demo", icon=_png()))
    assert any("ARTIFACT_ROOT" in error for error in bad_root.errors)
    unsafe = validate_artifact(
        _make_zip(tmp_path, extra={"../evil.py": b"x"}, icon=_png())
    )
    assert any("ARTIFACT_ROOT" in error for error in unsafe.errors)


def test_missing_or_invalid_metadata(tmp_path: Path) -> None:
    missing = validate_artifact(
        _make_zip(tmp_path, metadata=None, extra={"demo/only.py": b"x"}, icon=_png())
    )
    assert any("ARTIFACT_METADATA" in error for error in missing.errors)
    broken = validate_artifact(
        _make_zip(tmp_path, metadata="not a section", icon=_png())
    )
    assert any("ARTIFACT_METADATA" in error for error in broken.errors)


def test_empty_license_and_invalid_qgis_version(tmp_path: Path) -> None:
    empty = validate_artifact(_make_zip(tmp_path, license_text="", icon=_png()))
    assert any("LICENSE is empty" in error for error in empty.errors)
    bad_qgis = METADATA.replace("qgisMinimumVersion=3.0", "qgisMinimumVersion=3.x")
    invalid = validate_artifact(_make_zip(tmp_path, metadata=bad_qgis, icon=_png()))
    assert any("qgisMinimumVersion" in error for error in invalid.errors)


def test_icon_non_png_and_too_small(tmp_path: Path) -> None:
    non_png = validate_artifact(_make_zip(tmp_path, icon=b"not-png"))
    assert any("not a PNG" in warning for warning in non_png.warnings)
    small = validate_artifact(_make_zip(tmp_path, icon=_png(8, 8)))
    assert any("expected at least" in warning for warning in small.warnings)


def test_hidden_file_and_directory_entry(tmp_path: Path) -> None:
    path = _make_zip(
        tmp_path,
        extra={"demo/.secret": b"x"},
        icon=_png(),
    )
    with zipfile.ZipFile(path, "a") as archive:
        directory = zipfile.ZipInfo("demo/", date_time=(1980, 1, 1, 0, 0, 0))
        directory.external_attr = 0o40755 << 16
        archive.writestr(directory, b"")
    result = validate_artifact(path)
    assert any("Hidden file" in error for error in result.errors)
