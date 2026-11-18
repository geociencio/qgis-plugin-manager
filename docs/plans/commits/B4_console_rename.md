# B4 — Console rename

**Status**: Done
**Implementation commit**: `50594aa refactor(cli): rename console alias`
**State commit**: `2388191 chore(agent): record B4 console rename`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Remove the misleading `console as click` compatibility alias left after the
click removal, with no behavior change.

## Procedure

1. Replace `from .. import console as click` and
   `from . import console as click` with plain `console` imports.
2. Replace `click.echo/style/confirm/prompt/progressbar` with `console.*`.
3. Update test patch targets from `...click.confirm` to `...console.confirm`.
4. Update the progress helper docstring.
5. Add a regression test that rejects `console as click` and `click.` in
   `src/qgis_manager`.

## Files

- `src/qgis_manager/cli/base.py`
- `src/qgis_manager/cli/app.py`
- `src/qgis_manager/cli/json_output.py`
- `src/qgis_manager/cli/commands/*.py`
- `tests/test_console.py`
- command tests with patch paths

## Acceptance

- No `click` alias in production or tests.
- Behavior and output unchanged.
- 445 tests passed at this stage.
