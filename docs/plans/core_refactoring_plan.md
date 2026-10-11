# Technical Plan — `core.py` Split & Optimization

**Status**: IMPLEMENTED (2026-10-10) — split + complexity reduction landed; all gates green.
**Scope**: Break the 840-line `src/qgis_manager/core.py` monolith into a
`qgis_manager.core` package and lower the cyclomatic complexity of its hottest
functions. Behaviour-preserving refactor.
**Related**: `docs/reports/DEEP_ANALYSIS_v0.9.0.md` (§2 duplication, §3 complexity,
P1 recommendation), `forge.toml` (`max_cc = 10`, `module_size_limit = 400`).

---

## 1. Context & objective

`core.py` is the only module that violates the project thresholds and has the lowest
Maintainability Index in the repo. This plan:

1. **Split** it into cohesive submodules re-exported through `core/__init__.py`
   (import compatibility preserved).
2. **Reduce cyclomatic complexity** of the 6 functions above `max_cc = 10`.
3. Keep the full test suite green at every step.

### Baseline (recorded 2026-10-10, commit state after release-pipeline work)

| Metric | Value |
| :--- | :--- |
| `core.py` lines / statements | 840 / 425 |
| Functions / classes | 21 / 0 |
| Radon MI | **A (23.75)** |
| Radon average CC | **B (7.67)** |
| Functions > CC 10 | 6 (`stamp_metadata_text` D21, `create_plugin_package` C18, `sync_directory` C15, `compile_qt_resources` C15, `compile_docs` C12, `clean_artifacts` C12) |
| Coverage (`core.py`) | 89 % (45 statements missed) |
| Tests | 190 passed |
| Public consumers | `cli/commands/{deploy,compile,package,clean,init,dclean}.py` + 4 test modules |

---

## 2. Non-goals

- Do **not** touch `ignore.py`, `validation.py`, `discovery.py` (cross-tool concerns
  from the deep analysis are separate, P2/P3).
- Do **not** change any public behaviour, signatures, log messages or output.
- Do **not** add new features or fix the uncovered branches (coverage work is separate);
  the split must not *lower* coverage below 80 %.

---

## 3. Target architecture

```
src/qgis_manager/core/
├── __init__.py     # re-exports the public API (import compatibility)
├── platform.py     # get_qgis_plugin_dir
├── deploy.py       # uninstall_plugin, rotate_backups, sync_directory, deploy_plugin
├── compile.py      # compile_docs, get_rcc_tool, get_uic_tool, _is_stale,
│                   # count_compile_steps, verify_resource_patch, patch_resource_file,
│                   # patch_ui_file, compile_ui_files, compile_qt_resources
├── package.py      # is_prerelease, get_git_info, stamp_metadata_text, create_plugin_package
├── cleanup.py      # clean_artifacts
└── scaffold.py     # init_plugin_project
```

`core/__init__.py` re-exports every public symbol so existing
`from qgis_manager.core import X` imports (CLI + tests) keep working:

```python
from __future__ import annotations

from .cleanup import clean_artifacts
from .compile import (
    compile_docs,
    compile_qt_resources,
    compile_ui_files,
    count_compile_steps,
    get_rcc_tool,
    get_uic_tool,
    patch_resource_file,
    patch_ui_file,
    verify_resource_patch,
)
from .deploy import (
    deploy_plugin,
    rotate_backups,
    sync_directory,
    uninstall_plugin,
)
from .package import (
    create_plugin_package,
    get_git_info,
    is_prerelease,
    stamp_metadata_text,
)
from .platform import get_qgis_plugin_dir
from .scaffold import init_plugin_project

__all__ = [ ... ]  # the 20 public names above
```

---

## 4. Import & path adjustments (critical)

Moving code one level deeper changes relative imports and one `__file__` path:

| Location | Change |
| :--- | :--- |
| every submodule | `from .discovery import …` → `from ..discovery import …` |
| every submodule | `from .ignore import IgnoreMatcher` → `from ..ignore import IgnoreMatcher` |
| `scaffold.py` | `from .templating import render_template` → `from ..templating import render_template`; `from .discovery import slugify` → `from ..discovery import slugify` |
| `scaffold.py:804` | **`Path(__file__).resolve().parent / "templates"` → `Path(__file__).resolve().parent.parent / "templates"`** (templates live at `qgis_manager/templates/`) |
| `deploy.py` | `from .platform import get_qgis_plugin_dir` (so it resolves to `core.deploy.get_qgis_plugin_dir` for patching) |

No CLI change is required (`...core` imports resolve through `__init__.py`).

---

## 5. Test migration — `@patch` targets (mandatory)

`unittest.mock.patch("qgis_manager.core.X")` resolves the attribute on the `core`
package. Because each submodule looks up its own module globals, **re-exports do not
preserve patch semantics**. Every target must point at the submodule that *calls* the
symbol. Exact mapping:

| Current target | Test line(s) | New target |
| :--- | :--- | :--- |
| `qgis_manager.core.get_plugin_metadata` | `test_core.py:78, 98, 260` (deploy_plugin) | `qgis_manager.core.deploy.get_plugin_metadata` |
| `qgis_manager.core.get_plugin_metadata` | `test_core.py:234, 251` (uninstall_plugin) | `qgis_manager.core.deploy.get_plugin_metadata` |
| `qgis_manager.core.sync_directory` | `test_core.py:79, 101, 261` | `qgis_manager.core.deploy.sync_directory` |
| `qgis_manager.core.datetime` | `test_core.py:100` (deploy_plugin) | `qgis_manager.core.deploy.datetime` |
| `qgis_manager.core.get_qgis_plugin_dir` | `test_core.py:237, 254` (uninstall_plugin) | `qgis_manager.core.deploy.get_qgis_plugin_dir` |
| `qgis_manager.core.get_rcc_tool` | `test_core.py:124, 430` | `qgis_manager.core.compile.get_rcc_tool` |
| `qgis_manager.core.get_uic_tool` | `test_core.py:502, 518, 537` | `qgis_manager.core.compile.get_uic_tool` |
| `qgis_manager.core.patch_ui_file` | `test_core.py:501` | `qgis_manager.core.compile.patch_ui_file` |
| `qgis_manager.core.subprocess.run` | `test_core.py:581, 586` (get_git_info) | `qgis_manager.core.package.subprocess.run` |
| `qgis_manager.core.get_git_info` | `test_core.py:590` | `qgis_manager.core.package.get_git_info` |
| `qgis_manager.core.rotate_backups` | `test_commands.py:390` | `qgis_manager.core.deploy.rotate_backups` |

Direct imports (`from qgis_manager.core import …`) in `test_core.py`,
`test_fix_exclusions.py`, `test_rcc_modernization.py`,
`test_deployment_optimization.py` **need no change** (re-export handles them).

> Alternative considered and rejected: making each submodule import the *module* and
> calling `module.func()`. It does not reduce churn and adds indirection.

---

## 6. Complexity reduction (behaviour-preserving extractions)

Applied after the split, one commit, each function target **≤ 10**.

| Function | Current | Extraction plan |
| :--- | :--- | :--- |
| `stamp_metadata_text` (D21) | `package.py` | module-level `_GENERAL_KEY_RE`; helpers `_apply_key_line(line, updates, applied) -> str \| None` and `_insert_missing_general(out, general_tail, updates, applied)` |
| `create_plugin_package` (C18) | `package.py` | `_build_stamped_metadata(root, version) -> str \| None`; `_collect_zip_items(root, matcher, slug, include_dev) -> list[tuple[Path, str]]`; `_write_zip(zip_path, items, metadata_path, metadata_content, callback)`; `_write_checksum(zip_path, checksum_file)` |
| `sync_directory` (C15) | `deploy.py` | `_is_same_or_nested(item, dst) -> bool`; `_needs_copy(src, dst) -> bool`; `_copy_one(item, dest_item)`; `_cleanup_destination(src, dst, matcher)` |
| `compile_qt_resources` (C15) | `compile.py` | `_compile_qrc_files(root, callback)`; `_compile_ts_files(root, callback)`; keep the type dispatch only |
| `compile_docs` (C12) | `compile.py` | `_run_sphinx(cmd, callback)` encapsulating `Popen` streaming + returncode check |
| `clean_artifacts` (C12) | `cleanup.py` | `_remove_cache_dirs(root)`, `_remove_cache_files(root)`, `_remove_compiled_outputs(root)`, `_remove_docs_output(root)` |

Signatures, return values, log/echo text and callbacks stay identical.

---

## 7. Execution phases (each phase = one green commit)

**Phase 0 — Baseline.** Record `pytest -q`, coverage, radon, mypy, ruff (already green).

**Phase 1 — Package split (behaviour-preserving).**
1. `mkdir src/qgis_manager/core/` and create the 6 submodules + `__init__.py`.
2. Move functions verbatim; fix relative imports and the templates path (§4).
3. `git rm src/qgis_manager/core.py`.
4. Update `@patch` targets (§5).
5. Gate: `pytest`, `ruff check`, `ruff format --check`, `mypy`, coverage ≥ 80 %.
   → *Behaviour and metrics unchanged except file layout.*

**Phase 2 — Complexity reduction.**
6. Apply the extractions (§6), function by function.
7. Gate: same suite + radon confirms every `core/*` function ≤ CC 10.

**Phase 3 — Documentation.**
8. Update `docs/reports/DEEP_ANALYSIS_v0.9.0.md` (mark P1/P2-core items done),
   add a `docs/DEVELOPMENT_LOG.md` entry and a session log.

---

## 8. Verification gates

```bash
uv run ruff check . && uv run ruff format --check .
uv run mypy src
uv run pytest -q --cov=qgis_manager --cov-report=term-missing --cov-fail-under=80
python .agent/tools/forge.py validate
uvx radon cc -s -a src/qgis_manager/core          # no function > 10
uvx radon mi -s src/qgis_manager/core             # all A
```

Acceptance criteria:
- 190 tests still pass; coverage ≥ 80 % (target: unchanged ~89 %).
- No file in `core/` exceeds 400 lines; no function exceeds CC 10.
- `import qgis_manager.core as core` exposes the same 20 public names.
- CLI (`qgis-manage --version`, `--help`, a `deploy --help`) still works.

---

## 9. Risks & mitigations

| Risk | Likelihood | Mitigation |
| :--- | :--- | :--- |
| Broken `@patch` after split | High | Explicit mapping (§5); Phase 1 runs the full suite before proceeding |
| `templates` path regression in `init_plugin_project` | High | `parent.parent` fix (§4); `test_core` template tests cover it |
| Circular imports between submodules | Low | Layering: `platform` ← `deploy`; `package`/`compile`/`cleanup`/`scaffold` independent |
| Coverage drops on moved except-branches | Medium | Gate at 80 %; increases coverage threshold buffer already at ~89 % |
| Hidden consumer of `qgis_manager.core` module path | Low | `rg "qgis_manager.core"` audited: only CLI (via re-export) + tests |

Rollback: each phase is an isolated commit; `git revert` restores the previous state.
Phase 1 is pure code motion, so reverting it is safe by construction.

---

## 10. Deliverables

- `src/qgis_manager/core/` package (6 modules + `__init__.py`), old `core.py` removed.
- Updated `@patch` targets in `tests/test_core.py`, `tests/test_commands.py`.
- Updated `DEEP_ANALYSIS` report, `DEVELOPMENT_LOG.md`, session log.

---

## 11. Approval required

Per the @architect role, **no code will be written or executed until this plan is
explicitly approved**. Open decisions for the user:

1. Approve the module split as proposed (names/grouping)?
2. Reduce complexity in the **same** refactor (Phase 2) or defer it to a follow-up?
3. Keep `clean_artifacts` in its own `cleanup.py`, or fold it into `compile.py`?
