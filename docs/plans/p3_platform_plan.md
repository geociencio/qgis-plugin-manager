# P3 Platform Plan — nested ignores, execution policy, parallelism and plugins

**Date**: 2026-10-25
**Baseline after P2**: 259 tests (+13 subtests), 90.43 % combined line+branch
coverage, branch gate 90 %, C901 = 0, two intentional CLI exception guards.
**Predecessors**: [`p0_optimization_plan.md`](p0_optimization_plan.md),
[`p1_optimization_plan.md`](p1_optimization_plan.md),
[`p2_quality_plan.md`](p2_quality_plan.md) — implemented.
**Status**: ✅ Core implemented 2026-10-25 in commits `73aaa93`, `3f4ceb9`, `83a41fb`, `fa4d414`, `b669eee`, `4e9a811`, `01c67f3`; compatibility deviations are listed in `.agent-state/task.md`.

## 1. Goal

Move from a solid single-process CLI to a safer, extensible platform:

1. Full-enough ignore semantics for real repositories (nested ignore files).
2. A smaller execution surface for hooks and dependency installation.
3. Bounded parallel compilation without changing output semantics.
4. Third-party command discovery through Python entry points.

This phase is deliberately **opt-in and compatibility-first**: defaults stay
deterministic; new behavior is enabled by configuration or flags.

## 2. Current state

| Area | Current behavior | Gap |
| :--- | :--- | :--- |
| Ignore | root `.qgisignore`/`.gitignore` + pyproject; `!` supported | nested ignore files ignored |
| Hooks | `--trust` required; shell commands use `shell=True`; no timeout | broad execution surface, no time limit |
| Dependencies | `uv/pip install --target libs`; `--trust` gated | no timeout/index/constraint policy, shell resolved externally |
| Compile | sequential UI/QRC/TS using `CompileContext` | no `--jobs`; repeated subprocess waits |
| Commands | static `cli/registry.py` | no external command packages |
| Tests | 259, branch ≥90 % | few performance/contract tests |

## 3. Workstreams and commits

### Commit 1 — `feat(ignore): load nested ignore rules`

Introduce an internal rule model while preserving the public API:

```python
@dataclass(frozen=True)
class IgnoreRule:
    pattern: str
    base_dir: Path       # directory containing the ignore file
    source: str           # .qgisignore / .gitignore / pyproject
```

- `load_ignore_patterns()` remains the compatibility API returning `list[str]`
  for root rules.
- Add `load_ignore_rules(project_root, include_dev)` used by `IgnoreMatcher`.
- `IgnoreMatcher.should_exclude(path)`:
  - starts with root rules;
  - adds rules from each ancestor directory between project root and the path;
  - deeper files override shallower ones; in the same directory `.qgisignore`
    wins over `.gitignore`;
  - applies the existing ordered negation semantics.
- Cache loaded rules per directory; invalidate only in tests/constructors.
- Explicitly document that `.git/info/exclude` is not supported.

Tests:
- nested `.gitignore` applies only inside its subtree;
- deeper `!` re-includes a parent-excluded file;
- root `.qgisignore` precedence preserved;
- no repeated disk reads for the same directory.

**Acceptance**: nested rules work; existing ignore tests unchanged; no C901.

### Commit 2 — `feat(hooks): execution policy and timeout`

Add a `HookPolicy` dataclass in `hooks.py`:

```python
@dataclass(frozen=True)
class HookPolicy:
    timeout: int = 300
    shell: bool = False          # opt-in legacy shell commands
    inherit_env: bool = False    # allowlist + QGIS_PROJECT_ROOT by default
```

- `run_hook(..., policy: HookPolicy | None = None)`.
- Python hooks run in-process as today (already trusted by `--trust`).
- Shell hooks:
  - default `shell=False` (split command safely with `shlex.split`);
  - legacy shell requires explicit `shell = true` in project config and a
    one-time warning;
  - always pass `timeout=policy.timeout`;
  - environment: minimal allowlist (`PATH`, `HOME`, `USERPROFILE`, `SYSTEMROOT`,
    `TEMP`, `TMP`, `QGIS_PROJECT_ROOT`), never the full environment by default;
  - on timeout, kill and report a clear error.
- `deploy` reads policy from `[tool.qgis-manager.hooks]` or defaults; `--trust`
  remains mandatory.
- `hooks test` uses the same policy.

Tests: timeout, shell-opt-in warning, env allowlist, Python-hook failure.

**Acceptance**: no unbounded hooks; no shell by default; `--trust` semantics
unchanged; existing hook tests updated.

### Commit 3 — `feat(dependencies): bounded, auditable install`

- Add `DependencyPolicy` (`timeout`, `index_url`, `extra_args`) with defaults.
- Always pass `timeout`; never use `shell=True`; resolve `uv`/`python -m pip`
  via explicit argv.
- Add optional `--index-url`/config passthrough and `--dry-run` for
  `install-deps`/`package`.
- Log the exact command (redact credentials in URLs) and target directory.
- Keep `--trust` gating in `package`; `install-deps` remains explicit.
- Reject dependency specs containing shell metacharacters before invoking pip/uv.

Tests: timeout, dry-run, redacted URL, rejected metacharacters, argv shape.

**Acceptance**: no unbounded or shell dependency install; package trust behavior
unchanged.

### Commit 4 — `feat(compile): bounded parallel jobs`

- Add `--jobs` to `compile` and `[tool.qgis-manager].compile_jobs` (default `1`).
- Use `ThreadPoolExecutor` for independent files within UI/QRC/TS families.
- Preserve deterministic **callback/log order**: workers emit into an ordered
  queue; the main thread drains it.
- Keep `CompileContext` thread-safe: timeout, tool path and callback are
  immutable; no shared mutable progress state.
- Stop scheduling new work after a failure? Default: finish in-flight work,
  report aggregate False (same as sequential).
- Benchmark 1 vs 4 jobs on a synthetic project; record throughput only as
  informational, not a CI gate.

Tests: same output with jobs=1/4, failure aggregation, callback ordering,
invalid jobs value.

**Acceptance**: default output identical; `--jobs 1` byte-for-byte behavior;
no race in callbacks; timeout preserved.

### Commit 5 — `feat(cli): discover external command entry points`

- Define group `qgis_manager.commands`.
- `build_registry()` returns built-ins plus entry points, ordered:
  built-ins first, external alphabetical.
- Reject duplicate names and non-`BaseCommand` objects with a clear error.
- `CLIApp` uses `build_registry()`.
- Document packaging a plugin command; no network discovery.
- Tests monkeypatch `importlib.metadata.entry_points` for valid/duplicate/broken
  entries.

**Acceptance**: built-in help/order unchanged when no external commands; broken
external entry points fail clearly without crashing the core registry.

### Commit 6 — `test: add contract and performance smoke tests`

- Contract tests for `compile`, `bump`, `init` (the P1 E2E gap).
- A small synthetic compile benchmark (`pytest.mark.benchmark` optional, skipped
  in normal CI) or a non-flaky timing smoke test.
- Keep the default suite fast; no network in tests.

**Acceptance**: contract tests pass; benchmark opt-in; default suite runtime
increase <20 %.

### Commit 7 — `docs(release): document platform controls`

- Update `README`, `help/compile.md`, `help/install-deps.md`, `help/deploy.md`,
  `docs/guides/TUTORIAL.md`.
- Document ignore nesting, hook policy, dependency dry-run/index, `--jobs`,
  entry-point packaging.
- Add changelog entries.
- Regenerate help.

**Acceptance**: docs match CLI help; links valid; no stale examples.

### Commit 8 — `chore(agent): record P3 results`

- Metrics, task/next_steps, plan/report status.

## 4. Test and quality gates

After every commit:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q
uv run pytest .agent/tests -q
uv run python .agent/tools/forge.py validate
uv run python .agent/tools/forge.py metrics validate
```

Final:

```bash
uv run python .agent/tools/forge.py project test-full
uv run python -m pytest --cov=qgis_manager --cov-branch --cov-fail-under=90
uv run ruff check --select C90 src/qgis_manager
```

## 5. Acceptance criteria

- **C901 = 0**, branch coverage ≥90 %, line coverage not reduced.
- Nested ignore rules work with documented precedence; root API compatible.
- Hooks/dependencies are bounded, non-shell by default, and auditable; `--trust`
  remains required for project-controlled execution.
- `compile --jobs N` preserves output/callback ordering; `--jobs 1` is the
  compatibility default.
- External command entry points are optional, deterministic and fail clearly.
- No new runtime dependencies.
- `.agent` submodule remains untouched.

## 6. Risks and mitigations

| Risk | Mitigation |
| :--- | :--- |
| Nested ignore changes exclusions | Golden tests for root/nested/negation; keep root API |
| Hook shell default changes behavior | Legacy `shell = true` opt-in with warning; migration note |
| Parallel callbacks race/reorder | Ordered queue + immutable context; jobs=1 default |
| External entry point import side effects | Lazy/isolated import; clear error; no built-in override |
| Dependency installer timeout/index errors | Explicit argv, timeout, dry-run tests |
| Performance regressions | Benchmark opt-in; default jobs=1 |

## 7. Sequence and rollback

1. Nested ignore rules (self-contained).
2. Hook policy (security-sensitive).
3. Dependency policy.
4. Parallel compile (opt-in).
5. Entry points.
6. Contract/performance tests.
7. Docs.
8. Results.

Each commit is independently revertible. Keep `jobs=1` and `shell=False` as
defaults so rollback is always behavior-compatible.

## 8. Out of scope (P4/never)

- OS/container sandboxing of hooks (requires external runtime).
- Full Git ignore semantics (`.git/info/exclude`, global excludes).
- Remote plugin/command marketplaces.
- Async subprocess rewrite; threads are enough for independent tools.
- Network-based dependency resolution changes.

## 9. Approval

Per the Architect constraint, **no code will be written until this plan is approved**.
On approval, start with Commit 1 (nested ignore) and report compatibility tests
before touching hooks or parallel execution.
