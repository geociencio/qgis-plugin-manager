# B6 — Atomic TOML updates

**Status**: Done
**Implementation commit**: `a405927 fix(toml): write versions atomically`
**State commit**: `1b8cab7 chore(agent): record B6 atomic TOML`
**Parent plan**: `../v0.17.0_refactor_plan.md`

## Goal

Make pyproject version edits atomic and accept both TOML quote styles without
introducing an import cycle.

## Procedure

1. Move `write_text_atomic` from `metadata.py` to `atomic.py`.
2. Re-export it from `metadata.py` so existing patches keep working.
3. Use `write_text_atomic` in `set_project_version`.
4. Extend the version-line regex to capture `'` or `"` and preserve the quote.
5. Add tests:
   - single-quote version with trailing comment;
   - atomic write failure leaves the original file intact.

## Files

- `src/qgis_manager/atomic.py`
- `src/qgis_manager/metadata.py`
- `src/qgis_manager/toml_utils.py`
- `tests/test_toml_utils.py`

## Acceptance

- Version replacement is atomic.
- Both quote styles work.
- Comments and unrelated TOML remain untouched.
- 449 tests passed at this stage.
