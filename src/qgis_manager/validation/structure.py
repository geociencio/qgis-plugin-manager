"""Physical project-structure validation."""

from pathlib import Path
from typing import Any

from .result import ValidationResult


def validate_project_structure(
    project_root: Path, metadata: dict[str, Any]
) -> ValidationResult:
    """Validate the physical structure of the plugin project.

    Args:
        project_root: Root directory of the project.
        metadata: Plugin metadata dictionary.

    Returns:
        ValidationResult with validation status and messages.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Essential files
    init_py = project_root / "__init__.py"
    if not init_py.exists():
        errors.append("Critical file missing: '__init__.py'")
    else:
        # Check for classFactory
        try:
            content = init_py.read_text(encoding="utf-8")
            if "def classFactory" not in content:
                errors.append(
                    "Critical function missing in '__init__.py': 'def classFactory'"
                )
        except Exception:
            errors.append("Could not read '__init__.py'")

    # 2. Icon validation
    icon_name = metadata.get("icon", "icon.png")
    icon_path = project_root / icon_name
    if not icon_path.exists():
        if icon_name == "icon.png":
            warnings.append("Recommended file missing: 'icon.png' (standard icon)")
        else:
            errors.append(f"Specified icon file does not exist: '{icon_name}'")

    # 3. Code consistency (Basic check)
    # If the user specifies a class name, it's harder to check without parsing Python,
    # but we can check if there's at least some .py files besides __init__.py
    py_files = list(project_root.glob("*.py"))
    if len(py_files) <= 1:  # Only __init__.py or none
        warnings.append(
            "Project contains very few Python files. Is the plugin logic implemented?"
        )

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
