#!/usr/bin/env python3
"""Verify that built distributions contain only runtime/tool files."""

from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

_SDIST_FILES = {
    "pyproject.toml",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "PKG-INFO",
    ".gitignore",  # Hatch force-includes VCS metadata
}


def _check_sdist(path: Path) -> list[str]:
    errors: list[str] = []
    with tarfile.open(path) as archive:
        for member in archive.getnames():
            parts = member.split("/", 1)
            relative = parts[1] if len(parts) == 2 else ""
            if not relative or relative in _SDIST_FILES:
                continue
            if relative.startswith("src/qgis_manager/"):
                continue
            errors.append(f"{path.name}: unexpected {relative}")
    return errors


def _check_wheel(path: Path) -> list[str]:
    errors: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.startswith("qgis_manager/"):
                continue
            if name.startswith("qgis_manage-") and ".dist-info/" in name:
                continue
            errors.append(f"{path.name}: unexpected {name}")
    return errors


def main() -> int:
    dist = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    sdists = sorted(dist.glob("*.tar.gz"))
    wheels = sorted(dist.glob("*.whl"))
    if not sdists or not wheels:
        print("Missing wheel or sdist", file=sys.stderr)
        return 1
    errors: list[str] = []
    for path in sdists:
        errors.extend(_check_sdist(path))
    for path in wheels:
        errors.extend(_check_wheel(path))
    if errors:
        print("Distribution contains non-tool files:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print("Distribution contents: wheel and sdist contain only tool files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
