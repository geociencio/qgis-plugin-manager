"""End-to-end tests for the deploy and package CLI commands.

These tests invoke the real CLI in a subprocess against temporary plugin projects;
they intentionally avoid mocks so file-system effects are verified directly.
"""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI_CODE = "from qgis_manager.cli import main; main()"


def _run_cli(
    project: Path,
    *args: str,
    stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Invoke the CLI in a subprocess with an isolated home directory."""
    home = project.parent / ".home"
    home.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["PYTHONIOENCODING"] = "utf-8"
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(ROOT / "src"), existing_pythonpath) if part
    )
    return subprocess.run(
        [sys.executable, "-c", CLI_CODE, *args],
        cwd=project,
        env=env,
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )


def _make_project(
    root: Path,
    *,
    name: str = "Demo Plugin",
    version: str = "1.0.0",
    include_repo: bool = True,
) -> Path:
    """Create a minimal QGIS plugin project with files and ignored artifacts."""
    project = root / "project"
    project.mkdir()
    fields = [
        "[general]",
        f"name={name}",
        "description=Demo plugin for end-to-end tests",
        f"version={version}",
        "qgisMinimumVersion=3.0",
        "author=Tester",
        "email=test@example.com",
    ]
    if include_repo:
        fields += [
            "about=Demo plugin for end-to-end tests",
            "homepage=https://example.com/demo",
            "repository=https://example.com/demo.git",
            "tracker=https://example.com/demo/issues",
            "tags=demo,test",
        ]
    (project / "metadata.txt").write_text("\n".join(fields) + "\n", encoding="utf-8")
    (project / "__init__.py").write_text(
        "def classFactory(iface):\n    return None\n", encoding="utf-8"
    )
    (project / "core").mkdir()
    (project / "core" / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
    (project / ".git").mkdir()
    (project / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (project / "dist").mkdir()
    (project / "dist" / "old.zip").write_text("old", encoding="utf-8")
    return project


def _deploy(
    project: Path,
    target: Path,
    *extra: str,
    stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run_cli(
        project,
        "deploy",
        str(project),
        "--profile",
        str(target),
        "--no-compile",
        *extra,
        stdin=stdin,
    )


def test_deploy_copies_plugin_and_ignores_dev_files(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    target = tmp_path / "plugins"

    result = _deploy(project, target, "--no-backup")

    assert result.returncode == 0, result.stderr
    deployed = target / "demo_plugin"
    assert (deployed / "metadata.txt").is_file()
    assert (deployed / "__init__.py").is_file()
    assert (deployed / "core" / "helper.py").is_file()
    assert not (deployed / ".git").exists()
    assert not (deployed / "dist").exists()
    assert not list(target.glob("demo_plugin.bak.*"))


def test_redeploy_creates_backup_and_removes_stale_files(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    target = tmp_path / "plugins"
    first = _deploy(project, target)
    assert first.returncode == 0, first.stderr

    deployed = target / "demo_plugin"
    (deployed / "stale.txt").write_text("stale", encoding="utf-8")
    (project / "__init__.py").write_text(
        "def classFactory(iface):\n    return 'v2'\n", encoding="utf-8"
    )
    second = _deploy(project, target)

    assert second.returncode == 0, second.stderr
    assert (deployed / "__init__.py").read_text(encoding="utf-8") == (
        "def classFactory(iface):\n    return 'v2'\n"
    )
    assert not (deployed / "stale.txt").exists()
    backups = list(target.glob("demo_plugin.bak.*"))
    assert len(backups) == 1
    assert (backups[0] / "stale.txt").read_text(encoding="utf-8") == "stale"


def test_purge_backups_removes_existing_backups(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    target = tmp_path / "plugins"
    assert _deploy(project, target).returncode == 0
    (target / "demo_plugin" / "stale.txt").write_text("stale", encoding="utf-8")
    assert _deploy(project, target).returncode == 0
    assert list(target.glob("demo_plugin.bak.*"))

    result = _deploy(project, target, "--purge-backups", "--no-backup", stdin="y\ny\n")

    assert result.returncode == 0, result.stderr
    assert not list(target.glob("demo_plugin.bak.*"))
    assert (target / "demo_plugin" / "metadata.txt").is_file()


def test_deploy_rejects_empty_plugin_name(tmp_path: Path) -> None:
    project = _make_project(tmp_path, name="")
    target = tmp_path / "plugins"

    result = _deploy(project, target, "--no-backup")

    assert result.returncode == 1
    assert "Error" in result.stderr
    assert not target.exists()


def test_package_creates_zip_and_checksum(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    output = tmp_path / "packages"

    result = _run_cli(project, "package", str(project), "--output", str(output))

    assert result.returncode == 0, result.stderr
    zip_path = output / "demo_plugin.1.0.0.zip"
    checksum = output / "demo_plugin.1.0.0.zip.sha256"
    assert zip_path.is_file()
    assert checksum.is_file()
    assert "demo_plugin.1.0.0.zip" in checksum.read_text(encoding="utf-8")
    with zipfile.ZipFile(zip_path) as archive:
        names = {name.replace("\\", "/") for name in archive.namelist()}
        assert "demo_plugin/metadata.txt" in names
        assert "demo_plugin/__init__.py" in names
        assert "demo_plugin/core/helper.py" in names
        assert not any(
            ".git" in name or name.startswith("demo_plugin/dist") for name in names
        )
        assert archive.read("demo_plugin/metadata.txt").decode() == (
            project / "metadata.txt"
        ).read_text(encoding="utf-8")


def test_package_stamp_does_not_modify_source_metadata(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    output = tmp_path / "packages"
    original = (project / "metadata.txt").read_text(encoding="utf-8")

    result = _run_cli(
        project, "package", str(project), "--output", str(output), "--stamp"
    )

    assert result.returncode == 0, result.stderr
    assert (project / "metadata.txt").read_text(encoding="utf-8") == original
    with zipfile.ZipFile(output / "demo_plugin.1.0.0.zip") as archive:
        packaged = archive.read("demo_plugin/metadata.txt").decode()
    assert "dateTime=" in packaged
    assert packaged != original


def test_package_sync_version_uses_pyproject(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    (project / "pyproject.toml").write_text(
        '[project]\nname = "demo_plugin"\nversion = "2.3.4"\n',
        encoding="utf-8",
    )
    output = tmp_path / "packages"

    result = _run_cli(
        project,
        "package",
        str(project),
        "--output",
        str(output),
        "--sync-version",
    )

    assert result.returncode == 0, result.stderr
    assert (output / "demo_plugin.2.3.4.zip").is_file()
    assert "version=2.3.4" in (project / "metadata.txt").read_text(encoding="utf-8")


def test_package_repo_check_fails_without_repository_metadata(tmp_path: Path) -> None:
    project = _make_project(tmp_path, include_repo=False)
    output = tmp_path / "packages"

    result = _run_cli(
        project, "package", str(project), "--output", str(output), "--repo-check"
    )

    assert result.returncode == 1
    assert "compliance failed" in result.stdout.lower()
    assert not list(output.glob("*.zip"))


def _symlink_or_skip(link: Path, target: Path, *, directory: bool) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError):
        import pytest

        pytest.skip("symlinks are not available on this platform")


def test_deploy_skips_source_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("SECRET = 1\n", encoding="utf-8")
    project = _make_project(tmp_path)
    _symlink_or_skip(project / "linked.py", outside / "secret.py", directory=False)
    _symlink_or_skip(project / "linked_dir", outside, directory=True)
    target = tmp_path / "plugins"

    result = _deploy(project, target, "--no-backup")

    assert result.returncode == 0, result.stderr
    deployed = target / "demo_plugin"
    assert not (deployed / "linked.py").exists()
    assert not (deployed / "linked_dir").exists()
    assert (outside / "secret.py").is_file()


def test_package_excludes_nested_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("SECRET = 1\n", encoding="utf-8")
    project = _make_project(tmp_path)
    _symlink_or_skip(
        project / "core" / "linked.py", outside / "secret.py", directory=False
    )
    _symlink_or_skip(project / "core" / "linked_dir", outside, directory=True)
    output = tmp_path / "packages"

    result = _run_cli(project, "package", str(project), "--output", str(output))

    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output / "demo_plugin.1.0.0.zip") as archive:
        names = {name.replace("\\", "/") for name in archive.namelist()}
    assert not any("linked" in name for name in names)


def test_deploy_refuses_symlink_target(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    target = tmp_path / "plugins"
    target.mkdir()
    _symlink_or_skip(target / "demo_plugin", outside, directory=True)
    project = _make_project(tmp_path)

    result = _deploy(project, target, "--no-backup")

    assert result.returncode == 1
    assert not (outside / "metadata.txt").exists()


def test_deploy_skips_hooks_without_trust(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    (project / "plugin_hooks.py").write_text(
        "from pathlib import Path\n"
        "\n"
        "def pre_deploy(context):\n"
        "    Path(context['project_root'], 'hook-ran.txt').write_text('yes')\n",
        encoding="utf-8",
    )
    target = tmp_path / "plugins"

    result = _deploy(project, target, "--no-backup")

    assert result.returncode == 0, result.stderr
    assert "Skipping pre-deploy hooks" in result.stderr
    assert not (project / "hook-ran.txt").exists()


def test_deploy_runs_hooks_with_trust(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    (project / "plugin_hooks.py").write_text(
        "from pathlib import Path\n"
        "\n"
        "def pre_deploy(context):\n"
        "    Path(context['project_root'], 'hook-ran.txt').write_text('yes')\n",
        encoding="utf-8",
    )
    target = tmp_path / "plugins"

    result = _deploy(project, target, "--no-backup", "--trust")

    assert result.returncode == 0, result.stderr
    assert (project / "hook-ran.txt").read_text(encoding="utf-8") == "yes"
    assert (target / "demo_plugin" / "hook-ran.txt").is_file()


def test_package_requires_trust_for_dependencies(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    (project / "pyproject.toml").write_text(
        '[tool.qgis-manager]\ndependencies = ["requests"]\n',
        encoding="utf-8",
    )
    output = tmp_path / "packages"

    result = _run_cli(project, "package", str(project), "--output", str(output))

    assert result.returncode == 1
    assert "--trust" in result.stderr
    assert not list(output.glob("*.zip"))


def test_package_rejects_unsafe_version(tmp_path: Path) -> None:
    project = _make_project(tmp_path, version="../escape")
    output = tmp_path / "packages"

    result = _run_cli(project, "package", str(project), "--output", str(output))

    assert result.returncode == 1
    assert not list(output.glob("*.zip"))


def test_redeploy_replaces_destination_symlink(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    target = tmp_path / "plugins"
    assert _deploy(project, target).returncode == 0
    outside = tmp_path / "outside.py"
    outside.write_text("SECRET = 1\n", encoding="utf-8")
    deployed_helper = target / "demo_plugin" / "core" / "helper.py"
    deployed_helper.unlink()
    _symlink_or_skip(deployed_helper, outside, directory=False)
    (project / "core" / "helper.py").write_text("VALUE = 2\n", encoding="utf-8")

    result = _deploy(project, target)

    assert result.returncode == 0, result.stderr
    assert not deployed_helper.is_symlink()
    assert deployed_helper.read_text(encoding="utf-8") == "VALUE = 2\n"
    assert outside.read_text(encoding="utf-8") == "SECRET = 1\n"
