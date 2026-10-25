# P1 Optimization Plan — Validation, metadata, compile and CLI registry

**Date**: 2026-10-25
**Baseline after P0**: 250 tests (+13 subtests), 91.83 % line coverage, strict mypy clean,
0 import cycles, 3 remaining C901 violations.
**Source analysis**: [`DEEP_CODE_OPTIMIZATION_2026-10-25.md`](../reports/DEEP_CODE_OPTIMIZATION_2026-10-25.md).
**Predecessor**: [`p0_optimization_plan.md`](p0_optimization_plan.md) — implemented.
**Status**: ✅ Implemented 2026-10-25 in commits `75b7448`, `9887640`, `41317c5`, `d92be38`, `b794dd4`, `2354eb7`; C901 = 0.

## 1. Goal

Continue the structural optimization started in P0: split the validation monolith,
consolidate metadata ownership, remove the remaining C901 violations, reduce CLI
coupling and make compile/deploy internals reusable. Preserve every public import and
all CLI behavior.

## 2. Current state

| Item | State |
| :--- | :--- |
| Tests / coverage | 250 (+13) / 91.83 % |
| C901 | 3: `validate_metadata` (23), `validate_official_compliance` (11), `load_ignore_patterns` (11) |
| Largest module | `core/compile.py` ~500 lines after P0 |
| CLI fan-out | `cli.app` imports 12 concrete commands inline |
| Metadata ownership | split between `discovery.py` and `metadata.py` |
| Deploy sync | `_needs_copy` uses only size + mtime |
| Public API | `qgis_manager.validation`, `qgis_manager.discovery`, `qgis_manager.core` |

## 3. Workstreams and commits

### Commit 1 — `refactor(ignore): split pattern loading`

- `src/qgis_manager/ignore.py`
  - Extract `_load_ignore_file(path) -> list[str]`.
  - Extract `_load_pyproject_ignores(project_root) -> list[str]`.
  - Keep `load_ignore_patterns()` as the composition point.
- Preserve current semantics exactly: first `.qgisignore`/`.gitignore` wins, no negation,
  dev-directory expansion unchanged.
- Tests: existing `test_ignore.py`/`test_ignore_system.py`; add one test for precedence
  and one for pyproject-only patterns if missing.

**Acceptance**: `load_ignore_patterns` no longer C901; all ignore tests pass.

### Commit 2 — `refactor(validation): split into focused modules`

Create a package:

```text
src/qgis_manager/validation/
    __init__.py        # re-export the existing public API
    result.py          # ValidationResult
    fields.py          # version/email/url/category/tags/boolean validators
    metadata.py        # validate_metadata and required fields
    repository.py      # validate_official_compliance
    structure.py       # validate_project_structure
```

- Replace the `validate_metadata` if-chain with small rule functions returning
  `list[str]` / a `ValidationResult`.
- Keep signatures used by `package.py`, `validate.py` and tests:
  `validate_metadata`, `validate_official_compliance`, `validate_project_structure`,
  `ValidationResult`, individual field validators.
- `validation/__init__.py` must re-export everything currently imported from
  `qgis_manager.validation`.
- Tests: existing validation tests must pass without import changes; add a rule-order
  test only if needed.

**Acceptance**: both validation C901 violations are gone; imports remain compatible;
`package --repo-check` behavior unchanged.

### Commit 3 — `refactor(metadata): consolidate metadata ownership`

- Move `get_plugin_metadata`, `save_plugin_metadata` and `sync_metadata_version` from
  `discovery.py` to `metadata.py`.
- Extract `slugify`/`validate_slug` (and reserved names) into `naming.py` to avoid a
  `metadata ↔ discovery` cycle.
- `discovery.py` keeps **compatibility re-exports** for the moved names and `slugify`,
  so external imports keep working.
- Update internal imports in `core/deploy`, `core/package`, `cli/commands/bump`,
  `cli/commands/package`, `cli/commands/validate` and `validation`.
- Tests: existing discovery/metadata tests pass; add a test that the compatibility
  imports resolve and that `save_plugin_metadata` preserves formatting (existing).

**Acceptance**: no cycles; `discovery.py` no longer owns metadata parsing/writing;
compatibility imports unchanged; tests pass.

### Commit 4 — `refactor(cli): add command registry`

- Add `src/qgis_manager/cli/registry.py` (or fill `cli/commands/__init__.py`) with the
  ordered command classes.
- `cli.app._discover_commands` imports only the registry, not 12 modules.
- Keep command names/order/help output identical.
- Tests: existing CLI/help tests; add a registry completeness test (all commands have
  unique names and are `BaseCommand` subclasses).

**Acceptance**: `cli.app` fan-out drops to 1; `qgis-manage --help` unchanged.

### Commit 5 — `refactor(compile): introduce CompileContext/tool runner`

- Add a small `CompileContext` (project root, callback, tool paths, timeout) and a
  generic `_run_tool(command, label, patcher)` helper.
- Rewrite `compile_ui_files`, `_compile_qrc_files` and `_compile_ts_files` as thin
  adapters over it.
- Preserve public functions, callback strings, tool-missing messages, timeout constant
  and patching behavior.
- Tests: existing compile tests + scan/timeout tests; add a test that callback events
  and failure aggregation are unchanged.

**Acceptance**: no duplicated subprocess/callback loops; existing output/behavior
unchanged; no new C901.

### Commit 6 — `fix(deploy): detect content changes beyond size+mtime`

- `core/deploy._needs_copy`:
  - If destination is missing → copy.
  - If size differs → copy.
  - If size matches but mtime differs → compare content (e.g.
    `filecmp.cmp(shallow=False)`) and copy only when different.
- Add a test where a file is rewritten with the same size and an old mtime; deploy
  must update it.
- Consider a fast path for large/unchanged trees (size first).

**Acceptance**: same-size, same-mtime content changes are deployed; normal deploy
tests/performance unchanged.

### Commit 7 — `chore(agent): record P1 results`

- Refresh `agent_metrics.json`, task/next_steps, optimization report and this plan
  status.
- No behavior changes.

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
uv run python -m pytest tests/test_e2e_cli.py -q
uv run python scripts/sync_metrics.py
uv run ruff check --select C90 src/qgis_manager
```

## 5. Acceptance criteria

- **C901 = 0** across `src/qgis_manager`.
- Existing **250 tests** pass; new tests added; coverage **≥91.83 %**.
- All current public imports still resolve:
  - `from qgis_manager.validation import ValidationResult, validate_metadata`
  - `from qgis_manager.discovery import get_plugin_metadata, save_plugin_metadata, slugify`
  - `from qgis_manager.core import deploy_plugin`
- CLI help/command order/exit codes unchanged.
- Compile callbacks/tool messages unchanged; timeouts preserved.
- Deploy detects same-size/same-mtime content changes.
- No changes to `.agent` submodule.
- No new runtime dependencies.

## 6. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Validation package move breaks imports/tests | `__init__.py` re-exports; run full suite; keep function signatures |
| Metadata move creates an import cycle | Extract `naming.py`; import direction `metadata → naming`, `discovery → naming/metadata` |
| Command registry import cycle/order change | Registry imports only command classes; CLI tests compare help/order |
| Compile refactor changes callback/output | Golden assertions on callback strings and tool-missing paths |
| Hash comparison slows deploy | Compare sizes first; only hash when size matches; benchmark a large tree |
| Public API removal | Compatibility re-exports; deprecate only in a later major |

## 7. Sequence and rollback

1. Ignore loader split (small, isolated).
2. Validation package split (largest, but tests stable).
3. Metadata/naming consolidation.
4. Command registry.
5. Compile context/tool runner.
6. Deploy content comparison.

Each commit is independently revertible. Do not combine validation and metadata moves
in one commit; keep pure moves separate from rule changes.

## 8. Out of scope (P2)

- Narrowing all broad exceptions.
- Branch-coverage gate and test-suite split.
- Config portability (`XDG_CONFIG_HOME`/`APPDATA`).
- Ignore negation/nested ignore files.
- `BaseCommand.project_root()` extraction (deferred from P0).

## 9. Approval

Per the Architect constraint, **no code will be written until this plan is approved**.
On approval, start with Commit 1 and report tests before moving to the next commit.
