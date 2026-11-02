# Maintenance Session: 2026-11-01 — Correctness Patch

## Technical Summary

Closed the v0.15.1 code-analysis findings with a patch release. The session also
completed the zero-runtime-dependency release started earlier the same day:
`0.16.0` removed `click`; `0.16.1` fixed the manifest, clean, SemVer, validation
and compile defects.

## Changes Made

### 0.16.0 — zero runtime dependencies

- Added `qgis_manager/cli/console.py` (echo/style/confirm/prompt/progress) using
  only the standard library.
- Removed `click` from runtime dependencies; `project.dependencies = []`.
- Added console tests and an AST policy test that rejects third-party runtime
  imports.

### 0.16.1 — correctness patch

- `DeployManifest` keeps a full target map and saves only the current target,
  preserving multi-profile/QGIS caches.
- `clean` walks with pruning for `.venv`, `env`, `libs`, `.git`,
  `node_modules`, `build` and `dist`; project caches still removed.
- `bump` parses `major.minor.patch` with a regex, accepting prerelease and extra
  components.
- Artifact validation accepts a `README` file without extension.
- Structure validation detects imported/aliased/multiline `classFactory` with
  AST plus regex fallback.
- Fresh `.qrc` outputs skip RCC; compile label is English.

## Verification Results

| Gate | Result |
| :--- | :--- |
| Project tests | **426 passed** (+13 subtests) |
| Statements / branches | **96.11 % / 90.33 %** |
| Combined | **94.70 %** |
| Gates | 95/90 |
| Ruff / format / strict mypy | Clean |
| C901 | 0 |
| Runtime dependencies | 0 (`click` absent in clean venv) |
| Distribution | wheel/sdist tool-only |
| Releases | 0.16.0 and 0.16.1 published |
| PyPI | wheel/sdist hashes verified |

## Impact

Multi-target deployments no longer lose manifest cache entries, `clean` no
longer degrades virtualenvs, and version/validation/compile edge cases behave
predictably. The package remains stdlib-only.

## Follow-up

No active phase. Remaining work: B2 scaffold recursion/`pyproject.toml.tmpl`
(feature, 0.17.0), SecInterp migration and upstream analyzer refinements.
Start with `/start-session`.

**Reference commits**: `87db104` (fixes), `d666b24` (release prep), `ba11887`
(tag state), tag `v0.16.1`.
