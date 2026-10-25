# Maintenance Session: 2026-10-25 — P0/P1/P2 Platform Releases

## Technical Summary

Closed the 0.10.0 analysis remediation across three releases. P0 fixed deploy/compile/
package/clean footguns in 0.10.1; a risk-weighted coverage initiative replaced the
combined coverage gate with independent statement/branch gates; P1 added the pruned
repository scan, deploy manifest, reflink backups and compile freshness in 0.11.0;
P2 added JSON output, ignore explain, deploy dry-run, profiles, docs gating, max-cc
passthrough and non-shell hooks by default in 0.12.0.

All three releases were tagged, published on GitHub and uploaded to PyPI. The final
PyPI artifacts were verified byte-for-byte against a rebuild at the release tag.

## Changes Made

### 0.10.1 — P0 correctness

- Collision-safe deploy backups (microseconds + defensive suffix).
- Repeatable `compile --type` (resources + translations in one invocation).
- `package --release-version` consistency validation against `metadata.txt`.
- `deploy --yes` for non-interactive purge/create/deploy.
- `clean --dry-run`, `--keep-generated` and tracked-file warning.

### Coverage initiative

- `scripts/check_coverage.py` enforces statements ≥95 % and branches ≥90 % separately.
- Added CLI fallback, deploy/compile error, metadata/hook/bump, validation/ignore/
  package and P0 E2E tests.
- Coverage moved from 90.80 % combined / 85.33 % branches to **95.32 % combined /
  90.73 % branches** with **373 tests**.

### 0.11.0 — P1 performance

- One-pass, pruned `--repo-check` binary scan.
- `.qgis-manage/deploy-manifest.json` with `--no-manifest` fallback.
- Linux reflink backups with `copytree` fallback.
- UI/QRC temporary-output replacement and fresh `.qm` skip.

### 0.12.0 — P2 UX/safety

- JSON output for validate/analyze/package.
- `ignore check/explain`, `analyze --max-cc`, `deploy --dry-run`, `profiles list`,
  `package --require-docs`.
- Breaking: `HookPolicy(shell=False)` by default with migration error.

## Verification Results

| Gate | Result |
| :--- | :--- |
| Project tests | **373 passed** (+13 subtests) |
| Statements / branches | **96.77 % / 90.73 %** |
| Combined coverage | **95.32 %** |
| Gates | 95/90 |
| Ruff / format / strict mypy | Clean |
| C901 | 0 |
| Framework | 37 tests, validators clean |
| Releases | 0.10.1, 0.11.0, 0.12.0 published |
| PyPI | wheel + sdist hashes verified |

## Impact

The 0.10.0 findings are closed, the coverage gate now measures what it claims, and
P1/P2 platform controls are released. The only intentional compatibility break is
non-shell hook execution in 0.12.0; callers using shell syntax must opt in with
`HookPolicy(shell=True)`.

## Follow-up

No active project phase. Post-0.12 backlog: hook sandboxing, config-file shell policy,
global Git excludes, and formal benchmarks. Start with `/start-session`.

**Reference commits**: `f4e09ff`..`f6396ec` (P0), `0bf6e84`..`c918e12` (coverage),
`fe7b8dd`..`dd96cda` (P1), `0b23b9e`..`ad241d7` (P2), tags `v0.10.1`, `v0.11.0`,
`v0.12.0`.
