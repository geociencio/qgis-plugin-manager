# Next Steps

**Date**: 2026-10-10
**Context**: Release automation + `core.py` refactor complete; **v0.9.1** and **v0.9.2** released (GitHub + PyPI). CI green across Ubuntu/Windows/macOS × Python 3.11–3.13.

**Pending (What's missing):**
- [ ] **Deep-analysis follow-ups (not `core`)**: lower CC of `validation.validate_metadata` (D28) and `cli/commands/deploy.py::execute` (D27); decide the compliance / metadata-validation single source of truth vs `qgis-plugin-analyzer`; remove the dead `ignore.get_ignore_func`; refresh or remove the stale `ai-context-core` dev dependency.
- [ ] **(Optional) Backfill GitHub Releases** for tags `v0.7.0`–`v0.9.0` (only tags exist; the last GitHub Release is `v0.6.4`).
- [ ] **(Optional) Prune stale Gen 5 knowledge** in `.agent-state/memory/AGENT_LESSONS.md` (references to `skill_sync.py` / `antigravity-framerepo` are obsolete).

**Command to resume:**
`/start-session`
