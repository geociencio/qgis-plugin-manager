import sys
from dataclasses import dataclass, field
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@dataclass
class Settings:
    """Store application settings."""

    profile: str = "default"
    backup: bool = True
    auto_compile: bool = True
    hooks: dict[str, str] = field(default_factory=dict)


def load_config() -> Settings:
    """Load configuration from ~/.config/qgis-manager/config.toml and pyproject.toml."""
    settings = Settings()

    # 1. Load from ~/.config/qgis-manager/config.toml
    config_path = Path.home() / ".config" / "qgis-manager" / "config.toml"
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                defaults = data.get("defaults", {})
                settings.profile = defaults.get("profile", settings.profile)
                settings.backup = defaults.get("backup", settings.backup)
                settings.auto_compile = defaults.get(
                    "auto_compile", settings.auto_compile
                )
        except Exception:
            # Fallback to defaults on corrupt config
            pass

    # 2. Load from pyproject.toml in project root (if exists)
    # This logic might need to find the project root first, so it's typically called
    # with a known root or we search upwards.
    return settings


def load_project_config(project_root: Path, base_settings: Settings) -> Settings:
    """Load project-specific overrides from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                tool_config = data.get("tool", {}).get("qgis-manager", {})

                # Overrides from pyproject.toml
                base_settings.profile = tool_config.get(
                    "profile", base_settings.profile
                )
                base_settings.backup = tool_config.get("backup", base_settings.backup)
                base_settings.auto_compile = tool_config.get(
                    "auto_compile", base_settings.auto_compile
                )
                base_settings.hooks = tool_config.get("hooks", base_settings.hooks)
        except Exception:
            pass
    return base_settings
