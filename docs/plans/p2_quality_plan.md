# P2 Quality & Reliability Plan — errors, branches, config, ignore and tests

**Date**: 2026-10-25
**Baseline after P1**: 253 tests (+13 subtests), 92.35 % line coverage,
90.57 % branch coverage (614 branches, 83 missed), C901 = 0, 17 broad
`except Exception` sites.
**Source**: [`DEEP_CODE_OPTIMIZATION_2026-10-25.md`](../reports/DEEP_CODE_OPTIMIZATION_2026-10-25.md).
**Predecessors**: [`p0_optimization_plan.md`](p0_optimization_plan.md),
[`p1_optimization_plan.md`](p1_optimization_plan.md) — implemented.
**Status**: ✅ Implemented 2026-10-25 in commits `b1afd80`, `8df1ae9`, `6c2c76a`, `dd8e17c`, `f8bd39b`, `e316303`, `b9d5297`.

## 1. Goal

Harden behavior and tests after the structural P1 refactors: stop swallowing
unexpected errors, make branch coverage a gate, remove the remaining environment
assumptions, finish the ignore semantics needed by real projects, and split the
largest test modules before they become unmaintainable.

## 2. Current state

| Item | State |
| :--- | :--- |
| Tests / line / branch | 253 / 92.35 % / 90.57 % |
| C901 | 0 |
| Broad `except Exception` | 17 |
| Largest tests | `test_commands.py` 790, `test_core.py` 737, `test_e2e_cli.py` 386 |
| Config path | hardcoded `~/.config/qgis-manager/config.toml` |
| Windows dependency path | `os.environ["APPDATA"]` raises `KeyError` if unset |
| Ignore semantics | root file only; no `!` negation; no nested ignore files |
| Project root | climbs to `/`; can select a monorepo parent |

## 3. Workstreams and commits

### Commit 1 — `fix(errors): narrow exception handling`

Audit the 17 sites and replace broad catches where the failure mode is known:

- `toml_utils.py`: catch `tomllib.TOMLDecodeError` / `OSError`, not `Exception`.
- `metadata.py`: catch `configparser.Error`, `UnicodeDecodeError`, `OSError`.
- `validation/structure.py`: catch `OSError`/`UnicodeDecodeError` when reading
  `__init__.py`.
- `core/compile.py`: narrow patch/read/write catches to `OSError`,
  `UnicodeDecodeError` and `ValueError`; never catch `KeyboardInterrupt`.
- `core/deploy.py`: narrow path-resolution fallbacks to `OSError`, `ValueError`,
  `RuntimeError`.
- `hooks.py` / `dependencies.py`: narrow subprocess/import errors; keep a final
  unexpected-error log with `logger.exception`.
- `cli/app.py` and `cli/base.py`: keep the intentional top-level guards, documented.
- `bump.py` per-file metadata catch: narrow to `OSError`/`ValueError`.

Add tests for each newly narrowed path (malformed TOML, unreadable metadata,
missing APPDATA, failed subprocess).

**Acceptance**: no `except Exception` in `core/`, `metadata.py`, `toml_utils.py`,
`validation/` or `discovery.py`; only the two documented CLI boundaries remain.
Error messages and exit codes preserved.

### Commit 2 — `test: enforce branch coverage`

- Enable branch coverage in the test command/config:
  `pytest --cov=qgis_manager --cov-branch --cov-fail-under=90`.
- Update CI and `forge.toml` `test_command_full` accordingly.
- Add tests for the 83 missing branches, prioritizing:
  - compile tool-missing/timeout paths;
  - deploy backup/rotation/trust errors;
  - bump sync/metadata failures;
  - config missing/malformed files.
- Keep line coverage ≥92.35 %.

**Acceptance**: branch coverage ≥90 % enforced; line coverage not reduced; CI
and local collector agree.

### Commit 3 — `refactor(config): portable config and APPDATA fallback`

- Add `config_path()`:
  - Linux/macOS: `$XDG_CONFIG_HOME/qgis-manager/config.toml`, falling back to
    `~/.config/qgis-manager/config.toml`.
  - Windows: `%APPDATA%/qgis-manager/config.toml`, falling back to
    `Path.home()/AppData/Roaming/...` if `APPDATA` is absent.
- `core/platform.get_qgis_plugin_dir`: use `os.environ.get("APPDATA")` with a
  clear `OSError` when unavailable, not `KeyError`.
- Tests with `monkeypatch.setenv/delenv` for both platforms.
- Do not change the project-level `pyproject.toml` overrides.

**Acceptance**: no hardcoded `~/.config` in `config.py`; no raw `os.environ[...]`
for APPDATA; tests pass on Linux/Windows/macOS CI.

### Commit 4 — `feat(ignore): support negation patterns`

- Implement ordered matching: last matching pattern wins, `!pattern` re-includes
  a path that an earlier pattern excluded.
- Preserve root-only ignore-file precedence (`.qgisignore` before `.gitignore`);
  document that nested ignore files are still unsupported.
- Add tests: exclude then re-include file/directory, ordering, root-relative and
  global patterns.
- Do **not** change default patterns or `include_dev` semantics.

**Acceptance**: negation works in deploy/package scans; existing ignore tests
unchanged; nested files explicitly documented as out of scope.

### Commit 5 — `fix(discovery): stop project-root search at repository boundary`

- `find_project_root` stops when it finds a `.git` file/directory **and** no
  project root was found below it; it must not select a parent monorepo
  `pyproject.toml`.
- Keep `--path` behavior and error message.
- Tests: nested package inside a Git repo without metadata → `FileNotFoundError`;
  project root with metadata found before the boundary.
- Rationale: avoids accidentally operating on a parent project.

**Acceptance**: no `/` climb past a Git boundary; all discovery/deploy tests pass.

### Commit 6 — `refactor(cli): add BaseCommand.project_root`

- Add `BaseCommand.project_root(args)` and use it in commands that need a project
  root; this was deferred from P0.
- Update tests that patch per-command `find_project_root` to patch the shared
  helper (or make the helper injectable).
- Keep command-specific `--path` handling (`init`, etc.) unchanged.

**Acceptance**: no duplicated `find_project_root(Path(args.path))` in commands;
CLI tests/E2E pass.

### Commit 7 — `test: split command/core suites and add fixtures`

- Split `tests/test_commands.py` into `tests/commands/` by command group and
  `tests/test_core.py` by area (deploy/compile/package/scaffold).
- Add shared `tests/conftest.py` fixtures for temporary plugin projects and
  metadata; avoid changing test semantics.
- Add contract tests for `compile`, `bump` and `init` where P1 only had
  deploy/package E2E.

**Acceptance**: same test count or higher; pytest discovery works; no duplicate
fixture code; coverage unchanged or better.

### Commit 8 — `chore(agent): record P2 results`

- Refresh `agent_metrics.json`, task/next_steps, plan/report status.
- No production changes.

## 4. Test and quality gates

After every commit:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
uv run pytest .agent/tests -q
uv run python .agent/tools/forge.py validate
uv run python .agent/tools/forge.py metrics validate
```

Final:

```bash
uv run python .agent/tools/forge.py project test-full
uv run python -m pytest --cov=qgis_manager --cov-branch --cov-fail-under=90
uv run ruff check --select C90 src/qgis_manager
```

## 5. Acceptance criteria

- **C901 remains 0.**
- **Branch coverage ≥90 %** and line coverage ≥92.35 %.
- **No broad `except Exception`** outside the two documented CLI boundaries.
- No hardcoded `~/.config`; no unguarded `os.environ["APPDATA"]`.
- Ignore negation works and is documented; nested ignore files explicitly out of
  scope.
- `find_project_root` stops at a Git boundary instead of selecting a monorepo.
- All existing 253 tests pass; new tests cover error branches.
- No changes to the `.agent` submodule or new runtime dependencies.

## 6. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Narrowing exceptions changes fallback behavior | Add exact failing tests for each path; preserve messages/exit codes |
| Branch gate fails due generous 90.57 baseline | Target 90, add tests for compile/deploy/config first; keep line gate unchanged |
| Config XDG changes break tests/users | Keep `~/.config` fallback; test both envs; document precedence |
| Negation changes existing ignores | Add ordering tests; preserve defaults and root precedence |
| Project-root boundary breaks monorepos | Only stop at `.git` if no project root was found below; test nested repo |
| Test split loses discovery | Use `tests/commands/` subpackage with `__init__`; run full suite |

## 7. Sequence and rollback

1. Narrow exceptions (behavioral, test-heavy).
2. Branch coverage gate (test-only + config).
3. Config portability.
4. Ignore negation.
5. Project-root boundary.
6. `BaseCommand.project_root`.
7. Test-suite split/fixtures.

Each commit is independently revertible. Do not combine exception narrowing with
coverage-gate changes; keep behavior fixes separate from test-only changes.

## 8. Out of scope (P3)

- Nested `.gitignore` files and full Git ignore semantics.
- Sandboxing hooks/dependency installation beyond the existing `--trust` model.
- Async/parallel compile execution.
- Plugin command auto-discovery via entry points.

## 9. Approval

Per the Architect constraint, **no code will be written until this plan is approved**.
On approval, start with Commit 1 and report the exact exception sites changed and
their tests before moving to coverage enforcement.
