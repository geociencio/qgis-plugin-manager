"""Tests for the deploy content manifest."""

import json
from pathlib import Path
from unittest.mock import patch

from qgis_manager.core import create_plugin_package, deploy_plugin
from qgis_manager.core import manifest as manifest_module


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    (project / "metadata.txt").write_text(
        "[general]\nname=Demo Plugin\nversion=1.0.0\n", encoding="utf-8"
    )
    (project / "plugin.py").write_text("VALUE = 1\n", encoding="utf-8")
    return project


def test_second_deploy_uses_manifest_without_hashing(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    deploy_plugin(project, dest_dir=target)
    manifest_path = project / ".qgis-manage" / "deploy-manifest.json"
    assert manifest_path.is_file()

    calls = []
    original = manifest_module._sha256

    def counting(path: Path) -> str:
        calls.append(path)
        return original(path)

    with patch("qgis_manager.core.manifest._sha256", side_effect=counting):
        deploy_plugin(project, dest_dir=target)

    assert calls == []


def test_manifest_detects_same_size_rewrite(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    deploy_plugin(project, dest_dir=target)

    (project / "plugin.py").write_text("VALUE = 2\n", encoding="utf-8")
    deploy_plugin(project, dest_dir=target)

    deployed = target / "demo_plugin" / "plugin.py"
    assert deployed.read_text(encoding="utf-8") == "VALUE = 2\n"


def test_corrupt_manifest_falls_back_to_full_scan(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    deploy_plugin(project, dest_dir=target)
    manifest_path = project / ".qgis-manage" / "deploy-manifest.json"
    manifest_path.write_text("{not-json", encoding="utf-8")

    deploy_plugin(project, dest_dir=target)

    assert json.loads(manifest_path.read_text(encoding="utf-8"))["version"] == 1


def test_failed_sync_does_not_save_manifest(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    target.mkdir()

    with patch(
        "qgis_manager.core.deploy.sync_directory",
        side_effect=RuntimeError("sync failed"),
    ):
        try:
            deploy_plugin(project, dest_dir=target)
        except RuntimeError:
            pass

    assert not (project / ".qgis-manage" / "deploy-manifest.json").exists()


def test_manifest_is_excluded_from_packages(tmp_path: Path) -> None:
    project = _project(tmp_path)
    (project / ".qgis-manage").mkdir()
    (project / ".qgis-manage" / "deploy-manifest.json").write_text("{}")

    zip_path = create_plugin_package(project, output_dir=tmp_path / "out")

    import zipfile

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    assert not any(".qgis-manage" in name for name in names)


def test_manifest_ignores_unknown_schema(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    manifest_path = project / ".qgis-manage" / "deploy-manifest.json"
    manifest_path.parent.mkdir()
    manifest_path.write_text('{"version": 99, "targets": {}}', encoding="utf-8")

    manifest = manifest_module.DeployManifest(project, target)
    assert manifest.entries == {}


def test_manifest_save_failure_is_non_fatal(tmp_path: Path) -> None:
    project = _project(tmp_path)
    manifest = manifest_module.DeployManifest(project, tmp_path / "plugins")
    with patch(
        "qgis_manager.core.manifest.write_text_atomic",
        side_effect=OSError("read-only"),
    ):
        manifest.save()


def test_manifest_source_outside_root_needs_copy(tmp_path: Path) -> None:
    project = _project(tmp_path)
    target = tmp_path / "plugins"
    target.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("x", encoding="utf-8")
    manifest = manifest_module.DeployManifest(project, target)
    assert manifest.needs_copy(outside, target / "outside.py") is True


def test_manifest_record_skips_missing_target(tmp_path: Path) -> None:
    project = _project(tmp_path)
    manifest = manifest_module.DeployManifest(project, tmp_path / "plugins")
    manifest.record(project / "plugin.py", tmp_path / "missing.py")
    assert manifest.entries == {}
