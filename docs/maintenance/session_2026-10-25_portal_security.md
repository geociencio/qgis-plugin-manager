# Maintenance Session: 2026-10-25 — Portal Security

## Technical Summary

Closed the remaining qgis-manage side of the upstream gate integration. Added
configuration for artifact gates (`docs_entry`, size, icon, permissions), QGIS 4
and config-file checks, reproducible `SOURCE_DATE_EPOCH` timestamps, and the
`security --portal` orchestrator for qgis-plugin-analyzer 1.18.0.

Released `0.13.0` (artifact audit), `0.14.0` (configurable gates) and `0.15.0`
(portal security). All tags, GitHub releases and PyPI artifacts were verified.

## Changes Made

### 0.13.0 — artifact audit

- Added `validation/artifact.py` with stable `ARTIFACT_*` checks.
- Added `validate --zip`, JSON output, strict permissions and exit codes 0/1/2.
- `package --repo-check` audits the written ZIP and normalizes 0644/0755 modes.
- Artifact limit is 25 MB over the ZIP.

### 0.14.0 — configurable gates

- `docs_entry` (glob-capable), `max_package_size_mb`, `icon_min_px`,
  `normalize_permissions` in `[tool.qgis-manager]`.
- `ARTIFACT_QGIS4`, `ARTIFACT_CONFIG`, `SOURCE_DATE_EPOCH`.
- `validate --zip --max-size-mb/--icon-min-px` and configurable docs gate.

### 0.15.0 — portal security

- Bumped minimum analyzer to 1.18.0 (`--exclude`, `--scope`, `--tools`, `--json`).
- Added `security --portal`, repeatable `--exclude`, JSON envelope and
  `--fail-on`.
- Documented analyzer `[portal]` extras and ignore/scope behavior.

## Verification Results

| Gate | Result |
| :--- | :--- |
| Project tests | **405 passed** (+13 subtests) |
| Statements / branches | **96.11 % / 90.11 %** |
| Combined | **94.65 %** |
| Gates | 95/90 |
| Ruff / format / strict mypy | Clean |
| C901 | 0 |
| Framework | 37 tests, validators clean |
| Releases | 0.13.0, 0.14.0, 0.15.0 published |
| PyPI | wheel/sdist hashes verified |

## Impact

qgis-manage now validates what it actually ships, supports configurable portal
gates, and can orchestrate the real analyzer security tool set without
implementing AST analysis itself. Analyzer 1.18 provides scoped ignores and
`--exclude`; users must install `qgis-plugin-analyzer[portal]` and exclude
project-specific dev directories.

## Follow-up

No active qgis-manage phase. Remaining cross-repo work: SecInterp migration and
upstream analyzer refinements. Start with `/start-session`.

**Reference commits**: `cfc3a85` (0.13.0), `4204809`/`6489743` (0.14.0),
`46aa093`/`1659e14` (0.15.0), tags `v0.13.0`, `v0.14.0`, `v0.15.0`.
