"""Path exclusion policy shared by compile, clean, package and validation."""

from __future__ import annotations

from dataclasses import dataclass

_VCS_DIRS = frozenset({".git"})
_ENV_DIRS = frozenset({".venv", "env", "libs", "node_modules", "venv"})
_CACHE_DIRS = frozenset({"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"})
_BUILD_DIRS = frozenset({"build", "dist"})
_TOOL_DIRS = frozenset({".agent", ".ai-context", ".qgis-manage"})
_DEV_DIRS = frozenset(
    {"tests", "test", "docs", "scripts", "tools", "research", ".github"}
)

_PURPOSES = {
    "compile": _VCS_DIRS | _ENV_DIRS | _CACHE_DIRS | _BUILD_DIRS,
    "clean": _VCS_DIRS | _ENV_DIRS | _CACHE_DIRS | _BUILD_DIRS,
    "package": _VCS_DIRS | _ENV_DIRS | _CACHE_DIRS | _BUILD_DIRS | _TOOL_DIRS,
    "repository": _VCS_DIRS | _ENV_DIRS | _CACHE_DIRS | _BUILD_DIRS | _TOOL_DIRS,
}


@dataclass(frozen=True)
class PathPolicy:
    """Directories excluded for a particular filesystem operation."""

    excluded_dirs: frozenset[str]
    root_excluded_dirs: frozenset[str] = frozenset()
    cache_dirs: frozenset[str] = _CACHE_DIRS
    dev_dirs: frozenset[str] = _DEV_DIRS

    @classmethod
    def for_purpose(cls, purpose: str, include_dev: bool = False) -> PathPolicy:
        """Build a policy for ``compile``, ``clean``, ``package`` or ``repository``.

        Args:
            purpose: Operation requesting the policy.
            include_dev: Include development directories for package/repository.

        Returns:
            The immutable policy.

        Raises:
            ValueError: If ``purpose`` is unknown.
        """
        try:
            excluded = _PURPOSES[purpose]
        except KeyError as exc:
            raise ValueError(f"Unknown path-policy purpose: {purpose}") from exc
        root_excluded: set[str] = set()
        if purpose in {"package", "repository"}:
            root_excluded |= set(_TOOL_DIRS)
            if not include_dev:
                root_excluded |= set(_DEV_DIRS)
        return cls(
            excluded_dirs=frozenset(excluded),
            root_excluded_dirs=frozenset(root_excluded),
        )

    def excludes(self, name: str, *, at_root: bool = False) -> bool:
        """Return True when a directory name is excluded by this policy."""
        return name in self.excluded_dirs or (
            at_root and name in self.root_excluded_dirs
        )
