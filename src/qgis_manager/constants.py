
"""
Constants and default values for QGIS Plugin Manager.
"""

# Default patterns to exclude from package building and deployment
# These are applied to both the file discovery and the packaging process.
DEFAULT_EXCLUDE_PATTERNS = {
    # Python
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.egg-info",
    ".venv",
    "venv",
    "env",

    # Version Control
    ".git",
    ".gitignore",
    ".gitattributes",

    # IDEs / Editors
    ".vscode",
    ".idea",
    ".vs",
    ".settings",
    ".project",
    ".classpath",
    "*.sublime-project",
    "*.sublime-workspace",
    ".DS_Store",

    # Tools / Linters
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".pre-commit-config.yaml",

    # Package Managers
    "poetry.lock",
    "uv.lock",
    "Pipfile",
    "Pipfile.lock",

    # Build Artifacts
    "build",
    "dist",
    "*.bak*",
    "*.log",

    # QGIS Manager internals
    ".agent",
    ".ai-context",
    "debug_package_list.py", # Exclude debug scripts if present
    "analysis_results",
    "generator_export",
}

# Directories that are considered "dev-only" and should be excluded
# unless specifically requested (e.g. for a dev build).
# These are only excluded at the root level by default in strict mode.
DEV_DIRECTORIES = {
    "tests",
    "test",
    "docs",
    "scripts",
    "tools",
    "research",
    ".github",
}
