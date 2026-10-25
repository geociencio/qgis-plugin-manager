# Agent Learning Memory

This file records technical lessons, user preferences, and solutions to complex issues
encountered during development. It is the semantic-memory layer of the Agentic Forge
system; see `memory_policy.md` for retention and promotion rules.

---

## 🧠 Critical Lessons

```yaml
lessons:
  - date: 2026-10-25
    category: TOOLING
    topic: Metrics report assumes a numeric task completion rate
    lesson: >-
      forge.py metrics report crashed after close-session because the rotated history entry
      had task_completion_rate=None; completed sessions need a numeric rate or upstream
      null handling.
    action: >-
      Record task_completion_rate=1.0 for completed sessions and propose a null-safe
      formatter upstream in agentic-forge.
  - date: 2026-10-25
    category: TESTING
    topic: Subprocess E2E catches path bugs that mocks hide
    lesson: >-
      The deploy E2E test found that --purge-backups ignored an absolute --profile
      because target_dir was resolved inside the purge branch; mocked CLI tests could
      not observe the real filesystem target.
    action: >-
      Keep at least one real-CLI test for path-sensitive commands and assert the
      filesystem effects, not only exit codes.
  - date: 2026-10-25
    category: TOOLING
    topic: Strict mypy exposes real argument bugs
    lesson: >-
      Enabling strict mypy revealed that get_source_files passed an ignore-pattern list
      as the boolean include_dev argument of IgnoreMatcher, so dev files were not
      excluded as intended.
    action: >-
      Adopt strict typing incrementally and treat new type errors as possible runtime
      defects rather than adding blanket ignores.
  - date: 2026-10-25
    category: AGENTIC_SYSTEM
    topic: Document shared-framework hints instead of editing the submodule
    lesson: >-
      The remaining // turbo hints and qa-docker alias belong to the shared Agentic Forge
      submodule; editing them locally would fork the framework used by sibling repos.
    action: >-
      Record project decisions in AGENTS/docs and add guard tests; propose framework
      changes upstream in agentic-forge.
  - date: 2026-10-19
    category: AGENTIC_SYSTEM
    topic: Check upstream framework tags before implementing features
    lesson: >-
      A stale submodule checkout made a P0 implementation look necessary when the
      upstream framework had already released the same capabilities in v1.4.1.
    action: >-
      Run `git fetch --tags` and review the remote release notes before building a
      framework feature or forking local tooling.
  - date: 2026-10-19
    category: AGENTIC_SYSTEM
    topic: Shared framework changes must stay generic
    lesson: >-
      Agentic Forge is used by sibling repositories, so project-specific commands,
      thresholds and paths belong in forge.toml or .agent-state, not in the shared
      workflows or tooling.
    action: >-
      Validate framework changes against temporary copies of sibling projects and keep
      project commands in `[project]` configuration.
  - date: 2026-10-19
    category: TOOLING
    topic: Never round-trip metadata.txt through configparser
    lesson: >-
      Rewriting metadata.txt with configparser drops comments, custom sections and
      formatting, which silently loses user content during version bumps.
    action: >-
      Use a line-oriented updater that changes only the affected keys and writes the
      file atomically; add a preservation test with comments and custom sections.
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
