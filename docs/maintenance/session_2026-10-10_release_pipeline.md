# Session 2026-10-10 — Automated Release Pipeline & Release-Docs Migration

**Topic**: `release_pipeline`
**Agent role**: @architect (+ @qa_engineer for verification)
**Result**: ✅ COMPLETE — `qgis-manage` now releases through a two-stage GitHub Actions
pipeline, with coverage gating and migrated release documentation.

---

## Objective

Adapt the analyzer-style release process (`docs/RELEASE_PROCESS.md`) to this repository:
automate the GitHub/PyPI release, migrate release notes to `docs/releases/notes/`, add a
coverage gate (80 %), and refresh the documentation.

---

## What was done

### Pipeline
- Added `.github/workflows/release.yml`:
  - `draft-release` (on `v*` tag push) creates a draft GitHub Release using
    `docs/releases/notes/<tag>.md` as the body when present.
  - `publish-pypi` (on `release: published`, no `needs:`) runs `uv build` + `uv publish`
    with `UV_PUBLISH_TOKEN` from the `PYPI_TOKEN` secret.

### CI & quality
- `main.yml`: added `ruff format --check`, switched the test step to
  `pytest -q --cov=qgis_manager --cov-report=term-missing --cov-fail-under=80`, and added
  an informational `qgis-analyzer analyze .` step (no `--max-cc`).
- `pyproject.toml`: added `pytest-cov>=5.0` to both dev groups and `[tool.coverage]`
  (`source = ["qgis_manager"]`, `fail_under = 80`); regenerated `uv.lock`; ran
  `ruff format .` (8 files).

### Documentation migration
- `docs/releases/notes/` — release notes (moved from `docs/releases/`).
- `docs/releases/github/` — GitHub release bodies (moved).
- `docs/releases/RELEASE_PROCESS.md` — canonical guide, rewritten for `qgis-manage`
  (bump CLI, `--version`, notes path, coverage, `PYPI_TOKEN`, domain guardrail).
- `docs/CHANGELOG.md` — synchronized with the canonical root `CHANGELOG.md`.
- Updated internal references (`CHANGELOG.md`, `GITHUB_RELEASE_v0.6.0.md`, README badge).

---

## Decisions

- **Self-analysis**: informational only (no `--max-cc`); `core.py` still exceeds the
  complexity threshold, so a hard gate is deferred until it is split.
- **Publish auth**: `PYPI_TOKEN` repo secret (Trusted Publishing documented as an
  alternative).
- **Notes naming**: legacy `RELEASE_NOTES_vX.Y.Z.md` files are preserved in `notes/`
  (mirroring the analyzer); new releases use `notes/vX.Y.Z.md`.

---

## Verification

- `uv run ruff check .` → clean.
- `uv run ruff format --check .` → clean.
- `uv run mypy src` → clean.
- `uv run pytest -q --cov=qgis_manager --cov-fail-under=80` → passing, ≥80 %.
- `uv build` + `uvx twine check dist/*` → PASSED.

---

## Follow-up

- Create the `qgis-manage` PyPI API token and add the `PYPI_TOKEN` repo secret
  (`gh secret list` to verify).
- Consider a hard complexity gate once `core.py` is split (see the deep analysis report).
