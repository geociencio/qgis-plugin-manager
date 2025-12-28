from pathlib import Path

from qgis_manager.config import Settings, load_config, load_project_config


def test_settings_defaults():
    settings = Settings()
    assert settings.profile == "default"
    assert settings.backup is True
    assert settings.auto_compile is True
    assert settings.hooks == {}


def test_load_project_config(tmp_path: Path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.qgis-manager]
profile = "prod"
backup = false
auto_compile = false
[tool.qgis-manager.hooks]
pre-deploy = "echo 1"
""",
        encoding="utf-8",
    )

    settings = Settings()
    settings = load_project_config(tmp_path, settings)

    assert settings.profile == "prod"
    assert settings.backup is False
    assert settings.auto_compile is False
    assert settings.hooks["pre-deploy"] == "echo 1"


def test_load_config_no_file(mocker):
    mocker.patch("pathlib.Path.home", return_value=Path("/nonexistent"))
    settings = load_config()
    assert settings.profile == "default"
