# B1 — PathPolicy and ProjectWalker

**Status**: Done
**Implementation commit**: `587071f refactor(paths): centralize project walking`
**State commit**: `76b9572 chore(agent): record B1 path refactor`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Replace five independent tree walkers with one deterministic, symlink-safe
walker and one exclusion policy, without changing package/deploy/clean behavior.

## Procedure

1. Create `src/qgis_manager/paths/policy.py` with `PathPolicy.for_purpose` for
   `compile`, `clean`, `package`, and `repository`.
2. Create `src/qgis_manager/paths/walker.py` with `ProjectWalker`:
   - sorted directory/file traversal;
   - no symlink descent;
   - extra exclusion predicate;
   - `include_cache_dirs` mode for `clean`;
   - `root_items()` for discovery.
3. Migrate `core/compile.py` `_iter_compile_sources`.
4. Migrate `core/package.py` `_iter_package_files` and pass the project root so
   root-only dev/tools exclusions work for nested root items.
5. Migrate `core/cleanup.py` cache/files/compiled-output walks.
6. Migrate `validation/repository.py` prohibited-binary walk.
7. Migrate `discovery.py` root entries.
8. Remove duplicated `_COMPILE_EXCLUDED_DIRS`, `_EXCLUDED_DIRS`, `_CACHE_DIRS`.
9. Add `tests/test_paths_walker.py` for purposes, ordering, symlinks, caches,
   extra rules and root items.

## Files

- `src/qgis_manager/paths/__init__.py`
- `src/qgis_manager/paths/policy.py`
- `src/qgis_manager/paths/walker.py`
- `src/qgis_manager/core/{compile,package,cleanup}.py`
- `src/qgis_manager/validation/repository.py`
- `src/qgis_manager/discovery.py`
- `tests/test_paths_walker.py`

## Acceptance

- Only `paths/walker.py` calls `os.walk`.
- Root dev/tool directories are excluded; nested `gui/tools` is preserved.
- Package and clean tests remain green.
- C901 = 0.

## Evidence

- `rg "os.walk" src/qgis_manager` returns only the walker.
- 441 tests passed at this stage (B1 + existing suite).
