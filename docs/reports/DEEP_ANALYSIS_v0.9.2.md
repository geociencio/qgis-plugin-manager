# Deep Analysis Report — QGIS Plugin Manager (qgis-manage v0.9.2)

**Scope**: repository-wide technical audit — architecture, correctness, data-safety,
testing, security, packaging, release automation and documentation drift.

**Source**: `qgis-plugin-manager/`, branch `main`, commit `939b750`,
`version = "0.9.2"`, working tree clean.

**Environment**: Python 3.12.12 (`.venv`), Linux. `uv`'s cache was read-only in the
audit sandbox, so the quality gates were executed through `.venv` binaries.

**Method** (read-only, no source changes):

| Step | What was done |
| :--- | :--- |
| Static review | Read all 36 `src/` modules, tests, `pyproject.toml`, CI, scaffold and docs |
| Quality gates | `ruff`, `ruff format --check`, `mypy`, full `pytest` with line/branch coverage |
| Build check | `uv build`; inspected wheel contents; ran `init` from the extracted wheel |
| Behaviour probes | Reproduced risky operations in throwaway directories (deploy, dclean, bump, compile, validate, ignore) |
| Extra lint | `ruff --select C90` (complexity) and `ruff --select S` (security) |

**Status in one line**: solid engineering hygiene (green gates, 190 tests, 90 % line
coverage, automated release), but **functional reliability is not at the same level**:
two data-loss defects and several high-severity failures survive because the test suite
mocks exactly the risky seams.

---

## 1. Verified quality gates

| Gate | Command | Result |
| :--- | :--- | :--- |
| Lint | `ruff check .` | **PASS** — 0 errors |
| Format | `ruff format --check .` | **PASS** — 57 files |
| Types | `mypy src` | **PASS** — 36 files |
| Tests | `pytest -q` | **PASS** — 190 passed in ~1.0 s |
| Line coverage | `--cov=qgis_manager` | **89.93 %** (1,738 stmts, 175 missed) |
| Branch coverage | `--cov-branch` | **87.99 %** (560 branches, 75 partial) |
| Build | `uv build` | **PASS** — `qgis_manage-0.9.2` wheel + sdist |
| Wheel smoke | extract wheel, run `init` | **PASS** — 14 template files shipped, project created |
| Complexity | `ruff --select C90` | `deploy.execute` **CC 20** (>10); `validate.execute` **CC 11** |
| Security lint | `ruff --select S` | 15 findings (7×S603, 5×S607, 2×S110, 1×S108 in tests) |

Lowest-covered modules: `cli.py` 0 % (dead module), `__init__.py` 54.5 %,
`cli/__init__.py` 66.7 %, `core/compile.py` 80.9 %, `ignore.py` 81.4 %.

---

## 2. Architecture assessment

### 2.1 Strengths

- **Clear layering**: `cli/` (argparse + presentation) → `core/` (deploy, package,
  compile, cleanup, scaffold) with shared modules (`discovery`, `ignore`, `validation`,
  `hooks`, `config`, `toml_utils`).
- **Recent `core.py` split** into cohesive submodules is a real improvement; the
  `core/__init__.py` re-export keeps backward compatibility for imports and tests.
- **Minimal runtime dependency**: only `click>=8.0`; everything else is standard
  library. The template renderer and ignore matcher are small and dependency-free.
- **`stamp_metadata_text` is the right pattern**: line-oriented editing that preserves
  comments/formatting. The problem is that `bump`/`sync` do not use it (see C2).
- **Good CI foundation**: 3 OS × 3 Python versions, coverage gate, format gate,
  conventional commits, changelog and release notes.

### 2.2 Weaknesses

- **The CLI layer is not thin**, despite `AGENTS.md` claiming it is.
  `cli/commands/deploy.py::execute` has CC 20 and mixes destination resolution,
  prompts, hooks, compilation and deployment; `validate.execute` also exceeds the
  threshold. Extract an application service (e.g. `DeployService`) and keep the
  command as parse → dispatch → render.
- **Two template systems exist.** The CLI reads `src/qgis_manager/templates/`
  (`core/scaffold.py:27`); the repository-root `scaffold/` is not referenced by any
  code and is excluded from the sdist. `AGENTS.md:102` states that the CLI injects
  `scaffold/`, which is inaccurate.
- **Dead module**: `src/qgis_manager/cli.py` is shadowed by the `cli/` package
  (verified: `qgis_manager.cli` resolves to `cli/__init__.py`). It is 0 % covered and
  its `from .cli import main` would self-import if it were ever loaded.
- **Typing is weaker than the stated standard**: no `py.typed`, `mypy` is not strict,
  12 functions lack return annotations and 3 lack parameter annotations (AST scan of
  150 functions). `mypy` passes because it is configured permissively.

---

## 3. Critical findings (data loss)

### C1 — Empty slug wipes unrelated plugins (`deploy`) or the whole plugins directory (`dclean`)

**Evidence**

- `slugify()` (`src/qgis_manager/discovery.py:41-53`) strips every non-word character
  and can return `""` (e.g. `name=!!!`).
- `uninstall_plugin()` (`src/qgis_manager/core/deploy.py:32-37`) builds
  `plugins_dir / ""` and calls `shutil.rmtree(...)`.
- `deploy_plugin()` (`src/qgis_manager/core/deploy.py:142-171`) uses `dest_dir / ""`
  as the target, and `_cleanup_destination()` (`src/qgis_manager/core/deploy.py:86-100`)
  deletes every destination entry that does not exist in the source.

**Reproduced**

```text
slug repr: ''
dest before: ['other_plugin']
dest after : ['metadata.txt', 'plugin.py']
other plugin survived: False

uninstall -> removed .../profiles/default/python/plugins
plugins dir still exists: False
```

**Impact**: silent destruction of other installed plugins, or of the entire QGIS
profile plugins directory.

**Fix**: validate the slug against `^[a-z0-9_]+$` and reject empty; refuse when
`target_path == dest_dir`; refuse `uninstall` for an empty/unsafe slug. Add tests for
`deploy` and `dclean` with names `!!!`, `My-Plugin`, `123`.

### C2 — `bump` and `--sync-version` destroy `metadata.txt`

**Evidence**

- `save_plugin_metadata()` (`src/qgis_manager/discovery.py:126-147`) re-parses with
  `configparser` and rewrites the file containing **only** `[general]`.
- Callers: `bump` (`src/qgis_manager/cli/commands/bump.py:180-210`),
  `sync_metadata_version()` (`src/qgis_manager/discovery.py:150-170`) and
  `package --sync-version` (`src/qgis_manager/cli/commands/package.py:67-71`).

**Reproduced**

```text
--- BEFORE ---              --- AFTER ---
[general]                   [general]
# comment that matters      name=Demo
name=Demo                   description=Demo plugin
version=1.2.3               version=1.2.4
[custom]                    ...
keep=this-section           ([custom] and the comment are gone)
```

**Impact**: loss of comments, custom sections, ordering and formatting on every bump or
version sync.

**Fix**: implement `update_metadata_text()` as a line-oriented, atomic writer (reuse the
approach already used by `stamp_metadata_text`) and use it for `bump`, `sync` and
`package --sync-version`. Add a test that compares the whole file, including comments
and a custom section.

---

## 4. High-severity findings

### H1 — `--purge-backups` is a no-op

`rotate_backups()` returns immediately when `limit <= 0`
(`src/qgis_manager/core/deploy.py:40-43`), yet the command calls it with `limit=0`
(`src/qgis_manager/cli/commands/deploy.py:96`) and prints "Backups purged". Reproduced:
two backups survived. The existing test mocks `rotate_backups`
(`tests/test_commands.py:394`), so it cannot catch this.
**Fix**: add a dedicated `purge_backups()` (or make `limit=0` mean "delete all") and test
actual deletion without mocks.

### H2 — `init` generates syntactically invalid Python

`class_name = name.replace(" ", "")` (`src/qgis_manager/core/scaffold.py:21-22`) does not
sanitize hyphens, parentheses or leading digits; the template inserts it directly as an
identifier (`src/qgis_manager/templates/default/__init__.py.tmpl:7-8`). Reproduced with
`"My-Weird Plugin (Ñ)"`: `SyntaxError` at line 7 of `__init__.py` and at line 5 of the
plugin module. The slug also keeps non-ASCII characters.
**Fix**: derive a valid ASCII PascalCase identifier from the slug, prefix `_` when it
starts with a digit, and `ast.parse` every generated `.py` in tests for several names and
all three templates.

### H3 — UI compilation does not patch PyQt6 imports

`get_uic_tool()` prefers `pyuic6` (`src/qgis_manager/core/compile.py:84-90`), but
`patch_ui_file()` only replaces `PyQt5`, `PySide2` and `PySide6`
(`src/qgis_manager/core/compile.py:200`). Reproduced: the generated module kept
`from PyQt6 import QtCore, QtGui, QtWidgets`, which fails inside QGIS. The test covers
only PySide6 (`tests/test_core.py:482`).
**Fix**: include `PyQt6` (better: a regex for `from (PyQt5|PyQt6|PySide2|PySide6)`) and
add a test for pyuic6 output.

### H4 — `compile` exits 0 on failure and deletes existing documentation

`compile_docs()` removes `help/html` before invoking Sphinx and swallows every exception
(`src/qgis_manager/core/compile.py:52-72`); `_compile_single_qrc()` only logs errors
(`src/qgis_manager/core/compile.py:284-285`); the command always prints
"Compilation complete" and returns 0 (`src/qgis_manager/cli/commands/compile.py:58`).
Reproduced with an invalid `.qrc` and with a Sphinx failure: `EXIT: 0`, and `help/html`
left empty.
**Fix**: aggregate failures and return a non-zero exit code; build docs into a temporary
directory and move atomically on success; never delete the previous docs before a
successful build.

### H5 — The configured `profile` is ignored

`add_common_args()` sets `default="default"` for `--profile`
(`src/qgis_manager/cli/base.py:48-53`), so `args.profile or settings.profile`
(`src/qgis_manager/cli/commands/deploy.py:79-81`) never reads the global or project
configuration. Reproduced: config `profile="production"` still deployed to
`profiles/default`. Same bug in `dclean`
(`src/qgis_manager/cli/commands/dclean.py:53-54`). `qgis_version` works because its
default is `None`.
**Fix**: use `default=None` and resolve `args.profile or settings.profile`, then apply
the final default; test both config sources.

### H6 — Boolean validation always warns

In `src/qgis_manager/validation.py:341-347` the warning is emitted whenever the field has
any value, including valid `"True"`/`"False"`; `validate_boolean_field()` is never called
in production. Reproduced: `experimental=False` →
"should be 'True' or 'False'. Found: 'False'".
**Fix**: call `validate_boolean_field()` and warn only on invalid values.

### H7 — `package --repo-check` checks before installing dependencies

Compliance runs first (`src/qgis_manager/cli/commands/package.py:74-99`), then
`install_external_libs()` (`src/qgis_manager/cli/commands/package.py:101-102`), then the
ZIP is built. Any `.so`/`.dll` installed into `libs/` enters the package **after** the
check that forbids binaries. The return value of `install_external_libs()` is ignored.
**Fix**: install first (or not at all) and validate the final file set; treat install
failure as fatal.

### H8 — `--repo-check` has false positives and weaker rules than advertised

`validate_official_compliance()` scans the whole tree without `IgnoreMatcher`
(`src/qgis_manager/validation.py:186-194`): a `.venv` containing `.so` fails the check
(reproduced). `get_required_fields()` (`src/qgis_manager/validation.py:55-62`) does not
require `about`, `tracker`, `repository`, `tags` or `category`; `homepage`/`repository`/
`tags` are only warnings (`src/qgis_manager/validation.py:320-330`), so
`package --repo-check` can pass a plugin the official repository would reject.
**Fix**: reuse the ignore matcher, ignore dev directories, and promote the fields the
official repository requires to errors in `--repo` mode.

### H9 — Deploy follows symlinks

`sync_directory()` iterates and recurses without checking `is_symlink()`
(`src/qgis_manager/core/deploy.py:109-123`), unlike packaging
(`src/qgis_manager/discovery.py:188`). Reproduced: a symlink to the parent directory
raises `OSError: [Errno 40] Too many levels of symbolic links`; without a loop, external
trees would be copied into the plugin.
**Fix**: skip symlinks (or require an explicit `--follow-symlinks`), and add a loop test.

### H10 — A freshly scaffolded project fails the tool's own `--repo-check`

The template declares `icon=icon.png`
(`src/qgis_manager/templates/default/metadata.txt.tmpl:15`) but no icon is generated,
and no `LICENSE` is copied; `scaffold` only renders `*.tmpl`
(`src/qgis_manager/core/scaffold.py:56-60`). Reproduced: `validate --repo` exits 1 for a
missing `LICENSE` and warns about the missing icon. The template's `version=0.1` is not
`X.Y.Z` either.
**Fix**: ship `LICENSE` and `icon.png` in the templates (or don't declare `icon`), use a
semver version, and add an "init → validate --repo" test.

### H11 — The `ignore` configuration documented in the README does not work

The README shows `[tool.qgis-manager.ignore]` with an inner `ignore = [...]` list
(`README.md:257-261`), but the code reads a list directly under `[tool.qgis-manager]`
(`src/qgis_manager/ignore.py:77-81`). Reproduced: with the README form the pattern is not
loaded (file not excluded); the flat `ignore = [...]` form works.
**Fix**: support both shapes or correct the README; add a config-parsing test.

### H12 — Dangerous trust model for untrusted repositories

- `deploy` automatically executes `plugin_hooks.py` when it exists
  (`src/qgis_manager/hooks.py:12-60`).
- `hooks list` imports and executes the module just to enumerate functions
  (`src/qgis_manager/cli/commands/hooks.py:91`).
- Configured hooks run with `shell=True` (`src/qgis_manager/hooks.py:98-106`).
- `package` automatically runs `uv pip install` with dependencies from the project's
  `pyproject.toml` (`src/qgis_manager/dependencies.py:24-57`, called at
  `src/qgis_manager/cli/commands/package.py:102`). Dependency strings can also inject
  pip options (e.g. `--index-url`).

Running `qgis-manage deploy/package` on a cloned third-party repository is therefore
equivalent to executing arbitrary code, with no confirmation or opt-out.
**Fix**: document the trust model, require confirmation/`--trust` before executing project
code or installing dependencies, show the exact commands, validate dependencies with
`packaging.requirements`, and never execute hooks from a read-only command such as
`hooks list`. (Ruff `S603/S607/S110` already flag part of this.)

### H13 — Windows ZIP entries likely use backslashes

`arcname` is built with `str(Path)` (`src/qgis_manager/core/package.py:177`); on Windows
that produces `\`, and `zipfile` does not normalize it to `/`. The Windows CI job does not
assert `arcname` values.
**Fix**: `arcname.replace(os.sep, "/")` and add a Windows-safe test that inspects
`ZipFile.namelist()`.

### H14 — Aborting a prompt prints an empty error

`CLIApp.run()` catches every `Exception` (`src/qgis_manager/cli/app.py:169-178`),
including `click.Abort`, and prints `❌ Error: ` with no message and exit code 1.
Reproduced when declining the profile-creation prompt.
**Fix**: handle `click.Abort`/`EOFError` explicitly (clean message, exit code 130 or 0)
before the generic handler.

---

## 5. Medium-severity findings

| # | Area | Finding | Evidence |
| :--- | :--- | :--- | :--- |
| M1 | Dead code / typing | Shadowed `cli.py`; no `py.typed`; permissive `mypy`; dead `get_ignore_func`, `get_optional_fields`, `validate_boolean_field` in production | `src/qgis_manager/cli.py:27`, `pyproject.toml:99-104` |
| M2 | Error handling | 30 broad `except Exception`; `load_toml` returns `{}` on malformed TOML, hiding configuration errors | `src/qgis_manager/toml_utils.py:18-22` |
| M3 | Tests | High coverage but mock-heavy: `rotate_backups`, `get_qgis_plugin_dir`, `load_config` and `patch_ui_file` are mocked at the exact failure points; no end-to-end deploy/package/wheel tests | `tests/test_commands.py:394`, `tests/test_core.py:482` |
| M4 | Docs drift | `help/` generated at v0.9.0; README help sample says v0.8.0; `docs/CHANGELOG.md` lacks the 0.7.0 section; `AGENTS.md` misdescribes `scaffold/` | `help/index.md:4`, `README.md:119`, `AGENTS.md:102` |
| M5 | Tooling | `make test` uses `unittest discover`; `make lint` uses `mypy .`; `make format` only runs `ruff check --fix`; pre-commit pins ruff 0.8.6 vs 0.14.10 | `Makefile:6-15`, `.pre-commit-config.yaml:11` |
| M6 | Config | `~/.config` hardcoded (no XDG/APPDATA); global `hooks` never loaded; `APPDATA` can raise `KeyError` | `src/qgis_manager/config.py:19-33`, `src/qgis_manager/core/platform.py:22-26` |
| M7 | Ignore semantics | No `!negation`, only the first `.qgisignore`/`.gitignore`, no nested ignore files | `src/qgis_manager/ignore.py:56-71` |
| M8 | Compilation | `rglob` scans `.venv`, `libs` and nested copies; subprocesses have no timeout | `src/qgis_manager/core/compile.py:222,292,333` |
| M9 | Cleanup | `clean` deletes `*.qpj`/`*.cpg`, which are QGIS data sidecars, not build artifacts | `src/qgis_manager/core/cleanup.py:19-25` |
| M10 | Release | `body_path` expects `vX.Y.Z.md`, but v0.7.0/v0.8.0/v0.9.0 only have `RELEASE_NOTES_v*.md`; a tag without notes breaks the workflow; no tag/pyproject version check and no test job dependency before publishing | `.github/workflows/release.yml:30-31` |
| M11 | Packaging | Existing ZIP overwritten silently; `--release-version` may contain `/` or `..`; every `package` run reinstalls dependencies | `src/qgis_manager/core/package.py:246-248` |
| M12 | Hooks | `post_deploy` result ignored (unlike `pre_deploy`); declining the interactive hook still runs the native hook | `src/qgis_manager/cli/commands/deploy.py:184-192` |
| M13 | Versions | `validate_version` accepts `X.Y` for the plugin version (message says `X.Y.Z`) and has a malformed range `[0-zA-Z0-9-]`; `bump` cannot handle prereleases (`3-rc1` → `int()` error) | `src/qgis_manager/validation.py:86-101`, `src/qgis_manager/cli/commands/bump.py:107-117` |
| M14 | Project root | `find_project_root` climbs to `/` and may select a monorepo parent `pyproject.toml`; no `--project` override | `src/qgis_manager/discovery.py:56-75` |
| M15 | Structure validation | `classFactory` detected by substring search (can match a comment); "very few .py files" is heuristic | `src/qgis_manager/validation.py:229-260` |
| M16 | Incremental sync | `_needs_copy` compares only size + mtime; a content change with the same size and preserved mtime is not copied | `src/qgis_manager/core/deploy.py:75-83` |
| M17 | Dev deps | `dev` duplicated in `[project.optional-dependencies]` and `[dependency-groups]` with different lists; `types-setuptools` appears unused | `pyproject.toml:43-52`, `pyproject.toml:107-115` |
| M18 | i18n | Classifier "Natural Language :: Spanish" while CLI, help and docs are English; no gettext | `pyproject.toml` |
| M19 | Repo hygiene | Untracked/stale `analysis_results/` (score 22.9, 2026-09-06) and `generator_export/`; empty `.ai-context/`; root `metadata.txt` ignored but present | `.gitignore` |

**Minor debt**: fallback for Python <3.8 in `__init__.py` (requires >=3.11); no
`__main__.py`; `--verbose` counts above 1 have no effect
(`src/qgis_manager/cli/app.py:77-83,132-136`); `post_deploy` failures are silent.

---

## 6. Testing assessment

The suite is fast (190 tests in ~1 s), clean and broad on lines/branches, but it is
**wiring-oriented**:

- Command tests assert that services were called, not what they did. Example: the purge
  test patches `rotate_backups` and asserts the message
  (`tests/test_commands.py:394-423`).
- Deploy tests patch `get_qgis_plugin_dir`, `load_config` and `deploy_plugin`, so config
  precedence and destination resolution are never exercised end-to-end
  (`tests/test_commands.py:330-390`).
- `patch_ui_file` is tested only with PySide6 (`tests/test_core.py:482-490`).
- `stamp_metadata_text` has good preservation tests; the same tests are **missing** for
  `save_plugin_metadata`/`bump`, which is why C2 survives.
- No test builds/installs the wheel, inspects ZIP `arcname`s, runs on Windows paths, or
  performs a real deploy into a temporary profile.
- Branch coverage is not enforced in CI (`--cov-branch` is absent from the workflow).

**Missing tests (highest value)**: empty/unsafe slug for deploy+dclean; metadata
preservation through bump/sync; purge actually deleting; `ast.parse` of every generated
template; pyuic6 import patching; compile failure exit code; config precedence
(global/project/CLI); nested-ignore config; wheel install + `init`; ZIP names on Windows.

---

## 7. Security and trust model

The tool intentionally executes project code and installers. That is acceptable for a
developer CLI, but the contract is neither documented nor gated:

1. **Arbitrary code execution**: `plugin_hooks.py` runs on deploy (and is imported by
   `hooks list`); configured hooks use `shell=True`.
2. **Supply chain**: `package` runs `uv pip install` with dependencies read from the
   project's `pyproject.toml`, without confirmation; requirement strings can inject pip
   options.
3. **Path handling**: an empty/unsafe slug can target the whole plugins directory (C1);
   `--template` accepts absolute paths/`..` (`src/qgis_manager/core/scaffold.py:27-29`);
   `--release-version` can contain path separators in the ZIP name.
4. **Static findings**: `ruff --select S` reports 7×S603, 5×S607, 2×S110. Most are
   expected for a build tool, but they should be triaged, not ignored.

**Recommendation**: document a trust model ("only run on repositories you trust"),
require `--trust`/confirmation before project code or installers run, display the exact
commands, validate requirements with `packaging.requirements`, and keep read-only
commands (`hooks list`, `validate`, `analyze`) side-effect free.

---

## 8. Documentation, release and repository hygiene

- Documentation volume is a strength (guides, plans, session logs, release notes), but
  it has drifted from code: help v0.9.0 vs package 0.9.2; README sample v0.8.0;
  `docs/CHANGELOG.md` missing 0.7.0; `AGENTS.md` describes the root `scaffold/` as
  injected by the CLI; README `ignore` syntax unsupported.
- Release automation is a good design but brittle: note filenames are inconsistent
  (`RELEASE_NOTES_v*.md` vs `v*.md`), a missing notes file is not handled by
  `fail_on_unmatched_files` (that option applies to `files`, not `body_path`), tags are
  not checked against `pyproject.toml`, and PyPI publication does not wait for CI.
- `dist/`, `.coverage`, `analysis_results/`, `generator_export/` and caches are correctly
  ignored, but stale untracked artifacts remain in the workspace.
- Generated `help/` should be regenerated in CI (and asserted clean) or derived at
  release time so it cannot drift.

---

## 9. Prioritized roadmap

### P0 — before the next release

| # | Action | Why |
| :--- | :--- | :--- |
| 1 | Safe slug + `target != dest` guard, with deploy/dclean tests | Prevent data loss (C1) |
| 2 | Line-oriented atomic metadata writer reused by bump/sync | Prevent data loss (C2) |
| 3 | Real `purge_backups()` + behavioural test | Silent no-op (H1) |
| 4 | Identifier sanitization + `ast.parse` template tests | Broken `init` output (H2) |
| 5 | PyQt6 patching; compile failure propagation; atomic docs build | Broken compilation (H3, H4) |
| 6 | `--profile` default `None` + precedence test | Config ignored (H5) |
| 7 | Boolean/version validation fixes | False warnings/acceptance (H6, M13) |
| 8 | Compliance after installs; ignore-aware binary scan; stricter required fields | Invalid packages (H7, H8) |

### P1 — reliability and trust

- Skip symlinks in `sync_directory` (H9) and test loops.
- Normalize ZIP `arcname` separators (H13) with a Windows-safe test.
- Trust model: confirmation/`--trust`, no auto-install in `package`, no code execution in
  `hooks list`, requirement validation (H12).
- End-to-end tests: temporary-profile deploy, ZIP contents, wheel install + `init`,
  config precedence, metadata preservation, empty slug.
- `py.typed`, incremental `mypy --strict`, enable `C90`/`S` in CI after fixes.
- Delete `src/qgis_manager/cli.py`; align `Makefile` and pre-commit with CI; regenerate
  `help/` automatically.
- Release workflow: unify note filenames, validate tag vs `pyproject.toml`, run tests
  before publishing, add a wheel-install smoke test.

### P2 — improvements

- Optional `pathspec` backend for full gitignore semantics (negations, nested files).
- XDG/APPDATA config path; load global `hooks`; `--project` root override.
- `--dry-run` for deploy/bump/clean; do not overwrite ZIPs without confirmation.
- Subprocess timeouts; opt-in cleaning of `*.qpj`/`*.cpg`; i18n or remove the Spanish
  classifier.
- Reduce `deploy.execute`/`validate.execute` complexity by extracting services.

---

## 10. Reproduction appendix

All probes ran in throwaway temporary directories; no repository files were modified.

**C1 — empty slug**

```python
# metadata.txt: name=!!!
deploy_plugin(src, dest_dir=dest_with_other_plugins, no_backup=True)
# dest before: ['other_plugin'] -> after: ['metadata.txt', 'plugin.py']
uninstall_plugin(src)  # removed the whole .../profiles/default/python/plugins
```

**C2 — metadata loss**

```text
bump patch on metadata containing a comment and [custom] section
-> comment and [custom] section absent from the rewritten file
```

**H1 — purge**

```python
rotate_backups(parent, "plug", limit=0)  # no deletion
```

**H2 — scaffold**

```text
init "My-Weird Plugin (Ñ)" -> SyntaxError in __init__.py:7 and <slug>.py:5
```

**H3 — pyuic6**

```text
compile --type resources -> dialog.py contains:
from PyQt6 import QtCore, QtGui, QtWidgets
```

**H4 — compile failures**

```text
compile --type resources  (invalid .qrc) -> EXIT: 0
compile --type docs       (Sphinx/uv failure) -> EXIT: 0, help/html empty
```

**H5 — profile precedence**

```text
config profile="production" -> deploy target .../profiles/default/python/plugins
```

**H6 — boolean validation**

```text
experimental=False -> "Field 'experimental' should be 'True' or 'False'."
```

**H7 — compliance ordering**

```text
repo-check (passes) -> install_external_libs() -> ZIP (binaries included)
```

**H8 — false positive**

```text
.venv/lib/fastmath.so -> "Official repository prohibits binaries"
```

**H9 — symlink**

```text
symlink loop in project -> OSError: [Errno 40] Too many levels of symbolic links
```

**H10 — fresh scaffold**

```text
init -> validate --repo -> exit 1 (missing LICENSE)
```

**H11 — ignore config**

```text
README nested form: pattern loaded=False, excluded=False
flat list form:    pattern loaded=True,  excluded=True
```

**H14 — abort**

```text
decline click.confirm -> "❌ Error: " (empty), exit 1
```

**Packaging smoke (positive)**

```text
uv build -> qgis_manage-0.9.2-py3-none-any.whl (56 entries, 14 templates)
extract wheel + init "Wheel Test" -> exit 0, project created
```

---

## 11. Conclusion

The repository has better-than-average engineering hygiene: green lint/type/format gates,
a fast 190-test suite with ~90 % line coverage, a working wheel, and automated releases.
The risk is concentrated in **unprotected destructive operations** (slug handling,
metadata rewriting, purge, compilation) and in **implicit trust** in the repository being
managed. Fixing the P0 items and replacing wiring-only tests with behavioural tests would
substantially change the reliability profile; most of the remaining medium items are
maintainability and hygiene debt rather than blockers.

---

## Update — 2026-10-18: P0 implemented

The P0 items from §9 were implemented in a follow-up change set (working tree, not yet
committed):

| P0 item | Implementation | Regression tests |
| :--- | :--- | :--- |
| Safe slug / target guard | `validate_slug()` + ASCII `slugify()`, reserved Windows names; guards in `deploy`, `dclean`, `init`, `package` | empty slug preserves destination; unusual names |
| Metadata preservation | New `qgis_manager/metadata.py` with line-oriented `update_general_keys()` and atomic `write_text_atomic()`; reused by `bump`, `sync`, `stamp_metadata_text` | comments, custom sections, multi-line values round-trip |
| Real purge | `purge_backups()` (counts/removes only `slug.bak.*`); `deploy --purge-backups` now calls it | behavioural purge test with real directories |
| Valid scaffold identifiers | ASCII PascalCase class names; leading `_` for digit-leading names; empty slug rejected; templates use `version=0.1.0` | `ast.parse` over all templates/names; generated metadata validates |
| Compilation reliability | PyQt6 patching; UI/QRC/TS/docs failures propagate as `False`; `compile`/`deploy` exit non-zero; docs built in a temp dir and moved atomically; no forced `uv run` | invalid QRC, missing tools, docs failure preserves previous HTML, pyuic6 output |
| Profile precedence | `--profile` default is `None`; config value is used and CLI overrides it | configured profile + CLI override |
| Validation fixes | Valid `True`/`False` no longer warn; plugin version requires `X.Y.Z`; `about` required; `repository` warning locally and error in `--repo` mode; regex typo fixed | boolean, short-version, repo-mode tests |
| Compliance ordering/ignore-aware scan | Dependencies installed before compliance; final file set validated; binary scan uses `IgnoreMatcher`; `metadata.txt` required; repo metadata enforced | `.venv` binaries ignored; install-before-compliance order; install failure aborts |

**Verification after the changes**: **405 tests + 13 subtests pass**; line coverage
**94.65 %**, branch coverage **~88.7 %**; `ruff check`, `ruff format --check` and
`mypy src` clean; wheel rebuilt, contains `qgis_manager/metadata.py`, and `init` +
`validate` pass from the wheel. `make`'s `unittest discover` runner also passes.

**Still open (P1/P2)**: symlink traversal, Windows ZIP separators, trust model for hooks
and dependency installation, end-to-end deploy/package tests, `py.typed`/strict mypy,
dead `cli.py`, README ignore syntax, docs/Makefile drift, release-note filenames.

*The original audit was read-only; the implementation changes summarized above were made
afterwards. `dist/` artifacts were rebuilt for packaging checks and remain git-ignored.*
