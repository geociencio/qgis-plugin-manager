# Deep Code & Optimization Analysis — 2026-10-25

**Scope**: `src/qgis_manager/` (37 Python modules, 4,292 lines / 1,906 statements),
`tests/` (3,939 lines) and the CLI orchestration layer.

**Method**: AST inventory, `ruff` C90, Radon CC/MI, Vulture, coverage, import-graph
analysis, exact function-body clone detection, manual review of the highest-complexity
paths. No production code was changed for this analysis.

**Baseline**: 248 tests passed (+13 subtests), 90.45 % line coverage, 0 import cycles,
strict mypy clean, framework v1.4.2.

**Status**: the P0 batch was implemented on 2026-10-25 (CLI single instantiation,
BaseCommand error wrapper, deploy/package extraction, compile timeouts + ignore-aware
scan, dead helper removal). Result after P3: **269 tests, 91.03 % combined coverage, C901 = 0**; nested ignores,
bounded hooks/dependencies, compile jobs and external command entry points are in
place, with hook shell compatibility and config-file jobs deferred.

---

## 1. Executive summary

The codebase is **healthier than its size suggests**: all modules have an A
maintainability index (lowest 43.46 in `core/compile.py`), average cyclomatic
complexity is A (3.87), there are no import cycles and no large exact function-body
clones. The problems are concentrated in a few orchestration/validation hotspots and in
structural duplication around the CLI, metadata and compile pipelines.

| Signal | Value | Assessment |
| :--- | ---: | :--- |
| Source lines / statements | 4,292 / 1,906 | Medium-size CLI |
| Modules | 37 | Reasonable |
| Tests | 248 (+13) | Strong |
| Line coverage | 90.45 % | Good, but error paths weak |
| C901 violations (CC > 10) | 6 | Concentrated |
| Average CC | A (3.87) | Good |
| Lowest MI | A (43.46, `core/compile.py`) | Acceptable |
| `except Exception` | 29 | Too broad in core |
| Exact clones (≥4 statements) | 0 | Good |
| Import cycles | 0 | Good |
| Largest module | 446 lines (`core/compile.py`) | Borderline |

**Top three risks**:

1. `deploy.execute` — 154 lines, CC 23, 51 calls, nesting depth 5.
2. `validate_metadata` — 91 lines, CC 23, repeated field-by-field rules.
3. Broad exception handling and silent fallbacks hide real failures in core paths.

---

## 2. Complexity and size hotspots

### 2.1 C901 violations

| Function | File | CC | Size |
| :--- | :--- | ---: | ---: |
| `DeployCommand.execute` | `cli/commands/deploy.py:75` | **23** | 154 lines |
| `validate_metadata` | `validation.py:292` | **23** | 91 lines |
| `PackageCommand.execute` | `cli/commands/package.py:67` | 11 | 94 lines |
| `ValidateCommand.execute` | `cli/commands/validate.py:52` | 11 | 79 lines |
| `load_ignore_patterns` | `ignore.py:34` | 11 | 49 lines, depth 6 |
| `validate_official_compliance` | `validation.py:177` | 11 | 61 lines |

Radon additionally flags `deploy_plugin` (10), `sync_directory` (9), `rotate_backups`
(8), `create_plugin_package` (8), `compile_ui_files` (8) and `compile_qt_resources` (8)
as B-grade, not failures but candidates to simplify.

### 2.2 Long / wide functions

| Function | Lines | Args | Depth |
| :--- | ---: | ---: | ---: |
| `DeployCommand.execute` | 154 | 2 | 5 |
| `PackageCommand.execute` | 94 | 2 | 4 |
| `validate_metadata` | 91 | 1 | 3 |
| `ValidateCommand.execute` | 79 | 2 | 3 |
| `init_plugin_project` | 71 | 6 | 1 |
| `CLIApp._build_parser` | 66 | 1 | 2 |
| `update_general_keys` | 63 | 2 | 3 |
| `deploy_plugin` | 62 | 7 | 2 |
| `validate_official_compliance` | 61 | 2 | 3 |
| `run_hook` | 60 | 4 | 3 |
| `compile_docs` | 59 | 2 | 2 |
| `create_plugin_package` | 58 | 6 | 4 |
| `_hooks_list` | 58 | 2 | 4 |

---

## 3. Dead and zombie code

### Confirmed

- **`validation.get_optional_fields`** (`validation.py:69`) is referenced only by
  `tests/test_validation.py`; production never calls it. It is either a public helper
  that should be documented as API or a test-only zombie that should move to the test
  or be removed.
- **`IgnoreMatcher.get_ignore_func`** was already removed (previously dead).
- **`src/qgis_manager/cli.py`** was already removed (shadowed by the `cli/` package).

### False positives / intentional

- Vulture flags `progress.py` `bar.label` and `discovery.py` `config.optionxform`;
  both are attributes of external objects (`click` progress bar, `ConfigParser`) and
  are legitimate.
- Uncovered `__init__.py` fallback lines are importlib-metadata compatibility paths.
- `cli/__init__.py:main` is the console entry point; it is exercised by the installed
  script rather than unit tests.

### Coverage holes that are not dead code

`core/compile.py` has 44 uncovered lines (81 %), mostly tool-missing/error branches;
`core/deploy.py` 18 (86 %), `bump.py` 15 (86 %), `discovery.py` 10 (89 %). These are
error/fallback paths, not necessarily unnecessary code. They are the best candidates
for targeted failure tests, not deletion.

---

## 4. Duplication

No exact function-body clones ≥4 statements were found, and Pylint's duplicate-code
check is clean at a 6-line threshold. The duplication is **structural**, not textual:

### 4.1 CLI command boilerplate

All 12 command classes repeat the same shape:

```python
try:
    root = find_project_root(Path(args.path))
    ...
except Exception as e:
    click.echo(click.style(f"❌ Error: {e}", ...), err=True)
    return 1
```

`find_project_root(Path(args.path))` appears in 11 commands; the error formatting is
repeated with small variations. `BaseCommand` only defines parser hooks; it does not
own the common execution contract. A `BaseCommand.run()` template method (or a
`CLIApp` wrapper) could centralize root discovery, exception mapping and exit codes.

### 4.2 Metadata read/write/sync split across modules

`discovery.py` currently owns:

- `get_plugin_metadata` (`:132`)
- `save_plugin_metadata` (`:180`)
- `sync_metadata_version` (`:218`)

while `metadata.py` owns the line-oriented updater and atomic writer. `bump.py` and
`package.py` both call `sync_metadata_version`, and `package.py`/`core/package.py`
both talk about metadata stamping. Consolidating all metadata parsing/writing/sync in
`metadata.py` would remove a conceptual seam and reduce `discovery.py`'s fan-in (15).

### 4.3 Compile runners

`core/compile.py` has three near-identical runners:

- `compile_ui_files` (`:270`) → `pyuic`
- `_compile_single_qrc` / `_compile_qrc_files` (`:329`, `:359`) → `rcc`
- `_compile_single_ts` / `_compile_ts_files` (`:379`, `:406`) → `lrelease`

Each repeats callback start/done, `subprocess.run`, error logging and boolean
aggregation. A small `ToolRunner`/`CompileContext` (project root, tool path, callback)
would collapse the duplication and make timeouts/patching uniform.

### 4.4 Tests

`tests/test_commands.py` (790 lines) and `tests/test_core.py` (737) repeat temporary
project setup, metadata blocks and mock stacks. Shared fixtures/helpers in
`tests/conftest.py` would reduce maintenance without changing coverage.

---

## 5. Spaghetti / coupling indicators

### Positive

- **No import cycles** (Tarjan SCC across 37 modules).
- `core/__init__.py` is an explicit re-export surface; imports resolve cleanly.
- Average MI is A; only `core/compile.py` approaches the B boundary.

### Negative

| Indicator | Evidence | Why it matters |
| :--- | :--- | :--- |
| God orchestration | `DeployCommand.execute` 154 lines / 51 calls | Hard to test combinations; target resolution, trust, hooks, compile and deploy are interleaved. |
| Rule monolith | `validate_metadata` 91 lines / CC 23 | Adding a rule means editing a long function; rules cannot be reused/reordered easily. |
| Fan-in hub | `discovery.py` fan-in 15 | Every layer imports project root/metadata/slug helpers; changes ripple widely. |
| Fan-out hub | `cli.app` fan-out 14 | Command discovery imports 12 concrete classes statically. |
| Broad catches | 29 `except Exception` | Core silently degrades (`ignore`, `toml_utils`, `compile`, `deploy`) instead of surfacing corruption/config errors. |
| Double instantiation | `cli/app.py:55` `{cmd().name: cmd() ...}` | Each command is constructed **twice**; harmless today but a real bug/extension hazard. |
| Repeated scan roots | `core/compile.py` `rglob` at `:174`, `:287`, `:363`, `:411` | Scans `.venv`, `libs`, nested copies; slow and can compile vendored files. |
| No subprocess timeout | `compile.py:312`, `:343`, `:391` | A hung tool blocks the CLI indefinitely. |

### 5.1 The double-instantiation bug

```python
return {cmd().name: cmd() for cmd in command_classes}
```

This creates two instances per command: one only to read `.name`, one stored. It also
means any future constructor side effect runs twice. Fix is trivial:

```python
instances = [cmd() for cmd in command_classes]
return {command.name: command for command in instances}
```

---

## 6. Recommended optimizations

### P0 — quick, low-risk wins (hours)

1. **Fix command double instantiation** (`cli/app.py:55`). One-line behavior fix.
2. **Add a `BaseCommand` execution template**:
   - resolve project root once;
   - standard exception → exit-code mapping;
   - shared error/warning rendering.
   Keep command-specific `_run()` methods. This removes ~12 copies of the same
   `try/except` and makes error behavior consistent.
3. **Extract deploy phases**:
   `_resolve_target_dir`, `_run_pre_hooks`, `_compile_if_needed`, `_run_post_hooks`.
   Target: ≤60 lines in `execute`.
4. **Extract package compliance**:
   `_install_dependencies_with_trust` and `_run_compliance_check`; target ≤50 lines.
5. **Remove or document `get_optional_fields`**; if it is public API, add it to
   `__all__` and a docstring stating that; otherwise delete it and its test.
6. **Add subprocess timeouts** to all compile tools and log/return a clear error.
7. **Use `IgnoreMatcher`/`get_source_files` for compile scans** instead of raw
   `rglob`, so `.venv`, `libs`, `dist` and build artifacts are excluded.

### P1 — structural refactors (1–3 days)

8. **Split `validation.py`** into:
   - `validation/metadata.py` — field rules;
   - `validation/repository.py` — official compliance/license/binaries;
   - `validation/structure.py` — project layout;
   - `validation/result.py` — `ValidationResult`.
   Replace the `validate_metadata` chain with a list of small rule functions returning
   issues. This directly addresses CC 23.
9. **Consolidate metadata ownership**:
   move `get_plugin_metadata`, `save_plugin_metadata`, `sync_metadata_version` into
   `metadata.py`; leave `discovery.py` with project-root/slug/source-file discovery.
   Update `core.deploy`, `package`, `bump`, `validate` imports.
10. **Introduce a command registry**:
    replace the 12 inline imports in `_discover_commands` with a module-level registry
    or entry-point list; `cli.app` fan-out drops from 14 to 1–2.
11. **Compile tool runner**:
    one context object with tool lookup, timeout, callback and error mapping; three
    tool families become thin adapters. Move `verify_resource_patch`/`patch_ui_file`
    text rewriting into one helper.
12. **Deploy sync content check**:
    `_needs_copy` compares only size+mtime; use a fast hash (or `filecmp.cmp` with
    shallow fallback) when sizes match to avoid stale deployments after mtime-preserving
    copies. Make it optional for large trees.

### P2 — quality/ops (ongoing)

13. **Narrow exceptions**: replace `except Exception` in `core/`, `ignore.py`,
    `toml_utils.py` with expected exceptions (`OSError`, `ValueError`,
    `subprocess.CalledProcessError`, `configparser.Error`); use `logger.exception`
    for unexpected ones. Keep the top-level CLI catch.
14. **Branch coverage**: add `--cov-branch` and a branch target close to line coverage;
    target the 44 missing lines in `compile.py` and the deploy/bump error paths.
15. **Split large test files** and add fixtures for plugin projects/metadata; add
    contract tests for `compile`, `bump` and `init` (only deploy/package are true E2E).
16. **Config portability**: `load_config` hardcodes `~/.config`; use
    `XDG_CONFIG_HOME`/`APPDATA` (with `platformdirs` or a small helper).
17. **Ignore semantics**: `load_ignore_patterns` loads only the first ignore file and
    has no negation; split loaders (CC 11) and document the supported subset.
18. **`_build_parser` 66 lines**: build the epilog/examples from the command registry;
    keep command examples near their classes.

---

## 7. Suggested sequence

| Step | Work | Why |
| :--- | :--- | :--- |
| 1 | Double init + subprocess timeouts + compile ignore | Immediate correctness/robustness, tiny diff |
| 2 | `BaseCommand.run` + deploy/package extraction | Removes the biggest CC and boilerplate |
| 3 | Validation rule modules | Highest maintainability payoff |
| 4 | Metadata consolidation | Cuts discovery fan-in and duplicate concepts |
| 5 | Compile runner + branch coverage | Makes the largest module safe to change |
| 6 | Command registry + test fixtures | Long-term extensibility |

---

## 8. What not to do

- Do **not** split modules solely to hit a line-count target; the current module sizes
  are mostly acceptable.
- Do **not** replace all `except Exception` blindly: the top-level CLI guard is
  intentional. Narrow only where the failure mode is known.
- Do **not** add a dependency for clone detection/ignore matching unless the behavior
  is a requirement; the current stdlib-only design is a feature.
- Do **not** refactor `core/compile.py` and `validation.py` in the same PR as behavior
  fixes; keep pure moves/refactors separate from semantic changes.
