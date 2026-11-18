"""Tests for the shared path policy and deterministic walker."""

from __future__ import annotations

from pathlib import Path

import pytest

from qgis_manager.paths import PathPolicy, ProjectWalker


def _tree(root: Path) -> None:
    (root / "a.py").write_text("a", encoding="utf-8")
    (root / "z.py").write_text("z", encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_a.py").write_text("test", encoding="utf-8")
    (root / ".venv").mkdir()
    (root / ".venv" / "lib.py").write_text("lib", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "a.pyc").write_text("cache", encoding="utf-8")


def test_policy_purposes() -> None:
    compile_policy = PathPolicy.for_purpose("compile")
    assert compile_policy.excludes(".venv")
    assert compile_policy.excludes("__pycache__")
    assert not compile_policy.excludes("tests")

    package_policy = PathPolicy.for_purpose("package")
    assert package_policy.excludes("tests", at_root=True)
    assert package_policy.excludes(".agent", at_root=True)

    dev_policy = PathPolicy.for_purpose("package", include_dev=True)
    assert not dev_policy.excludes("tests", at_root=True)
    assert dev_policy.excludes(".agent", at_root=True)


def test_policy_rejects_unknown_purpose() -> None:
    with pytest.raises(ValueError, match="Unknown path-policy purpose"):
        PathPolicy.for_purpose("nope")


def test_walker_is_sorted_and_prunes(tmp_path: Path) -> None:
    _tree(tmp_path)
    walker = ProjectWalker(tmp_path, PathPolicy.for_purpose("compile"))
    files = [path.relative_to(tmp_path).as_posix() for path in walker.files()]
    assert files == ["a.py", "z.py", "tests/test_a.py"]


def test_walker_package_excludes_dev(tmp_path: Path) -> None:
    _tree(tmp_path)
    walker = ProjectWalker(tmp_path, PathPolicy.for_purpose("package"))
    files = [path.relative_to(tmp_path).as_posix() for path in walker.files()]
    assert files == ["a.py", "z.py"]


def test_walker_clean_exposes_cache_dirs(tmp_path: Path) -> None:
    _tree(tmp_path)
    walker = ProjectWalker(
        tmp_path,
        PathPolicy.for_purpose("clean"),
        include_cache_dirs=True,
    )
    entries = list(walker.entries())
    assert "__pycache__" in entries[0].cache_dirs
    assert "__pycache__" not in entries[0].dirnames
    assert all("__pycache__" not in entry.root.parts for entry in entries[1:])


def test_walker_skips_symlinks_and_extra_rules(tmp_path: Path) -> None:
    _tree(tmp_path)
    (tmp_path / "link.py").symlink_to(tmp_path / "a.py")
    walker = ProjectWalker(
        tmp_path,
        PathPolicy.for_purpose("compile"),
        extra_exclude=lambda path: path.name == "z.py",
    )
    files = [path.name for path in walker.files()]
    assert "link.py" not in files
    assert "z.py" not in files


def test_root_items_are_sorted(tmp_path: Path) -> None:
    _tree(tmp_path)
    walker = ProjectWalker(tmp_path, PathPolicy.for_purpose("package"))
    assert [path.name for path in walker.root_items()] == ["a.py", "z.py"]
