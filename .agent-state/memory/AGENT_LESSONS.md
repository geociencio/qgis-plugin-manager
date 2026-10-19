# Agent Learning Memory

This file records technical lessons, user preferences, and solutions to complex issues
encountered during development. It is the semantic-memory layer of the Agentic Forge
system; see `memory_policy.md` for retention and promotion rules.

---

## 🧠 Critical Lessons

```yaml
lessons:
  - date: 2026-10-19
    category: AGENTIC_SYSTEM
    topic: Framework tooling needs its own quality gate
    lesson: >-
      A tooling directory excluded from the project's lint/type/coverage paths drifts
      silently even when the framework preaches zero-regression gates.
    action: >-
      Lint, type-check and test .agent/tools in CI, and run forge.py validate as a
      required job.
  - date: 2026-10-19
    category: AGENTIC_SYSTEM
    topic: Session workflows depend on a metrics bootstrap
    lesson: >-
      The session lifecycle fails if agent_metrics.json does not exist, so a fresh
      clone cannot start or close a session until a collector runs.
    action: >-
      Run `uv run python scripts/sync_metrics.py` before metrics validation, and keep
      a committed metrics baseline in .agent-state/memory/.
  - date: 2026-10-19
    category: TOOLING
    topic: Destructive maintenance commands must be opt-in
    lesson: >-
      Documentation that labels a pruning command as a dry-run is dangerous when the
      implementation mutates files by default.
    action: >-
      Default to a dry-run, require --apply, print the exact candidates, and back up
      before deleting history.
  - date: 2026-10-10
    category: TOOLING
    topic: Mock patch targets after a package split
    lesson: >-
      Splitting a module into a package keeps `from pkg.mod import x` working via
      re-exports, but `unittest.mock.patch("pkg.x")` no longer intercepts calls made
      from inside the new submodules (they read their own module globals).
    action: >-
      After splitting a module, retarget every `@patch` to the submodule that looks up
      the symbol (e.g. `pkg.deploy.x`), not the package root.
  - date: 2026-10-10
    category: TESTING
    topic: Cross-platform file and path assertions
    lesson: >-
      `tempfile` returns unresolved paths while `Path.resolve()` follows symlinks and
      8.3 short names, so equality checks and default-encoding reads fail on
      macOS/Windows CI.
    action: >-
      Compare against `tmp_path.resolve()` and always pass `encoding="utf-8"` when
      reading files written as UTF-8.
  - date: 2026-10-10
    category: TOOLING
    topic: Release-event workflows use the tag's commit
    lesson: >-
      A `release: published` event evaluates the workflow from the tagged commit, and a
      publish job must not declare `needs:` on a job that is skipped on that event.
    action: >-
      Keep `publish-pypi` on its own `release` condition and apply release-event fixes
      in the commit the tag points to.
```

---

## ⚙️ User Preferences

- **Language**: Agent documentation, code, lessons and commits in English.
- **Formatting**: `uv run ruff check .` + `uv run ruff format .` (ruff is the only
  formatter; do not introduce black).
- **Package manager**: `uv` for the project; the CLI keeps a pip fallback for external
  environments, which is intentional.
- **Testing**: local `uv run pytest` is the primary path; Docker is optional and the
  repository does not ship a Docker setup.
- **UI**: the manager compiles `.ui` files, but new UI work should prefer programmatic
  Qt unless a `.ui` source is explicitly requested.
- **Commits**: Conventional Commits in English.
- **Metrics**: run `uv run python scripts/sync_metrics.py` before closing a session and
  `uv run python .agent/tools/forge.py metrics validate` before committing metric changes.
- **Framework state**: never write project state into `.agent/`; use `.agent-state/`.

---

## 🛠️ Hotspot Solutions

- **Pre-commit hook block on ruff E501 in `scripts/`**: `scripts/` is excluded from the
  project ruff configuration; fix framework/tooling style in `.agent/tools` instead of
  bypassing hooks.
- **Stale metric references**: refresh the metrics file, then run
  `forge.py metrics validate`; do not hand-edit historical numbers in architecture plans.
- **Long-lived lessons**: set `consolidated_in` once a lesson is reflected in a
  `SKILL.md`; `memory prune --apply` will move it to the `[PRUNED]` index.

---
*Last updated: 2026-10-19*
