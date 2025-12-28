from pathlib import Path

from click.testing import CliRunner

from qgis_manager.cli import main


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "deploy" in result.output
    assert "compile" in result.output
    assert "clean" in result.output
    assert "package" in result.output
    assert "validate" in result.output
    assert "init" in result.output


def test_cli_init_success(tmp_path: Path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            main,
            [
                "init",
                "Test Plugin",
                "--author",
                "Author",
                "--email",
                "email@example.com",
            ],
        )
        assert result.exit_code == 0
        assert "Plugin 'Test Plugin' initialized successfully" in result.output
        assert Path("test_plugin/metadata.txt").exists()


def test_cli_validate_no_project(tmp_path: Path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["validate"])
        assert result.exit_code != 0
        assert "Error:" in result.output


def test_cli_package_no_project(tmp_path: Path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(main, ["package"])
        assert result.exit_code != 0
        assert "Error:" in result.output
