# Test Coverage Implementation Plan

Add tests to close the coverage gaps identified in the analysis (61% global coverage).
Follows existing conventions: `unittest.TestCase` (pytest-compatible), `tempfile` for
filesystem, `unittest.mock.patch` for mocks, and `CLIApp().run(args)` for command tests.

## P1 — New modules from Phase 2 (regression safety)

- **`tests/test_toml_utils.py`** (new)
  - `load_toml`: valid -> dict; missing file -> `{}`; malformed -> `{}`.
  - `get_project_version`: with `[project] version` -> string; missing -> `None`.
  - `set_project_version`: updates and preserves comments/other sections; missing file
    -> `False`; no `[project]` -> `False`; no `version` line -> `False`.
- **`tests/test_progress.py`** (new)
  - `make_compile_callback` with a fake bar: `START:`/`PROGRESS:`/`DONE:` branches and icon
    selection per resource type.
- **`tests/test_discovery.py`** (extend)
  - `sync_metadata_version`: sync from pyproject; already in sync -> `False`; no version -> `False`.
  - `save_plugin_metadata`: round-trip; does not persist `slug`.

## P2 — Untested CLI commands

- **`tests/test_bump.py`** (new): `patch/minor/major`, `sync`, invalid version, no subcommand.
- **`tests/test_commands.py`** (new, grouped): `deploy`, `package`, `validate`, `hooks`,
  `analyze`, `clean`, `install-deps` via `CLIApp.run` with mocked `find_project_root` and
  underlying core functions.
- **`tests/test_dependencies.py`** (new): `get_dependencies` and `install_external_libs`
  (uv vs pip fallback, success/failure).

## P3 — Partially covered core functions

- **`tests/test_core.py`** (extend): `create_plugin_package` (ZIP + SHA256), `sync_directory`
  self-recursion safeguard, `rotate_backups` `limit<=0`, `count_compile_steps`.
- **`tests/test_validation.py` / `test_validation_deep.py`** (extend):
  `validate_official_compliance` (binaries/LICENSE), `validate_category`, `validate_tags`,
  `validate_boolean_field`.

## Verification

```bash
uv run ruff check .
uv run mypy src
uv run python -m unittest discover tests
uv run pytest -q
uv run --with coverage coverage run -m pytest -q
uv run --with coverage coverage report --include='src/qgis_manager/*'
```

Target: raise coverage from ~61% to ~85%+.
