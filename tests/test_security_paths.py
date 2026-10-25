"""Unit checks for path/trust hardening."""

from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path, PureWindowsPath
from unittest.mock import patch

from qgis_manager.cli.app import CLIApp
from qgis_manager.core.package import _zip_arcname


def test_zip_arcname_uses_posix_separators() -> None:
    root = PureWindowsPath("C:/project")
    file_path = PureWindowsPath("C:/project/core/helper.py")

    assert _zip_arcname(root, file_path, "demo") == "demo/core/helper.py"


def test_package_trust_allows_dependency_install(tmp_path: Path) -> None:
    app = CLIApp()
    output = tmp_path / "dist" / "demo.zip"
    with (
        patch(
            "qgis_manager.cli.commands.package.find_project_root",
            return_value=tmp_path,
        ),
        patch(
            "qgis_manager.cli.commands.package.get_dependencies",
            return_value=["requests"],
        ),
        patch(
            "qgis_manager.cli.commands.package.install_external_libs",
            return_value=True,
        ) as install,
        patch(
            "qgis_manager.cli.commands.package.create_plugin_package",
            return_value=output,
        ),
        redirect_stdout(io.StringIO()),
        redirect_stderr(io.StringIO()),
    ):
        exit_code = app.run(["package", str(tmp_path), "--trust"])

    assert exit_code == 0
    install.assert_called_once_with(tmp_path)
