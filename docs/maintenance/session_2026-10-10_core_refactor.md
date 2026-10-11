# Session 2026-10-10 — `core.py` Split & Complexity Reduction

**Topic**: `core_refactor`
**Agent role**: @architect (implementation) + @qa_engineer (verification)
**Result**: ✅ COMPLETE — `core.py` (840 lines, MI A 23.75) is now a 6-module
`qgis_manager.core` package with every function at CC ≤ 8 and all gates green.
**Plan**: `docs/plans/core_refactoring_plan.md`.

---

## Objective

Break the monolithic `src/qgis_manager/core.py` into cohesive submodules and lower
the cyclomatic complexity of its 6 hotspots, without changing behaviour. It was the
only module violating the project thresholds (`module_size_limit = 400`,
`max_cc = 10`) and the lowest Maintainability Index in the repo.

---

## What was done

### Phase 1 — Package split (behaviour-preserving)
- New package `src/qgis_manager/core/`:
  - `platform.py` — `get_qgis_plugin_dir`
  - `deploy.py` — `uninstall_plugin`, `rotate_backups`, `sync_directory`, `deploy_plugin`
  - `compile.py` — `compile_docs`, `compile_qt_resources`, `compile_ui_files`,
    `count_compile_steps`, tool/patch helpers
  - `package.py` — `stamp_metadata_text`, `create_plugin_package`, `get_git_info`, `is_prerelease`
  - `cleanup.py` — `clean_artifacts`
  - `scaffold.py` — `init_plugin_project`
  - `__init__.py` — re-exports the 20 public symbols (import compatibility).
- Fixed relative imports (`..discovery`, `..ignore`, `..templating`) and the
  `templates/` path in `scaffold.py` (`parent.parent`).
- Removed `src/qgis_manager/core.py`.

### Phase 1 — Tests
- Updated every `@patch("qgis_manager.core.X")` whose symbol moved to a submodule
  (`qgis_manager.core.<submodule>.X`). `test_commands.py` keeps patching
  `qgis_manager.core.rotate_backups` (the CLI imports it from the package).

### Phase 2 — Complexity reduction (behaviour-preserving extractions)

| Function | Before | After |
| :--- | :--- | :--- |
| `stamp_metadata_text` | D(21) | B(7) |
| `create_plugin_package` | C(18) | A(5) |
| `sync_directory` | C(15) | B(7) |
| `compile_qt_resources` | C(15) | A(4) |
| `compile_docs` | C(12) | B(7) |
| `clean_artifacts` | C(12) | A(1) |

---

## Verification

- `uv run pytest -q --cov=qgis_manager --cov-fail-under=80` → **190 passed**, **89.93 %**.
- `uv run ruff check .` / `uv run ruff format --check .` → clean.
- `uv run mypy src` → clean (36 files).
- `uvx radon cc -s -a src/qgis_manager/core` → average **A (4.44)**, max **B(8)**.
- `uvx radon mi -s src/qgis_manager/core` → all modules **A (42–63)**; each ≤ 352 lines.
- `python .agent/tools/forge.py validate` → 11 skills, 14 workflows.

---

## Notes / follow-up

- Still pending from the deep analysis (separate, not core): `validate_metadata`
  (D28), `cli/commands/deploy.py::execute` (D27), the `IgnoreMatcher`/compliance
  SSoT overlap, the dead `ignore.get_ignore_func` and the stale `ai-context-core`
  dev dependency.
