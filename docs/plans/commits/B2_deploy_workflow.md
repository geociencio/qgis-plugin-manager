# B2 — DeployWorkflow

**Status**: Done
**Implementation commit**: `0d0b12c refactor(deploy): add DeployWorkflow`
**State commit**: `77baebb chore(agent): record B2 deploy workflow`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Move deployment planning/execution out of the CLI command, introduce explicit
request/plan/result types, and remove the double purge confirmation.

## Procedure

1. Add `DeployRequest`, `DeployPlan`, `DeployResult` in `core/deploy.py`.
2. Add `prepare_deploy()`:
   - reads metadata through an injected reader;
   - validates slug and target path;
   - refuses symlink targets and paths outside the target dir.
3. Add `DeployWorkflow` with injectable `metadata_reader` and `deploy` callables.
4. Refactor `DeployCommand.execute` to build the workflow and plan.
5. Extract interactive flow to `_execute_plan`:
   - purge, ensure directory, hooks, confirm, compile, deploy, post-hook.
6. Change `_purge_backups` to ask once; `--yes` does not ask.
7. Add workflow tests and update the purge-abort test.

## Files

- `src/qgis_manager/core/deploy.py`
- `src/qgis_manager/core/__init__.py`
- `src/qgis_manager/cli/commands/deploy.py`
- `tests/test_core_deploy.py`
- `tests/test_commands_deploy.py`

## Acceptance

- `DeployCommand.execute` is under 30 lines.
- One purge confirmation, not two.
- `deploy_plugin` is still injectable and tests patch the command boundary.
- Existing deploy/dry-run/hook/compile tests pass.

## Evidence

- `execute` measured at 29 lines with AST.
- 442 tests passed at this stage.
