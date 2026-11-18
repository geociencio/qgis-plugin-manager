# B3 — PackageWorkflow

**Status**: Done
**Implementation commit**: `42cc861 refactor(package): add PackageWorkflow`
**State commit**: `d0d94b6 chore(agent): record B3 package workflow`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Remove the duplicated `create_plugin_package` call and make `package --json`
emit a valid envelope on every failure path.

## Procedure

1. Add `PackageRequest`, `PackageResult`, `PackageWorkflow` in `core/package.py`.
2. Route all package options through one request:
   - output, dev, stamp, release version, normalize permissions.
3. Replace the two `create_plugin_package` calls with one workflow call.
4. Keep progress callbacks for non-JSON mode.
5. Add `_failure()` in the command to emit `emit_json("package", False, ...)`
   for:
   - release version mismatch;
   - missing required docs;
   - dependency failure;
   - compliance failure;
   - artifact failure.
6. Add tests for workflow injection and JSON failure envelope.

## Files

- `src/qgis_manager/core/package.py`
- `src/qgis_manager/core/__init__.py`
- `src/qgis_manager/cli/commands/package.py`
- `tests/test_core_package.py`
- `tests/test_commands_package_hooks.py`

## Acceptance

- Exactly one `create_plugin_package` call per package operation.
- `normalize_permissions` is honored in JSON and progress modes.
- JSON failure always has schema/command/success/errors/data.
- Existing package/compliance tests pass.

## Evidence

- 444 tests passed at this stage.
