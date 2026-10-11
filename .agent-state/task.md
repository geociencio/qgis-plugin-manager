# Active Task: Release Automation & core.py Refactor

## Status
- **Phase**: Closed
- **Progress**: 100%
- **Status**: ✅ Released (v0.9.1, v0.9.2)

## Objectives
1. [x] Adopt the analyzer-style automated release pipeline (GitHub draft + PyPI) and migrate the release docs.
2. [x] Add a coverage gate (80%) and `ruff format --check` to CI.
3. [x] Split `core.py` into a cohesive package and lower cyclomatic complexity.
4. [x] Fix the cross-platform CI failures (macOS/Windows).
5. [x] Release v0.9.1 and v0.9.2.

## Todo
- [x] `.github/workflows/release.yml` + `main.yml` coverage/format gates; `pytest-cov`.
- [x] Migrate release docs to `docs/releases/{notes,github}`; rewrite `RELEASE_PROCESS.md`.
- [x] `core/` package split + complexity reduction; updated `@patch` targets.
- [x] Cross-platform test fixes (path resolution + UTF-8 reads).
- [x] Releases v0.9.1, v0.9.2 (tag → draft → publish → PyPI).

## Context
- Framework: **agentic-forge** (`.agent/` submodule v1.2.0, project state in `.agent-state/`).
- Quality: 190 tests, 89.93% coverage, `ruff`/`ruff format --check`/`mypy` clean;
  CI green across Ubuntu/Windows/macOS × Python 3.11–3.13.
- Release path: push tag `vX.Y.Z` → draft GitHub Release → publish → `publish-pypi` → PyPI.
