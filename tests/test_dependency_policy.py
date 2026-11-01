"""Enforce the zero-runtime-dependency policy."""

from __future__ import annotations

import ast
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "qgis_manager"


def test_project_has_no_runtime_dependencies() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["project"]["dependencies"] == []


def test_runtime_imports_are_stdlib_or_local() -> None:
    local = {"qgis_manager"}
    allowed = set(sys.stdlib_module_names) | local
    offenders: list[str] = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    continue
                names = [node.module.split(".")[0]] if node.module else []
            else:
                continue
            for name in names:
                if name and name not in allowed:
                    offenders.append(f"{path.relative_to(ROOT)}: {name}")
    assert offenders == [], "Third-party runtime imports: " + ", ".join(offenders)
