# P0 Optimization Plan — CLI, compile and dead code

**Date**: 2026-10-25
**Baseline**: 248 tests (+13 subtests), 90.45 % line coverage, strict mypy clean,
framework v1.4.2, 0 import cycles.
**Source analysis**: [`docs/reports/DEEP_CODE_OPTIMIZATION_2026-10-25.md`](../reports/DEEP_CODE_OPTIMIZATION_2026-10-25.md).

## 1. Goal

Reduce the highest-risk, highest-leverage problems found in the deep analysis without
starting the larger P1 refactors (validation split, metadata consolidation, compile
context, command registry). The P0 batch should be reviewable in small commits and must
not change user-facing behavior except for clearer errors and bounded tool execution.

## 2. Scope

### In scope

1. **CLI command lifecycle**
   - Fix double instantiation in `CLIApp._discover_commands` (`cli/app.py:55`).
   - Add a shared `BaseCommand.run()` wrapper for project-root resolution and
     unexpected-error mapping.
   - Remove the per-command `try/except Exception` boilerplate where the wrapper
     replaces it.
   - Extract deploy phases: target resolution, hooks, compile, post-hooks.
   - Extract package phases: version/dependency/compliance/package.
2. **Compile robustness**
   - Add subprocess timeouts (`sphinx`, `pyuic`, `rcc`, `lrelease`).
   - Replace raw `rglob("*.ui"/"*.qrc"/"*.ts")` scans with an ignore-aware iterator
     that skips `.venv`, `libs`, `dist`, `build`, VCS/cache dirs.
3. **Dead code**
   - Remove `validation.get_optional_fields` (only referenced by tests) or move it
     to the test suite if the public API must be preserved; preferred: remove.
4. **Regression tests**
   - Command wrapper error mapping.
   - Compile ignore-aware scan and timeout behavior.
   - Existing deploy/package E2E and CLI tests still pass.

### Out of scope (P1/P2)

- Splitting `validation.py` into rule modules.
- Moving metadata read/write/sync from `discovery.py` to `metadata.py`.
- Full `CompileContext`/tool-runner refactor.
- Command registry/entry points.
- Content hashing in `_needs_copy`.
- Branch-coverage gate and test-suite split.

## 3. Workstreams and commits

### Commit 1 — `fix(cli): instantiate commands once`

- `src/qgis_manager/cli/app.py`
  - Build instances once:
    ```python
    instances = [command_class() for command_class in command_classes]
    return {command.name: command for command in instances}
    ```
- Add/extend `tests/test_cli.py` if a constructor-count test is practical; otherwise
  document the invariant in a docstring.

**Acceptance**: `CLIApp.commands` constructs each command exactly once; all CLI tests pass.

### Commit 2 — `refactor(cli): centralize command execution`

- `src/qgis_manager/cli/base.py`
  - Add `run(args) -> int` as a template method around `execute`.
  - Add `project_root(args) -> Path` helper.
  - Standard error rendering (`❌ Error: ...`, stderr, exit 1).
- `src/qgis_manager/cli/app.py`
  - Call `command.run(args)` instead of `command.execute(args)`.
- `src/qgis_manager/cli/commands/*.py`
  - Replace `find_project_root(Path(args.path))` with `self.project_root(args)`.
  - Remove per-command `try/except Exception` where `BaseCommand.run` now owns it.
  - Keep command-specific catches (e.g., `bump` per-file metadata update) where they
    add actionable messages or continue after partial failure.
- Tests: ensure existing error-message assertions still pass; add a small
  `BaseCommand.run` error-mapping test.

**Acceptance**: no duplicated `find_project_root`/error boilerplate in command
`execute` methods; behavior unchanged; 248+ tests pass.

### Commit 3 — `refactor(cli): extract deploy orchestration`

- `src/qgis_manager/cli/commands/deploy.py`
  - `_resolve_target_dir(args, settings)` (absolute profile, named profile,
    purge prompt, existence/manual prompt).
  - `_run_hooks(name, command, root, context, interactive)`.
  - `_compile_if_needed(root, args, settings)`.
  - `execute` orchestrates the phases and returns exit codes.
- Keep `--trust`, `--purge-backups`, `--interactive`, backup/rotation behavior and
  output messages identical.
- Tests: existing deploy command/E2E tests must pass unchanged; add a focused test
  for the extracted target resolution if a gap appears.

**Acceptance**: `DeployCommand.execute` ≤60 lines and CC ≤10; all deploy tests pass.

### Commit 4 — `refactor(cli): extract package orchestration`

- `src/qgis_manager/cli/commands/package.py`
  - `_sync_version`, `_ensure_trusted_dependencies`, `_run_compliance`,
    `_build_package`.
  - `execute` becomes a short pipeline.
- Preserve `--trust`, `--repo-check`, `--sync-version`, `--stamp`, `--dev`,
  `--output`, `--release-version` semantics and messages.
- Tests: existing package command/E2E tests must pass unchanged.

**Acceptance**: `PackageCommand.execute` ≤60 lines and CC ≤10; all package tests pass.

### Commit 5 — `fix(compile): bound tools and skip dev directories`

- `src/qgis_manager/core/compile.py`
  - Add `COMPILE_TIMEOUT_SECONDS` constant (default 300).
  - Add `_iter_compile_sources(project_root, pattern, excluded_dirs)` or reuse
    `IgnoreMatcher` with explicit compile exclusions.
  - Use it in `count_compile_steps`, `compile_ui_files`, `_compile_qrc_files`,
    `_compile_ts_files`.
  - Add `timeout=...` to every `subprocess.run` (`sphinx`, `pyuic`, `rcc`,
    `lrelease`); catch `subprocess.TimeoutExpired` and return False with a clear
    error.
- Tests:
  - temporary project with `.venv/vendored.ui`, `libs/vendored.qrc`,
    `src/real.ui`; assert only real files count/compile;
  - monkeypatch `subprocess.run` to raise `TimeoutExpired`; assert False/error.
- Avoid changing tool selection or generated output.

**Acceptance**: no compile `rglob` on dev/vendor directories; no unbounded
subprocess; existing compile tests pass.

### Commit 6 — `chore(validation): remove dead optional-fields helper`

- Remove `get_optional_fields` from `validation.py`.
- Move/remove its test from `tests/test_validation.py`.
- If a public API consumer is found, stop and report before removing; otherwise
  delete it.

**Acceptance**: no references to `get_optional_fields`; 248 tests pass.

## 4. Test and quality gates

Run after every commit:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
uv run pytest .agent/tests -q
uv run python .agent/tools/forge.py validate
uv run python .agent/tools/forge.py metrics validate
```

For the final commit also run:

```bash
uv run python .agent/tools/forge.py project test-full
uv run python -m pytest tests/test_e2e_cli.py -q
uv run python scripts/sync_metrics.py
```

**Acceptance criteria**

- All existing 248 tests pass; new tests added.
- Line coverage does not drop below **90.45 %** (target: ≥90.5 %).
- No new C901 above the baseline (the only remaining known violations are
  `validate_metadata`, `validate_official_compliance`, `load_ignore_patterns` and
  `ValidateCommand.execute`, intentionally deferred to P1).
- `DeployCommand.execute` and `PackageCommand.execute` are no longer C901.
- No compile subprocess without a timeout.
- `get_optional_fields` is gone or explicitly documented as public API.
- No changes to `.agent` submodule.

## 5. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Removing per-command exceptions changes error text/exit behavior | Keep `BaseCommand.run` output compatible; run command tests and E2E; add one wrapper test |
| Deploy extraction changes prompt order or trust behavior | Preserve ordering; existing E2E covers purge/trust; add target-resolution tests |
| Ignore-aware compile scan misses legitimate nested sources | Add positive/negative scan tests; keep explicit source roots |
| Timeouts break slow QGIS builds | Make timeout a module constant (300 s) and catch `TimeoutExpired` with actionable message |
| Removing a helper breaks external imports | Search repository; `get_optional_fields` is not exported in `__all__`; if a consumer exists, stop and report |

## 6. Execution order and rollback

1. Commit 1 (one-line bug) — immediate, reversible.
2. Commit 2 (BaseCommand) — broad but mechanical.
3. Commit 3/4 (deploy/package) — separate, behavior-preserving.
4. Commit 5 (compile) — isolated core change.
5. Commit 6 (dead code) — trivial.

Each commit can be reverted independently. Do not combine a refactor with a behavior
change in the same commit.

## 7. Approval

This plan follows the Architect constraint: **do not write code until the user
approves it**. On approval, start with Commit 1 and report the diff/test result before
continuing.
