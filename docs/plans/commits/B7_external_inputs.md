# B7 — External input validation

**Status**: Done
**Implementation commit**: `6177d44 fix(security): validate external inputs`
**State commit**: `e5de15e chore(agent): record B7 input hardening`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Harden the remaining trust boundaries: dependency installation, template
selection, ZIP inspection, and analyzer process control.

## Procedure

1. **install-deps**
   - Validate each dependency as a PEP 508 requirement.
   - Reject entries beginning with `-`.
   - Insert `--` before dependency arguments.
   - Confine `--target` to the project root (reject absolute/`..` escapes).
2. **init --template**
   - Whitelist `default`, `processing`, `dockwidget`.
   - Resolve the template path and ensure it stays under `templates/`.
3. **ZIP inspection**
   - Enforce per-member and total uncompressed size limits before `zf.read`.
   - Keep the 25 MB compressed-size check.
4. **analyzer**
   - Cache the `qgis-analyzer --version` availability probe.
   - Add a configurable timeout to analyzer subprocesses.
5. Add negative tests for each boundary.

## Files

- `src/qgis_manager/dependencies.py`
- `src/qgis_manager/core/scaffold.py`
- `src/qgis_manager/validation/artifact.py`
- `src/qgis_manager/cli/analyzer.py`
- command tests for install/init/validate/security

## Acceptance

- Malicious/typo dependency strings cannot become pip options.
- Template traversal is rejected.
- ZIP metadata/icon reads are bounded.
- Analyzer cannot hang indefinitely.
- No runtime dependencies added.

## Planned tests

- `install-deps` with `--index-url` style entry.
- `init --template ../../...`.
- ZIP with oversized metadata/icon.
- Analyzer timeout and single availability probe.

## Execution result

- `is_valid_requirement()` rejects option-shaped, newline/NUL and underspecified
  requirement strings; valid names, extras, specifiers and markers are accepted.
- `install_external_libs()` validates every dependency **before** probing `uv`,
  rejects absolute/`..` targets, resolves the target inside the project, and
  builds `pip/uv install --target <dir> -- <deps>`.
- `_VALID_TEMPLATES` plus resolved-parent checks reject traversal and unknown
  templates.
- ZIP reads use `_read_member()` with a 5 MB member limit; total uncompressed
  size is capped at 100 MB before metadata/icon/license reads.
- Analyzer has a 300 s default timeout, returns 124 on timeout/start failure, and
  caches the availability probe. `tests/conftest.py` resets it per test.
- New tests: unsafe dependency, escaping target, separator, template traversal,
  oversized ZIP metadata, analyzer timeout and cache.

**Result**: 456 tests, 96.05 % statements, 90.08 % branches, 94.63 % combined;
C901 = 0.

**Files**: `dependencies.py`, `core/scaffold.py`, `validation/artifact.py`,
`cli/analyzer.py`, `tests/conftest.py`, and the corresponding test modules.
