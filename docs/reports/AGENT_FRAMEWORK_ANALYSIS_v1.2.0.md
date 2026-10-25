# Agent Framework Analysis — Agentic Forge

> **Audit snapshot**: v1.2.0 (commit `2de22cf`). **Current framework**: v1.4.2
> (`b264e35`), adopted after this audit; see the update at the end.

**Scope**: `.agent` git submodule (Agentic Forge), its integration with `.agent-state/`,
the root `AGENTS.md`, `forge.toml`, `opencode.json`, and the QGIS domain packs.

**Source (audit)**: submodule commit `2de22cf`, tag `v1.2.0`.
**Current**: submodule tag `v1.4.2`, commit `b264e35` (clean; quality-gate fixes included).

**Method** (read-only): full inventory and review, structural validation
(`forge.py validate`, `--graph`, `--conflicts`), metrics/lesson commands, frontmatter
and link audits, scaffold comparison, and the framework's own quality gates
(`ruff`, `ruff format`, `mypy`, complexity, module size).

**Verdict**: the conceptual design and documentation are good, but **the framework is
not fully operational in this repository**: the session lifecycle depends on a missing
`agent_metrics.json`, several documented commands/scripts do not exist, and the
tooling does not pass the quality gates it preaches. Overall: **6/10** (design 8,
tooling 4, operational readiness 3).

---

## 1. Inventory

| Item | State |
| :--- | :--- |
| Submodule | `v1.2.0`, commit `2de22cf`, clean |
| License | MIT (independent from the repository GPL) |
| Size | 52 files, ~384 KB |
| Core skills | 9 |
| Project overlay skills | 2 (`domain-logic`, `project-context`) |
| Core workflows | 14 |
| QGIS domain pack | 3 skills + 3 workflows + resources |
| Tooling | 6 modules, **1,855 LOC** |
| Project state | `.agent-state/` with task/next_steps, overlay skills, lessons, history |
| Runtime | `opencode.json` with `architect`/`qa_engineer`/`auditor` roles and scoped permissions |

### Strengths

- Clean separation between the framework (`.agent`, submodule) and project-owned state
  (`.agent-state`), with `forge.toml` as the path contract.
- Roles and permissions are coherent: auditor is read-only (`edit: deny`), QA asks
  (`edit: ask`), architect can edit (`edit: allow`).
- Focused skills with valid frontmatter; 14 workflows with a consistent structure.
- A single tooling entry point (`forge.py`) and read-only validators.
- `memory_prune` uses `yaml.safe_load`; `lesson_extractor` runs `git` through an argument
  list with a timeout (no `shell=True`).
- The QGIS domain pack is separated from the generic core.
- Session history and semantic memory are versioned.

---

## 2. Validation results

| Command | Result |
| :--- | :--- |
| `forge.py validate` | **PASS** — “11 skills, 14 workflows” (framework + overlay only) |
| `forge.py validate --graph` | **PASS** — 2 overlay skills unreferenced, 1 project script unreferenced |
| `forge.py validate --conflicts` | **PASS** — only duplicate names/descriptions are checked |
| `forge.py metrics validate` | **FAIL** — `.agent-state/memory/agent_metrics.json` missing |
| `forge.py metrics report` | **FAIL** — same missing metrics file |
| `forge.py lesson propose` | Runs, but only detected `area_focus` (see §3) |
| `ruff check .agent/tools` | **49 errors** (35 E501, 3 F402, 3 UP017, 3 UP045, 2 I001, F401, F541, B007) |
| `ruff format --check .agent/tools` | 4 of 6 files would be reformatted |
| `mypy .agent/tools` | **7 errors** |
| `ruff --select C90` | 4 functions above CC 10 |
| Module size | `forge_metrics.py` 705 and `validate_agent_system.py` 603 (limit: 400) |
| Framework tests | None for the 1,855 LOC of tooling |
| Pre-push hook | Not installed (only `pre-commit`) |

The repository excludes `.agent` from `ruff` and runs `mypy src` only, so none of this is
caught in CI. `forge.toml` declares `max_cc` and `module_size_limit`, but they are not
enforced: `MAX_CC` is only copied as ground truth and `MODULE_SIZE_LIMIT` is unreferenced.

---

## 3. Findings

### Critical / high

#### C1 — The session lifecycle is broken by missing metrics

- `/start-session` runs `metrics validate` as a critical step
  (`workflows/start-session.md:58`); it fails because there is no `agent_metrics.json`.
- `/close-session` runs `metrics close-session` (`workflows/close-session.md:86`) and
  `metrics validate` (`:95`); `rotate_session_history()` returns `False` when the file is
  missing (`tools/forge_metrics.py:36-50`).
- `metrics report` also fails (`tools/forge_metrics.py:676`).
- `QUICK_REFERENCE.md:82-94` attributes the collector to `scripts/sync_metrics.py`, which
  does not exist (only `scripts/generate_help.py` is present).

**Impact**: an agent following the workflows cannot start or close a session; the memory
loop does not work.

#### C2 — `memory prune` is documented as a dry-run but is destructive

- `AGENTS.md:199` says `memory prune # prune expired snapshots (dry-run)`.
- The CLI does not parse `--dry-run`; `main()` calls `prune_lessons()` and
  `prune_next_steps_snapshots()` directly (`tools/memory_prune.py:178-182`).
- `prune_next_steps_snapshots()` deletes snapshots older than 90 days
  (`:147-176`); `prune_lessons()` rewrites the lessons YAML block.
- Current lessons have no `consolidated_in`, so they would not be pruned today; that also
  means the mechanism never removes the stale Gen 5 lessons.

**Impact**: a documented “safe” command can delete history.

#### C3 — The tooling does not dogfood the framework gates

- 49 ruff errors, 7 mypy errors, 4 functions above CC 10, 2 modules above 400 lines.
- `.agent` is in the ruff `exclude` and outside `mypy src`; no CI job validates it.
- `README.md:17` claims a `pre-push` hook enforces complexity/style; no pre-push hook is
  installed (only `pre-commit`).
- `verify-standards` recommends the validators, but CI never runs them.

**Impact**: the framework's quality claims are not verifiable, and its own tooling is the
least compliant code in the repository.

#### C4 — Workflows are not instantiated for this repository

The workflows are generic templates, but they are presented as executable procedures:

| Workflow | Reference | State |
| :--- | :--- | :--- |
| `start-session` | `AI_CONTEXT.md` | Missing |
| `start-session` / `close-session` | Docker / `make docker-test` | No Dockerfile or target |
| `run-tests` | `pytest tests/integration`, `FORCE_MOCKS=0` | No `tests/integration` |
| `release-package` | `python -m build`, `twine`, `gh release` | Repository uses `uv build` + automated release workflow |
| `release-package` | `mypy .` | CI uses `mypy src` |
| Several | `scripts/sync_metrics.py`, `skill_sync.py`, `security_scan.py`, `context_selector.py`, `check_cc.py`, `verify_i18n_hygiene.py`, `run_in_qgis.py` | None exist |

The release workflow is especially risky: following it can bypass the tag → draft → PyPI
pipeline.

#### C5 — The validator gives false confidence

`forge.py validate` prints “All .agent/ files pass system validation”, but:

- It only scans `.agent/workflows`; it does not validate
  `.agent/scaffold/qgis/workflows` or `scaffold/qgis/workflows`.
- Project scaffold workflows use `agent: Agent Auditor` / `QA Engineer`, not the canonical
  IDs (`auditor`, `qa_engineer`), and this is not detected.
- It does not check Markdown links, `AGENTS.md`, `QUICK_REFERENCE.md`, or `.agent-state`.
- `--conflicts` only checks duplicate names/descriptions
  (`tools/validate_agent_system.py:556`); it does not compare triggers or contradictory
  instructions.
- `--graph` reports every workflow→script dependency as “—”, ignoring scaffold references.

#### C6 — Required state files are missing

Missing:

- `.agent-state/memory/agent_metrics.json`
- `.agent-state/memory/memory_policy.md` (referenced by `AGENTS.md:210` and
  `tools/forge_paths.py:62`)
- `AI_CONTEXT.md` (referenced by start/close-session)

The state is also stale after the P0 implementation: `.agent-state/task.md:24` says
**190 tests / 89.93 %**, while the repository now has **217 tests / 88.73 %**;
`.agent-state/next_steps.md` still lists completed P0 items.

#### C7 — Semantic memory is stale and contradicts the project

`.agent-state/memory/AGENT_LESSONS.md` still contains Gen 5 lessons (2026-04-05) referring
to `antigravity-framerepo`, `skill_sync.py`, `scripts/skill_sync.py`, and
`docs/COMMIT_GUIDELINES.md` (which does not exist). Its user preferences conflict with the
current project:

- “`black` + `ruff`” — the project uses ruff only.
- “Never use pip directly” — the code has a pip fallback.
- “Programmatic UI, no `.ui`” — the manager compiles `.ui`.
- “Always run `scripts/skill_sync.py`” — the script does not exist.

The footer says “Last updated: 2026-04-05” despite 2026-10-10 entries.

#### C8 — SecInterp-specific metrics and signals are hardcoded

- `tools/forge_metrics.py:311-312` hardcodes `535→620`, `572→620`, `40.8→52.3`, and
  `41.7→52.3` from another project.
- `tools/lesson_extractor.py:36` looks for the same numbers as “stale metrics”.
- `auto_fix` replaces numbers in documentation; with foreign mappings it can corrupt text.
- README/QUICK_REFERENCE still mention **SecInterp** as the reference implementation.

#### C9 — Three template systems and duplicated QGIS packs

Coexisting:

1. `.agent/scaffold/qgis/` (framework domain pack)
2. `scaffold/qgis/` (project copy)
3. `src/qgis_manager/templates/` (the real CLI `init` templates)

The six files shared by `.agent/scaffold/qgis` and `scaffold/qgis` **differ** (with/without
`trigger`, normalized/stale agent IDs); `scaffold/qgis/skills/qa-docker` exists only in
the project copy. Neither scaffold is validated.

#### C10 — Portability and implicit dependencies

- `memory_prune.py` imports `yaml`, but the framework declares no dependency; it works
  only when the project environment already has PyYAML.
- `forge_paths.py` uses `tomllib` with no fallback, requiring Python 3.11+, while the
  README presents the framework as runtime-agnostic.
- Workflows use `// turbo` in 30 places, a runtime-specific directive, contradicting the
  runtime-agnostic claim.
- `opencode.json` confirms the actual runtime is opencode; the generic claim is aspirational.

#### C11 — `lesson propose` analyzes the wrong diff

`tools/lesson_extractor.py:45` runs `git diff <since> --stat`, not the patch. The signal
patterns (`Traceback`, `self.tr(...)`, `raise effect`, `scripts/*.py`) look for content
that does not appear in `--stat`. Reproduced: it only detected `area_focus` from file
names and proposed no lessons.

#### C12 — Architecture plans are stale

`architecture/IMPROVEMENT_PLAN_GEN8.md` is marked “✅ Implemented” but still has open items:
consolidate the two `AGENTS.md` files, remove duplicated tables, retire `skill_sync.py` /
`context_selector.py`, normalize `agent:` IDs, drop `trigger`, and consolidate metrics and
test runners. It also references scripts that no longer exist.

### Medium / low

| Area | Finding |
| :--- | :--- |
| Config robustness | `forge_paths._load_config` does not catch malformed TOML; a bad config crashes all tooling |
| Dead constants | `RESOURCES_DIR` and `MEMORY_POLICY_FILE` are defined but unused; `.agent/resources` does not exist |
| YAML parser | `validate_agent_system.parse_yaml_frontmatter` splits on `---` and does not support multi-line lists; PyYAML is not used |
| Skill counting | `skills_count` counts directories, not valid `SKILL.md` files |
| `--graph` | Workflow→script table is empty because it only scans framework workflows |
| `--conflicts` | No semantic or trigger conflict detection |
| `auto_fix` | Non-atomic writes and hardcoded mappings |
| `memory_prune` | Rewrites the whole YAML block (format/comments lost) and deletes snapshots without backup |
| Tests | No tests for the tooling |
| CI | No `forge.py validate` job; agent-system drift is invisible |
| Documentation | Root `AGENTS.md`, framework `AGENTS.md`, and `QUICK_REFERENCE.md` duplicate tables |
| External paths | `scaffold/qgis/skills/qa-docker/SKILL.md` links to an absolute `file:///home/.../sec_interp/...` path |

### Minor

- `QUICK_REFERENCE.md` lists `qa-docker` for `/run-tests`, but this project has no Docker.
- `AGENTS.md` says `python tools/forge.py`, while the project uses `.agent/tools/forge.py`.
- Framework `AGENTS.md` and root `AGENTS.md` list different role-skill mappings.
- `.agent/tools/__pycache__/` exists in the working tree (ignored).
- `forge.py` has no `--version`.

---

## 4. Recommendations

### P0 — make the framework operational

1. **Metrics bootstrap**: create `.agent-state/memory/agent_metrics.json` and a
   `scripts/sync_metrics.py` collector; make start/close-session run the collector before
   validation and degrade gracefully if metrics are still missing.
2. **Safe pruning**: `memory prune` is a dry-run by default; add `--apply` with backup and
   confirmation; correct `AGENTS.md`.
3. **Dogfooding**: lint, format, type-check, and test `.agent/tools`; add
   `forge.py validate` and the tooling tests to CI; fix all ruff/mypy/C90/module-size
   violations.
4. **Instantiate workflows**: replace missing commands/scripts with real repository
   commands; align the release workflow with the tag-driven pipeline; create
   `AI_CONTEXT.md` and `memory_policy.md` or remove their references.
5. **Broaden the validator**: scan scaffolds, links, `AGENTS.md`, `QUICK_REFERENCE.md`,
   `.agent-state`, canonical agent IDs, and trigger conflicts.

### P1 — coherence and maintainability

- Consolidate `AGENTS.md` and `QUICK_REFERENCE.md` into one source of truth.
- Choose one QGIS domain pack and remove the divergent copy.
- Prune the Gen 5 lessons and obsolete preferences; refresh `task.md` and `next_steps.md`.
- Remove SecInterp mappings and make the lesson extractor use the full `git diff`.
- Declare PyYAML and the minimum Python version in a framework manifest.
- Normalize scaffold `agent:` IDs.

### P2 — hygiene

- Remove or document `// turbo` and other runtime-specific artifacts.
- Archive/annotate the Gen 7/8 plans.
- Add atomic writes and backups to `memory_prune` / `auto_fix`.
- Unify README and QUICK_REFERENCE; remove the SecInterp reference.

---

## 5. Conclusion

`.agent` is a well-designed, well-documented framework that is **half-instantiated** in
this repository: memory state is missing or stale, several workflows contain commands and
scripts that do not exist, and the tooling fails its own gates. The main risk is false
confidence: `forge validate` passes while scaffolds, links, and state are unchecked;
`metrics validate` is critical and fails; and an agent can run `memory prune` believing it
is a dry-run.

*Original audit was read-only.*

---

## Update — upstream v1.4.2 adopted

The remote `agentic-forge` published **v1.4.2** (`b264e35`), which includes the two
quality-gate fixes found during this integration:

1. `forge_paths` catches `ValueError` when decoding TOML, fixing the modern-mypy false
   positive.
2. `should_skip_file` skips the metrics file and tool caches, avoiding self-validation
   and inflated scans. `.gitignore` now covers `.mypy_cache/` and `.pytest_cache/`.

The `.agent` submodule is now clean at **v1.4.2**; no local framework patches or CI
workarounds are needed.

Retained project-owned changes:

- `forge.toml`: strict mode, `max_lesson_lines`, project commands.
- `scripts/sync_metrics.py` + `.agent-state/memory/agent_metrics.json`.
- `memory_policy.md`, `AI_CONTEXT.md`, refreshed task/next_steps/lessons.
- Project CI runs `.agent/scripts/ci.sh` plus metric consistency.
- Analysis report and project state.

**Verification (v1.4.2):**

- Framework CI (`uv run bash .agent/scripts/ci.sh`): **37 tests**, ruff/format/mypy
  clean, validate/graph/conflicts/memory check pass.
- `forge.py validate`: **15 skills, 14 workflows, 3 templates**, no issues (strict);
  the count dropped after removing the duplicate root QGIS pack.
- `forge.py metrics validate` / `report`: pass (279 tests, 90.80 %).
- Project gates: **279 tests**, **90.80 %** line coverage, ruff/format/mypy clean.

**Sibling compatibility (v1.4.2):** `sec_interp`, `qgis-plugin-analyzer` and
`ai-context-core` pass validate/metrics/memory/graph/conflicts in temporary copies,
except `ai-context-core`'s pre-existing strict-mode broken link in its own
`.agent-state` (`../docs/implementation_plan_improvements.md`), which is a project-content
issue, not a framework regression.

**P1 progress:** root `AGENTS.md` is canonical and the unused `scaffold/qgis/` copy
was removed; the framework pack at `.agent/scaffold/qgis/` is the single QGIS source.
`tests/test_agent_docs.py` guards both decisions.

**P1 progress:** 8 end-to-end deploy/package tests now run the real CLI in a
subprocess. They found and fixed `--purge-backups` ignoring an absolute `--profile`.
Path/trust hardening followed (symlink confinement, POSIX ZIP names, `--trust`),
and the package is now typed (`py.typed`, strict mypy) with the dead `cli.py`
removed and Makefile/README drift corrected.

**P2 complete:** release notes are normalized to `vX.Y.Z.md` (legacy fallback in
the workflow) and `docs/architecture/AGENTIC_SYSTEM_PLANS.md` records the Gen 7/8
status without editing the shared submodule. No active project backlog remains.
