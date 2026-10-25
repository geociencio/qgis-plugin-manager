# Test Coverage Improvement Plan — risk-weighted branches

**Date**: 2026-10-25
**Baseline**: 279 tests, 92.53 % statements (1957/2115), 85.33 % branches
(570/668), 90.80 % combined, C901 = 0.
**Context**: P0 for 0.10.1 is complete. This plan raises branch coverage before
and alongside P1; it does not chase 100 % or add vanity tests.

## 1. Why the current gate is misleading

The project runs pytest with `--cov-branch --cov-fail-under=90`, but
`--cov-fail-under` checks the **combined** line+branch percentage. A run can be
at 90.80 % combined while only 85.33 % of branches are covered.

The first deliverable is therefore a gate that checks both metrics separately,
not a large batch of easy tests.

## 2. Targets

| Phase | Statements | Branches | Combined |
| :--- | ---: | ---: | ---: |
| Baseline | 92.5 % | 85.3 % | 90.8 % |
| Gate + error paths | 94 % | 88 % | 92 % |
| Before P1 close | **95 %** | **90 %** | **93 %** |

Critical modules (`core/deploy.py`, `core/compile.py`, `metadata.py`,
`cli/commands/bump.py`, `hooks.py`) should reach **≥90 % branches** even if the
global metric is higher.

Do not set a global 100 % target: platform fallbacks, defensive exception paths
and unreachable compatibility branches would create brittle tests or unhelpful
`pragma: no cover` annotations.

## 3. Commit 1 — enforce the real gate

### `test: enforce line and branch coverage separately`

- Run coverage with machine-readable output:
  ```bash
  uv run pytest -q --cov=qgis_manager --cov-branch \
    --cov-report=json:coverage.json --cov-report=term-missing
  ```
- Add `scripts/check_coverage.py`:
  - reads `coverage.json`;
  - exits 1 if `totals.percent_statements_covered < 92.5`;
  - exits 1 if `totals.percent_branches_covered < 85.0`;
  - prints both values and the failing threshold.
- Wire it into CI and `forge.toml` `test_command_full` after pytest.
- Keep the existing combined gate during the transition; remove it only when the
  separate gate is stable.
- Publish `coverage.xml`/HTML as a CI artifact (optional but useful for review).

Initial thresholds are the current values rounded down, so the gate catches
regressions without forcing an immediate large patch. Raise them in Commit 5.
**Status**: ✅ Implemented 2026-10-25. Gate is 95.00 % statements / 90.00 %
branches; coverage is 96.55 % / 91.47 % with 331 tests, including P0 E2E
contracts. Shared fixtures were unnecessary because the E2E helpers are already
module-local and reused.

### Acceptance

- A deliberate branch regression fails CI even if combined coverage stays >90 %.
- Local `make test-cov`/documented command runs the same check.
- No production code changes.

## 4. Commit 2 — quick wins and CLI fallbacks

### Files and cases

| Target | Tests |
| :--- | :--- |
| `src/qgis_manager/__init__.py` | package metadata missing → `__version__` fallback; importlib metadata raises |
| `src/qgis_manager/cli/__init__.py` | `main()` direct entry, no args/help path |
| `src/qgis_manager/cli/app.py` | no subcommand, unknown command, `KeyboardInterrupt`, unexpected exception, `--version` |
| `src/qgis_manager/cli/parser.py` | parser without command, invalid subcommand, help formatting |
| `src/qgis_manager/cli/registry.py` | entry point import raises, entry point is not a `BaseCommand`, duplicate name (already covered) |
| `src/qgis_manager/cli/commands/clean.py` | tracked-file warning, `--dry-run`, `--keep-generated`, no Git |
| `src/qgis_manager/cli/commands/analyze.py` | analyzer missing, fallback `uv`, non-zero exit |
| `src/qgis_manager/cli/commands/security.py` | analyzer failure and missing binary |

### Design

- Use `CliRunner`/the existing `_CommandTestBase` harness.
- Assert exit code, stdout/stderr and side effects; not only “returns”.
- Patch `importlib.metadata.version`/`entry_points` at the narrowest scope.

### Expected gain

~12–15 statements and ~8 branches, mostly cheap and low-flake.

## 5. Commit 3 — core error paths (highest value)

### `core/deploy.py`

Add tests for:

1. Source symlink is skipped; destination symlink is removed.
2. Destination path is outside the plugins directory / same as parent → error.
3. Destination nested inside source → recursion guard.
4. `_is_same_or_nested` when `resolve()` raises → False fallback.
5. `_cleanup_destination` removes files/dirs absent from source, preserves
   ignored entries, removes destination symlinks.
6. Backup rotation keeps exactly N, purges all, handles `limit=0`.
7. Backup copy failure propagates without leaving a half-written backup.
8. Callback is called once with 100.

Use real `tmp_path` trees; mock only `get_plugin_metadata` and platform paths.

### `core/compile.py`

1. Missing pyuic/rcc/lrelease → clear False, no traceback.
2. `CompileContext.run` timeout / `FileNotFoundError` / `CalledProcessError`.
3. Docs failure preserves previous output; success replaces atomically.
4. Patch failure (`patch_ui_file`, `patch_resource_file`) returns False and logs.
5. No sources → no-op success; stale vs fresh source.
6. Failure aggregation: one failed file still runs the rest and returns False.
7. Invalid `jobs` value (0/negative) is normalized or rejected explicitly.

### `metadata.py` and `bump.py`

1. Empty/malformed metadata, missing `[general]`, latin-1 fallback.
2. Missing/unreadable pyproject and metadata.
3. Invalid/unsafe version; `bump sync` with no pyproject.
4. Metadata save failure leaves the original file intact.
5. Comments and multiline values preserved after update.

### `hooks.py`

1. Native import error, missing/non-callable hook, hook returns False.
2. Command timeout, non-zero exit, `shell=False` argv path.
3. Environment allowlist: `QGIS_PROJECT_ROOT` present, secret vars absent.

### Expected gain

~35–45 statements and ~25–30 branches; this is the main path to 90 % branches.

## 6. Commit 4 — validation, ignore and package contracts

### `validation/metadata.py`, `validation/structure.py`, `validation/repository.py`

- Missing required fields; invalid email/URL/version; prerelease; `True`/`False`.
- Unreadable `__init__.py`; missing icon/classFactory.
- `about`/`repository` missing; prohibited binary nested in an ignored dir.
- Repository scan does not follow symlinked directories.

### `ignore.py`

- Path outside project root; unreadable ignore file; empty patterns.
- Nested ignore file with a negation; deeper rule wins.
- Root `.qgisignore` precedence over `.gitignore`.
- Explain/check behavior once P2 adds it (test seam now).

### `core/package.py` and `package` command

- `--release-version` mismatch without `--stamp` (already covered); with
  `--stamp`; with `--sync-version`; missing metadata.
- Dependency install failure aborts before compliance.
- Repo check failure; checksum written; ZIP metadata bytes preserved.
- `--require-docs` once P2 adds it.

### Expected gain

~15 statements, ~12 branches; mostly behavior and contract clarity.

## 7. Commit 5 — raise gates and add contract/E2E

- Raise thresholds to **95 % statements / 90 % branches**.
- Add E2E CLI tests for:
  - two immediate deploys;
  - `compile --type resources --type translations`;
  - `deploy --purge-backups --yes`;
  - `clean --dry-run` and `--keep-generated`;
  - `package --release-version` mismatch;
  - Windows path/newline behavior in CI (already matrix-tested).
- Add a small `tests/conftest.py` fixture set:
  - `plugin_project` (metadata + pyproject + sample sources);
  - `mock_tool` for pyuic/rcc/lrelease;
  - `manifest_project` once P1 lands.
- Avoid duplicating fixtures already in command tests; migrate only shared setup.

### Expected gain

E2E tests add few new lines but catch integration regressions that unit coverage
misses; they are the safety net for P1.

## 8. P1 tests must ship with P1

When P1 lands, add coverage for:

- manifest missing/corrupt/partial schema;
- target changed with same size/mtime;
- failed deploy does not update manifest;
- manifest path traversal/symlink rejection;
- manifest excluded from packages;
- ignored directories pruned by `--repo-check`;
- reflink success/fallback/collision;
- identical compiled outputs not rewritten;
- fresh `.qm` skipped and stale `.qm` rebuilt.

Do not defer these to a later coverage pass; they are the highest-risk new code.

## 9. Test design rules

1. **Assert behavior, not just coverage**: exit code, message, filesystem state,
   callback sequence, subprocess argv.
2. **Real filesystem for filesystem logic**; mocks only for external tools,
   network and platform boundaries.
3. **Parametrize** valid/invalid variants instead of copy-pasting tests.
4. **Deterministic**: no sleeps, no wall-clock thresholds; use injected
   timestamps and fake tools.
5. **Isolated**: `tmp_path`, no writes to the repository, no real QGIS profiles.
6. **Cross-platform**: compare `Path` objects and bytes; avoid newline-sensitive
   string comparisons.
7. **No coverage theater**: no `# pragma: no cover` on business logic; no tests
   that only execute a line without asserting an outcome.
8. **Mutation testing is optional**: run `mutmut`/`cosmic-ray` manually on
   `core/deploy.py` and `metadata.py` once; do not gate CI on it.
9. **Property-based tests**: consider Hypothesis only for naming, version
   parsing and ignore matching; optional dev dependency, not runtime.

## 10. Suggested commit sequence

1. `test: enforce line and branch coverage separately`
2. `test: cover CLI fallbacks and registry errors`
3. `test: cover deploy and compile error paths`
4. `test: cover metadata, bump and hooks failures`
5. `test: cover validation, ignore and package contracts`
6. `test: add shared fixtures and E2E contracts`
7. `test: raise coverage gates to 95/90`
8. `chore(agent): record coverage results`

Each commit must keep the suite deterministic and under ~5 s locally.

## 11. Acceptance criteria

- Separate gate fails on a branch-only regression.
- Statements ≥95 %, branches ≥90 %, combined ≥93 %.
- Critical modules ≥90 % branches.
- No production code changes solely to satisfy coverage.
- No new runtime dependencies; optional Hypothesis only if approved.
- Existing 279 tests remain green; new tests are isolated and fast.
- P1 tests are included in the same P1 commits, not deferred.

## 12. Out of scope

- 100 % line/branch coverage.
- Coverage-driven rewrites of defensive code.
- Network/real-QGIS integration tests.
- Browser/GUI tests.
- Performance benchmarks as CI gates.

## 13. Approval

No code changes until this plan is approved. Start with Commit 1 (separate
gate), then proceed by risk order: CLI fallbacks → deploy/compile →
metadata/bump/hooks → validation/package → E2E and final thresholds.
