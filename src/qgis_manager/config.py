from dataclasses import dataclass, field
from pathlib import Path

from .toml_utils import load_toml


@dataclass
class Settings:
    """Store application settings."""

    profile: str = "default"
    qgis_version: int = 3
    backup: bool = True
    max_backups: int = 3
    auto_compile: bool = True
    hooks: dict[str, str] = field(default_factory=dict)


def load_config() -> Settings:
    """Load configuration from ~/.config/qgis-manager/config.toml."""
    settings = Settings()

    config_path = Path.home() / ".config" / "qgis-manager" / "config.toml"
    if config_path.exists():
        data = load_toml(config_path)
        defaults = data.get("defaults", {})
        settings.profile = defaults.get("profile", settings.profile)
        settings.qgis_version = defaults.get("qgis_version", settings.qgis_version)
        settings.backup = defaults.get("backup", settings.backup)
        settings.max_backups = defaults.get("max_backups", settings.max_backups)
        settings.auto_compile = defaults.get("auto_compile", settings.auto_compile)

    return settings


def load_project_config(project_root: Path, base_settings: Settings) -> Settings:
    """Load project-specific overrides from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        data = load_toml(pyproject_path)
        tool_config = data.get("tool", {}).get("qgis-manager", {})

        # Overrides from pyproject.toml
        base_settings.profile = tool_config.get("profile", base_settings.profile)
        base_settings.qgis_version = tool_config.get(
            "qgis_version", base_settings.qgis_version
        )
        base_settings.backup = tool_config.get("backup", base_settings.backup)
        base_settings.max_backups = tool_config.get(
            "max_backups", base_settings.max_backups
        )
        base_settings.auto_compile = tool_config.get(
            "auto_compile", base_settings.auto_compile
        )
        base_settings.hooks = tool_config.get("hooks", base_settings.hooks)

    return base_settings
