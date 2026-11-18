# B5 — Typed error boundary

**Status**: Done
**Implementation commit**: `156e533 refactor(cli): add typed error boundary`
**State commit**: `af84b98 chore(agent): record B5 error boundary`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Stop converting unexpected bugs into generic exit-1 errors and give users a
debug path without changing expected CLI failures.

## Procedure

1. Add `qgis_manager/cli/errors.py` with `CliError(message, exit_code=1)`.
2. `BaseCommand.run` catches only `CliError`, prints once and returns its code.
3. `BaseCommand.project_root` wraps `FileNotFoundError` in `CliError`.
4. `CLIApp.run`:
   - catches `CliError` (defensive);
   - catches unexpected exceptions, logs them and prints a concise error;
   - prints traceback only with `--debug`.
5. Add global `--debug`; logging becomes DEBUG when set.
6. Add tests for exit code 2 and debug traceback.

## Files

- `src/qgis_manager/cli/errors.py`
- `src/qgis_manager/cli/base.py`
- `src/qgis_manager/cli/app.py`
- `tests/test_cli.py`

## Acceptance

- Expected `CliError` keeps its exit code.
- Unexpected exceptions do not print traceback by default.
- `--debug` prints traceback.
- 447 tests passed at this stage.
