# Next Steps

**Date**: 2026-05-12
**Context**: Multi-version support (QGIS 3 and 4) has been implemented and version **v0.7.0** has been released.

**Pending (What's missing):**
- [ ] **Validate CLI integrations (Typer)** against the new blueprints in `/scaffold`.
- [ ] **Resolve `ruff` debts in the `scripts/` folder**. Add `exclude = ["scripts/"]` to `pyproject.toml` or fix the E501/E741 violations manually.
- [ ] **Test interactive deployment on Windows and macOS** to confirm that directory creation works as expected in non-Linux environments.

**Command to resume:**
`/start-session`
