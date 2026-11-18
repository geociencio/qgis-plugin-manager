# Phase B — commit plans

**Date**: 2026-11-18
**Parent plan**: `docs/plans/v0.17.0_refactor_plan.md`
**Status**: B1–B7 implemented; B8 pending.

Each file is the plan and execution procedure for one commit in phase B. The
implementation and state commits are listed so the history can be audited.

| Commit | Status | Implementation | State/docs | File |
| :--- | :--- | :--- | :--- | :--- |
| B1 | Done | `587071f` | `76b9572` | `B1_path_policy.md` |
| B2 | Done | `0d0b12c` | `77baebb` | `B2_deploy_workflow.md` |
| B3 | Done | `42cc861` | `d0d94b6` | `B3_package_workflow.md` |
| B4 | Done | `50594aa` | `2388191` | `B4_console_rename.md` |
| B5 | Done | `156e533` | `af84b98` | `B5_error_boundary.md` |
| B6 | Done | `a405927` | `1b8cab7` | `B6_atomic_toml.md` |
| B7 | Done | `6177d44` | `e5de15e` | `B7_external_inputs.md` |
| B8 | Planned | — | — | `B8_release.md` |

## Execution rules

1. One commit per item; never mix two B items in one implementation commit.
2. Each implementation commit must pass lint, format, mypy, tests, coverage
   95/90, and C901 = 0.
3. Add regression tests in the same commit as the fix.
4. Keep `project.dependencies = []`.
5. Update the parent plan status and state metrics after the commit.

## Current baseline

- Version: 0.16.2
- Tests: 449
- Statements: 96.18 %
- Branches: 90.45 %
- Combined: 94.82 %
- C901: 0
