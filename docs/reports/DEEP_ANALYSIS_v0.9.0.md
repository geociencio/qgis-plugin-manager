# Deep Analysis Report — QGIS Plugin Manager (qgis-manage v0.9.0)

**Scope**: dead code, duplication, complexity/optimization, and cross-tool boundary
guardrails for `ai-context-core` (ai-ctx) and `qgis-plugin-analyzer`.

**Source**: repository at `qgis-plugin-manager/`, commit `1542979`, `version = "0.9.0"`.
31 modules, 3,663 LOC, **190 tests**, coverage **90 %**, `ruff` + `mypy` clean.

**Method / tooling** (no source changes):

| Tool | Purpose | Result |
| :--- | :--- | :--- |
| `ruff` 0.15.2 | lint + F-rules | base config **clean**; `ERA001` 11 (commented-out code) |
| `pylint` 4.0.7 | `R0801` duplication + design | 2 duplicate blocks; 20 design smells |
| `vulture` 2.14 | dead code | 1 real (@60%); rest false positives |
| `radon` 6.0.1 | CC / MI | 3 rank **D**, 9 rank C; `core.py` MI A(23.7) |
| `pytest --cov` | coverage | 190 passed, **90 %** |
| `grep` reference check | confirm usage | each candidate verified |

---

## 1. Dead code

| Symbol | Evidence | Action |
| :--- | :--- | :--- |
| `ignore.py::IgnoreMatcher.get_ignore_func` (l.129-138) | 1 reference (the def itself); uncovered in `--cov-report=missing` | **Delete** |

`ruff --select ERA001` reports 11 commented-out-code blocks — review and remove.

**Ruled out (false positives):** `discovery.py` `optionxform` (a real `configparser`
override), `cli/progress.py` `label` (instance attribute), `validation.get_optional_fields`
(3 refs) and `validation.validate_boolean_field` (6 refs) — all used.

---

## 2. Duplication (broken single source of truth)

1. **Repeated command preamble** — `find_project_root()` + `load_config()` +
   `load_project_config()` + the `profile` / `qgis_version` defaults are copied across
   `cli/commands/deploy.py`, `dclean.py`, `hooks.py` (and variants in `validate.py`).
   `BaseCommand` exists but exposes no helper for this.
   → Extract `load_cli_context(args) -> (root, settings, …)` on `BaseCommand`.

2. **"No subcommand specified" block** duplicated in `cli/commands/bump.py:78-86` ↔
   `hooks.py:64-74` (pylint `R0801`).

3. **Cross-tool (worst): ignore-pattern matching implemented twice.**
   `qgis_manager/ignore.py::IgnoreMatcher` (reads `.qgisignore`/`.gitignore`, fnmatch)
   and `qgis-plugin-analyzer` `analyzer/utils/path_utils.py::IgnoreMatcher` (reads
   `.analyzerignore`). Same concept and algorithm, different config source.

---

## 3. Complexity & size

- **`core.py` = 842 lines** (2× the 400-line norm); lowest MI in the repo —
  `core.py A(23.72)`.
- **Rank D** (radon): `validation.validate_metadata` **D(28)**,
  `cli/commands/deploy.py::execute` **D(27)**, `core.stamp_metadata_text` **D(21)**.
- **Rank C**: `core.create_plugin_package` 18 · `sync_directory` 15 ·
  `compile_qt_resources` 15 · `compile_docs` 12 · `clean_artifacts` 12 ·
  `ignore.should_exclude` 13 · `ignore.load_ignore_patterns` 12 ·
  `cli/commands/validate.py::execute` 16 · `cli/commands/hooks.py::_hooks_list` 12.
- **Pylint design**: `core.py` concentrates `too-many-arguments/locals/branches`
  (`deploy_plugin`, `compile_qt_resources`, `stamp_metadata_text`,
  `create_plugin_package`, `init_plugin_project`); `deploy.execute`
  21 branches / 60 statements / 20 locals; `validate.execute` 17 locals;
  `package.execute` 17 locals.

**Stale dev dependencies**: `ai-context-core>=3.2.1` (current 5.1.0) and
`qgis-plugin-analyzer>=1.10.0` (current **1.15.2**) in `pyproject.toml` (dev groups,
lines 49-50 / 107-111). `ai-context-core` is not used by the manager at runtime.

---

## 4. Cross-tool boundaries (guardrails)

### 4.1 Correct by design — preserve

- `qgis-manage analyze` and `security` **delegate** to `qgis-analyzer`
  (`cli/analyzer.py::run_qgis_analyzer`, passing `--deep`/`--strict`/`-o`). Do **not**
  reimplement analysis in the manager.
- `package` / `deploy` / `compile` / `bump` are **lifecycle** concerns owned by the
  manager; the analyzer is read-only analysis.

### 4.2 Overlaps to resolve (define the SSoT, avoid drift)

1. **Official-repository compliance.** The manager checks prohibited binaries + `LICENSE`
   (`validation.validate_official_compliance`); the analyzer checks package size + binaries
   + metadata URLs (`analyzer/validators.validate_package_constraints` and
   `repository_compliance`). Two implementations of the same criterion.
   → The **manager** should be the authority for *packaging* compliance (it builds the
   ZIP); keep the analyzer's as *informative* analysis, or have `package --repo-check`
   invoke the analyzer instead of duplicating checks.

2. **`metadata.txt` validation.** `qgis_manager.validation.validate_metadata` vs
   `analyzer.validators.validate_metadata` — near-identical name, parallel rule sets
   (`qgis-manage validate` vs `qgis-analyzer analyze metadata`). Pick one authoritative
   implementation (likely the manager) or reuse the analyzer's `metadata` scope.

3. **`IgnoreMatcher` duplicated** across the two tools. Keep the **config files separate**
   (`.qgisignore`/`.gitignore` vs `.analyzerignore` are different concerns) but share
   semantics; extract a tiny shared matcher only if a third consumer appears.

### 4.3 With `ai-context-core`

- No runtime overlap (the manager produces no context artifacts).
- Latent only: plugin scaffolding (`core.init_plugin_project`) vs the scaffold in
  `agentic-forge`/ai-ctx. Keep them separate — the manager's scaffold is **QGIS-plugin
  domain-specific**; the forge scaffold is framework-generic.
- **Remove or update** the unused `ai-context-core` dev dependency.

---

## 5. Prioritized recommendations

| Priority | Action | Impact | Risk |
| :--- | :--- | :--- | :--- |
| **P0** | Delete `ignore.get_ignore_func` (dead) | −10 LOC | Low |
| **P0** | Update/remove dev deps (`ai-context-core`; `qgis-plugin-analyzer>=1.15.2`) | Security / consistency | Low |
| **P1** | Extract a shared CLI context helper + the "no subcommand" block | −duplication | Low |
| **P1** | **Split `core.py`** (842) into `core/{deploy,compile,package,scaffold,platform}.py`, re-exporting from `core/__init__.py` to keep tests green | Maintainability | Medium |
| **P2** | Lower CC of `validate_metadata` (28), `deploy.execute` (27), `stamp_metadata_text` (21) via extracted steps | Testability | Medium |
| **P2** | Define the compliance / metadata-validation SSoT with the analyzer (delegate, don't duplicate) | Prevents cross-repo drift | Medium |
| **P3** | Clean `ERA001`; fix `W0212` (`_positionals`/`_group_actions` in `cli/app.py`, `cli/parser.py`) | Hygiene | Low |

**Metadata nit**: `Natural Language :: Spanish` classifier with English README/docs.

---

*Generated as an ad-hoc deep analysis; no source or configuration was modified.*

---

## Update — 2026-10-10 (core.py refactor)

The `core.py` items below were addressed (plan: `docs/plans/core_refactoring_plan.md`):

- **P1 — Split `core.py`** ✅ Done. The 840-line module is now a package:
  `core/{platform,deploy,compile,package,cleanup,scaffold}.py` + `core/__init__.py`
  re-exporting the public API. Every module is ≤ 352 lines (limit 400).
- **P2 — Complexity of `stamp_metadata_text`** ✅ Done (D21 → B7). The other
  `core.py` hotspots were also extracted: `create_plugin_package` C18→A5,
  `sync_directory` C15→B7, `compile_qt_resources` C15→A4, `compile_docs` C12→B7,
  `clean_artifacts` C12→A1. No function in `core/` exceeds CC 8 (limit 10);
  average dropped from **B (7.67)** to **A (4.44)** and MI from **A 23.75** to
  **A 42–63** across modules. Coverage 89.78 % → 89.93 %; 190 tests still pass.

Still open (out of this refactor's scope): `validation.validate_metadata` (D28),
`cli/commands/deploy.py::execute` (D27), the `IgnoreMatcher`/compliance/metadata
SSoT overlap (§2/§4), the dead `ignore.get_ignore_func` (P0) and the stale
`ai-context-core` dev dependency (P0).
