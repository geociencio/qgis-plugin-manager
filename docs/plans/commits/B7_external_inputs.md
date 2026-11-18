# B7 — External input validation

**Status**: Planned
**Implementation commit**: pending
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
