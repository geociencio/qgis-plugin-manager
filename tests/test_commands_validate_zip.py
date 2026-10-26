"""Tests for validate --zip and package post-build artifact checks."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.validation.artifact import ArtifactError

from .command_test_base import _CommandTestBase


class TestValidateZip(_CommandTestBase):
    @patch("qgis_manager.cli.commands.validate.validate_artifact")
    def test_validate_zip_passes(self, mock_validate):
        mock_validate.return_value = Mock(
            is_valid=True,
            warnings=[],
            errors=[],
            to_dict=lambda: {"root": "demo", "checks": []},
        )
        exit_code, output, _ = self._invoke(["validate", "--zip", "demo.zip"])
        self.assertEqual(exit_code, 0)
        self.assertIn("passed", output)

    @patch("qgis_manager.cli.commands.validate.validate_artifact")
    def test_validate_zip_json_failure(self, mock_validate):
        mock_validate.return_value = Mock(
            is_valid=False,
            warnings=["ARTIFACT_README: missing"],
            errors=["ARTIFACT_LICENSE: missing"],
            to_dict=lambda: {"root": "demo", "checks": []},
        )
        exit_code, output, _ = self._invoke(["validate", "--zip", "demo.zip", "--json"])
        self.assertEqual(exit_code, 1)
        payload = json.loads(output)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["command"], "validate")

    @patch(
        "qgis_manager.cli.commands.validate.validate_artifact",
        side_effect=ArtifactError("bad zip"),
    )
    def test_validate_zip_invalid_input_exit_2(self, _mock_validate):
        exit_code, _, stderr = self._invoke(["validate", "--zip", "bad.zip"])
        self.assertEqual(exit_code, 2)
        self.assertIn("bad zip", stderr)

    def test_validate_zip_conflicts_with_project_path(self):
        exit_code, _, stderr = self._invoke(
            ["validate", "project", "--zip", "demo.zip"]
        )
        self.assertEqual(exit_code, 2)
        self.assertIn("mutually exclusive", stderr)


class TestPackageArtifactAudit(_CommandTestBase):
    @patch(
        "qgis_manager.cli.commands.package.PackageCommand._check_compliance",
        return_value=True,
    )
    @patch("qgis_manager.cli.commands.package.validate_artifact")
    @patch("qgis_manager.cli.commands.package.install_external_libs")
    @patch("qgis_manager.cli.commands.package.create_plugin_package")
    @patch("qgis_manager.cli.base.find_project_root")
    def test_package_fails_when_built_zip_is_invalid(
        self,
        mock_find,
        mock_package,
        _mock_install,
        mock_validate,
        _mock_compliance,
    ):
        root = Path(tempfile.mkdtemp())
        (root / "metadata.txt").write_text(
            "[general]\nname=Demo\nversion=1.0.0\n", encoding="utf-8"
        )
        mock_find.return_value = root
        mock_package.return_value = root / "dist" / "demo.zip"
        mock_validate.return_value = Mock(
            is_valid=False,
            warnings=[],
            errors=["ARTIFACT_LICENSE: missing"],
        )

        exit_code, _, stderr = self._invoke(["package", "--repo-check"])

        self.assertEqual(exit_code, 1)
        self.assertIn("built artifact", stderr.lower())
