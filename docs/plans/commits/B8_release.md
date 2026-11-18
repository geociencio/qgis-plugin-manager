# B8 — Release 0.17.0

**Status**: Done
**Implementation commit**: `893b67e chore(release): prepare v0.17.0`
**State commit**: `3a73f2c chore(agent): record v0.17.0 release`
**Tag commit**: `e0df140` (includes Windows portability test fixes)
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Publish the structural refactor as 0.17.0 after B1–B7 are green.

## Procedure

1. Bump minor: `0.16.2` → `0.17.0` with `qgis-manage bump minor`.
2. Update `uv.lock`, sync the dev environment.
3. Write `docs/releases/notes/v0.17.0.md` and changelog entries.
4. Regenerate help; update README version.
5. Refresh task/next_steps/AI context/metrics.
6. Run:
   - ruff check/format;
   - mypy;
   - full pytest + coverage 95/90;
   - C90 check;
   - distribution check.
7. Build wheel/sdist, run `scripts/check_distribution.py`, `twine check`.
8. Install the wheel with `--no-deps` and run `--version/--help`.
9. Commit release prep and state.
10. Push main, CI, tag `v0.17.0`, draft release, publish, wait PyPI.
11. Verify PyPI SHA256 for wheel and sdist.

## Acceptance

- Version 0.17.0 on GitHub and PyPI.
- Tag CI green (or a documented GitHub-capacity cancellation only).
- Wheel/sdist tool-only and hash-verified.
- Runtime dependencies still empty.
- Worktree clean.

## Rollback

Do not delete a published release. If a defect appears, cut 0.17.1 with a
changelog entry and the same verification gates.

## Execution result

- Bumped `0.16.2` → `0.17.0`, refreshed `uv.lock`.
- Added changelog/release notes and regenerated help.
- Gates: 456 tests, 96.05 % statements, 90.08 % branches, 94.63 % combined,
  C901 = 0.
- Wheel/sdist passed `check_distribution.py` and `twine check`.
- Wheel installed with `--no-deps`; `qgis-manage 0.17.0` runs without click.
- GitHub release and PyPI publication completed; wheel/sdist hashes verified.
- Tag CI completed successfully; main CI had macOS capacity queueing only.
