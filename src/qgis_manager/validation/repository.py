"""Official QGIS plugin repository compliance rules."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..ignore import IgnoreMatcher
from .result import ValidationResult

_PROHIBITED_BINARIES = (".so", ".dll", ".exe", ".dylib", ".pyd", ".pyc", ".pyo")
_LICENSE_VARIANTS = ("LICENSE.txt", "COPYING", "LICENSE.md")


def _validate_required_files(project_root: Path, errors: list[str]) -> None:
    if not (project_root / "metadata.txt").exists():
        errors.append("Critical file missing for official repository: 'metadata.txt'")


def _find_prohibited_binaries(project_root: Path) -> list[str]:
    matcher = IgnoreMatcher(project_root, include_dev=False)
    found: list[str] = []
    for extension in _PROHIBITED_BINARIES:
        for path in project_root.rglob(f"*{extension}"):
            if path.is_symlink() or not path.is_file():
                continue
            if not matcher.should_exclude(path):
                found.append(str(path.relative_to(project_root)))
    return found


def _validate_license(project_root: Path, errors: list[str]) -> None:
    if (project_root / "LICENSE").exists():
        return
    variant = next(
        (name for name in _LICENSE_VARIANTS if (project_root / name).exists()), None
    )
    if variant:
        errors.append(
            "License file must be named exactly 'LICENSE' "
            f"(no extension). Found '{variant}'."
        )
    else:
        errors.append("Critical file missing for official repository: 'LICENSE'")


def _validate_repository_fields(
    metadata: dict[str, Any] | None, errors: list[str]
) -> None:
    if metadata is None:
        return
    for field in ("about", "repository"):
        if not metadata.get(field):
            errors.append(f"Missing required field for official repository: '{field}'")


def validate_official_compliance(
    project_root: Path, metadata: dict[str, Any] | None = None
) -> ValidationResult:
    """Check if the project complies with official QGIS repository rules."""
    errors: list[str] = []
    _validate_required_files(project_root, errors)
    binaries = _find_prohibited_binaries(project_root)
    if binaries:
        errors.append(
            f"Official repository prohibits binaries. Found: {', '.join(binaries)}"
        )
    _validate_license(project_root, errors)
    _validate_repository_fields(metadata, errors)
    return ValidationResult(is_valid=not errors, errors=errors, warnings=[])
