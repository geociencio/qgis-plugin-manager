"""Deterministic, symlink-safe project walking with one exclusion policy."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from .policy import PathPolicy


@dataclass
class WalkEntry:
    """One directory yielded by :class:`ProjectWalker`."""

    root: Path
    dirnames: list[str]
    filenames: list[str]
    cache_dirs: list[str]


class ProjectWalker:
    """Walk a project tree without entering excluded or symlinked directories.

    Args:
        root: Directory to walk.
        policy: Exclusion policy for the operation.
        extra_exclude: Optional predicate for project-specific rules.
        include_cache_dirs: Yield cache directories separately instead of
            descending into them. Used by ``clean`` so it can remove them.
    """

    def __init__(
        self,
        root: Path,
        policy: PathPolicy,
        extra_exclude: Callable[[Path], bool] | None = None,
        include_cache_dirs: bool = False,
        project_root: Path | None = None,
    ) -> None:
        self.root = root
        self.project_root = project_root or root
        self.policy = policy
        self.extra_exclude = extra_exclude
        self.include_cache_dirs = include_cache_dirs

    def _excluded(self, path: Path) -> bool:
        return bool(self.extra_exclude and self.extra_exclude(path))

    def entries(self) -> Iterator[WalkEntry]:
        """Yield sorted directory entries, pruning excluded directories."""
        for current, dirnames, filenames in os.walk(
            self.root, topdown=True, followlinks=False
        ):
            root = Path(current)
            cache_dirs: list[str] = []
            allowed: list[str] = []
            for name in sorted(dirnames):
                path = root / name
                if path.is_symlink():
                    continue
                if self.include_cache_dirs and name in self.policy.cache_dirs:
                    cache_dirs.append(name)
                    continue
                if self.policy.excludes(
                    name, at_root=root == self.project_root
                ) or self._excluded(path):
                    continue
                allowed.append(name)
            dirnames[:] = allowed
            visible_files = [
                name
                for name in sorted(filenames)
                if not (root / name).is_symlink() and not self._excluded(root / name)
            ]
            yield WalkEntry(root, allowed, visible_files, cache_dirs)

    def files(self) -> Iterator[Path]:
        """Yield files in deterministic order."""
        for entry in self.entries():
            for name in entry.filenames:
                yield entry.root / name

    def root_items(self) -> Iterator[Path]:
        """Yield sorted root entries, applying the policy and extra rules."""
        for path in sorted(self.root.iterdir()):
            if path.is_symlink() or self.policy.excludes(
                path.name, at_root=self.root == self.project_root
            ):
                continue
            if self._excluded(path):
                continue
            yield path
