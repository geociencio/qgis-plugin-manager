# Zero Runtime Dependencies Plan — remove click

**Date**: 2026-11-01
**Baseline**: qgis-manage 0.15.1, 405 tests, 96.11 % statements / 90.11 % branches,
C901 = 0.
**Goal**: `qgis-manage` must run with the Python standard library only. Runtime
dependencies become an empty list; `click` moves out of the package entirely.

**Status**: implemented 2026-11-01; console adapter, click removal, policy test
and docs are in place. Release 0.16.0 pending.

## 1. Policy

- `project.dependencies = []`.
- Imports under `src/qgis_manager/` may use only:
  - the Python standard library;
  - `qgis_manager` itself.
- Dev-only tools (`pytest`, `ruff`, `mypy`, analyzer) stay in optional/dev
  dependencies and are never imported by runtime modules.
- External tools are invoked as subprocesses (`qgis-analyzer`, `sip`, `rcc`,
  `lrelease`, `git`, `uv`/`pip`), not imported.
- A test enforces the policy so a new runtime import cannot slip in.

## 2. Current footprint

`click` is the only runtime dependency and is used in 18 CLI modules for:

- `echo` / `style` (colored output);
- `confirm` / `prompt` (interactive input);
- `progressbar` (compile/package progress);
- error styling in `BaseCommand` and `CLIApp`.

`click` must be replaced by a small internal adapter, not by ad-hoc ANSI escapes
in every command.

## 3. Design: `qgis_manager/cli/console.py`

A stdlib-only module with a stable surface:

```python
def echo(message="", *, err=False) -> None
def style(text, fg=None, bold=False) -> str
def confirm(prompt, default=False) -> bool
def prompt(text, default="") -> str
@contextmanager
def progressbar(length, label="", show_pos=True) -> Iterator[ProgressBar]
```

Behavior:

- Color only when stdout is a TTY and `NO_COLOR` is not set; `TERM=dumb`
  disables color.
- `style` remains a pure formatter; commands can compose it.
- `confirm` uses `input()` and treats EOF/`KeyboardInterrupt` as abort; the
  caller decides whether abort is exit 0 or 1.
- `prompt` strips input and applies the default on empty/EOF.
- `progressbar` writes to stderr, uses `\r`, and exposes `.label` / `.update(n)`
  so `make_compile_callback` keeps working. Non-TTY emits no spinner noise.
- No new dependencies and no optional `colorama`.

## 4. Commit sequence

### Commit 1 — `feat(cli): add stdlib console adapter`

- Add `cli/console.py`.
- Add tests for echo/style/NO_COLOR, confirm/prompt EOF/defaults, progressbar
  TTY/non-TTY and label/update behavior.
- No command changes yet.

### Commit 2 — `refactor(cli): replace click output and prompts`

- Replace `import click` and `click.echo/style/confirm/prompt` in all command
  modules with the console functions.
- Keep argument parsing on `argparse`.
- Update test patch targets from `...click.confirm` to `...console.confirm` (or
  module-local imported symbol).
- Preserve all human output strings and exit codes.

### Commit 3 — `refactor(cli): replace click progressbar`

- Replace `click.progressbar` in `compile` and `package`.
- Ensure `make_compile_callback` accepts the adapter.
- Verify progress is on stderr and non-TTY output stays readable.
- Keep compile/package callbacks and counts unchanged.

### Commit 4 — `chore(deps): remove click and enforce zero runtime deps`

- Remove `click>=8.0` from `project.dependencies`.
- Regenerate `uv.lock`.
- Add `tests/test_dependency_policy.py`:
  - parse `pyproject.toml` and assert `project.dependencies == []`;
  - scan runtime imports under `src/qgis_manager` and reject non-stdlib,
    non-local top-level modules.
- Update README installation/runtime notes and pyproject description if needed.

### Commit 5 — `docs: document zero-dependency policy`

- README: “no runtime dependencies; click removed”.
- `docs/DEVELOPMENT_LOG.md`, changelog and release notes.
- Release **0.16.0** because removing a public dependency and changing the CLI
  internals is a minor breaking change.

## 5. Tests and acceptance

- Existing 405 tests pass.
- New console tests and policy test pass.
- `ruff`, `format`, `mypy`, coverage 95/90, C901 = 0.
- `uv build` wheel/sdist contain no `click` dependency; `pip install --no-deps`
  then `qgis-manage --version/help` works.
- `security --portal` still delegates via subprocess and never imports analyzer.
- No `import click` under `src/qgis_manager`.
- No third-party runtime import in the policy scan.

## 6. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Terminal output changes | Snapshot human strings; color only on TTY; NO_COLOR test |
| Prompt/EOF behavior changes | Explicit tests for EOF, empty input, default |
| Progressbar API mismatch | Adapter exposes `.label`/`.update`, same callback contract |
| Tests patch `click.*` | Mechanical update to console patch targets |
| Hidden third-party import | AST-based policy test |
| Release semantics | 0.16.0 minor, changelog migration note |

## 7. Out of scope

- Replacing `argparse` with another parser.
- Removing dev-only dependencies.
- Rewriting subprocess tool adapters.
- A full TUI/progress library.

## 8. Approval

This plan removes the only runtime dependency. No code is written until the plan
is approved; implementation starts with the console adapter and keeps each
commit green.
