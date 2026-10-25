# Agentic System Plans — Status

The Gen 7 and Gen 8 plans are **framework-owned** documents in the shared
`.agent/architecture/` submodule. They are kept as reference; this project does not
edit them and has no local work item for them.

| Plan | Status | Decision |
| :--- | :--- | :--- |
| [Gen 7 → Gen 8 proposal](../../.agent/architecture/IMPROVEMENT_PLAN_GEN7.md) | Superseded by Gen 8 | Reference only; the opencode-corrected Gen 8 plan supersedes its runtime assumptions. |
| [Gen 8 proposal (opencode)](../../.agent/architecture/IMPROVEMENT_PLAN_GEN8.md) | Partially implemented upstream | Agentic Forge **v1.4.2** is the adopted baseline; remaining items belong to upstream `agentic-forge`. |
| [General improvement plan](../../.agent/architecture/IMPROVEMENT_PLAN.md) | Historical roadmap | Reference for future upstream proposals. |

## Project position

- Root `AGENTS.md` is the project source of truth; framework defaults are linked.
- Adopted framework: **v1.4.2** (`b264e35`), clean submodule.
- Do not recreate the Gen 7/8 tooling in this repository; propose remaining items
  upstream in `agentic-forge` instead.
