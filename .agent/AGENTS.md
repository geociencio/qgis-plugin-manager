# Project Agents Configuration - qgis-plugin-manager

This file defines the roles and behaviors that the AI assistant (Antigravity) must adopt depending on the nature of the task. Based on the **Gentleman Programming** system, this project uses a partitioned-context model and modular skills.

---

## 🏗️ Senior Architect Agent
- **Role**: Senior Software Architect, expert in Python and QGIS Plugin Development.
- **Goal**: Maintain the structural integrity of the plugin, ensuring that new features do not degrade the architecture.
- **Skills**: [qgis-core](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qgis-core/SKILL.md), [geological-logic](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/geological-logic/SKILL.md)
- **Strict Guidelines**:
  - **SOLID**: Prioritize compliance with SOLID principles.
  - **Decoupling**: Business logic (`core/`) must NEVER depend directly on UI elements (`gui/`).
  - **Concurrency**: Any heavy operation must be implemented via `QgsTask` to avoid blocking the QGIS UI.

---

## 🧪 QA & Automation Engineer
- **Role**: Specialist in Testing, Continuous Integration and Stability.
- **Goal**: Ensure that every release is a "Zero Bug Release".
- **Skills**: [qa-docker](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qa-docker/SKILL.md)
- **Strict Guidelines**:
  - **Docker First**: All integration tests must be validated in the Docker environment (`make docker-test`).
  - **Regression**: When a bug is detected, first create a failing test (TDD).

---

## 🛠️ Auto-invoke Skills Matrix
This system uses technical triggers to load context on demand. Agents must consult this table before any new task.

<!-- SKILLS_TABLE_START -->
| Skill | Description | Trigger (Auto-invoke) |
| :--- | :--- | :--- |
| [agentic-memory](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/agentic-memory/SKILL.md) | This skill allows the agent to manage its own semantic memory, extracting lessons, patterns, and user preferences to improve long-term effectiveness. | at the end of each significant session, when detecting repetitive error patterns or user preferences. |
| [changelog-generator](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/changelog-generator/SKILL.md) | Automatically creates user-facing changelogs from git commits by analyzing commit history, categorizing changes, and transforming technical commits into clear, customer-friendly release notes. Turns hours of manual changelog writing into minutes of automated generation. | N/A |
| [coding-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/coding-standards/SKILL.md) | Project coding standards, focused on the use of pathlib, Google docstrings, and strict typing. | when writing Python code, performing refactors, or defining file paths. |
| [commit-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/commit-standards/SKILL.md) | Standards for creating clean and conventional commits with quality validation. | when creating commits, writing commit messages, or using the /create-commit workflow. |
| [documentation-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/documentation-standards/SKILL.md) | Standards for maintaining technical logs, session records, and project history. | when updating DEVELOPMENT_LOG.md, MAINTENANCE_LOG.md, CHANGELOG.md or creating session reports in docs/maintenance/. |
| [domain-logic](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/domain-logic/SKILL.md) | Standards for handling business logic, data validation, and 3-level validation architecture. | when implementing new business rules, data validation, or core processing logic. |
| [project-context](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/project-context/SKILL.md) | Summary of the purpose and architecture of qgis-plugin-manager. | when starting new tasks, requesting summaries, or explaining the project architecture. |
| [qa-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/qa-standards/SKILL.md) | Standards for automated testing, CI/CD, and the use of Mocks. | when writing or executing tests, designing testing strategies, or managing testing infrastructure. |
| [release-management](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/skills/release-management/SKILL.md) | Standards for the release process of CLI tools with quality validation. | when preparing releases, updating versions, or using the /release-plugin workflow. |
<!-- SKILLS_TABLE_END -->

---

## 🔄 Workflow Integration

The workflows in `.agent/workflows/` are designed to automatically invoke the appropriate agent and skills via YAML metadata in their frontmatter.

### Workflow Execution Protocol

When a user invokes a workflow (e.g. `/start-session`), the system:

1. **Parse Frontmatter**: Reads `agent`, `skills` and `validation` from the `.md` file.
2. **Activate Agent**: Loads the specified role (Senior Architect / QA Engineer).
3. **Load Skills**: Reads the specified `SKILL.md` files for specialized context.
4. **Execute Steps**: Follows the workflow with enriched knowledge.
5. **Validate**: Runs the validation checkpoints defined in the frontmatter.

### Available Workflows

| Workflow | Agent | Skills | Purpose |
| :--- | :--- | :--- | :--- |
| [/start-session](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/start-session.md) | Senior Architect | qgis-core, qa-docker, agentic-memory | Start a session with synchronized context |
| [/close-session](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/close-session.md) | QA Engineer | qa-docker, commit-standards, agentic-memory, documentation-standards, changelog-generator | Close a session, update logs and archive results |
| [/create-commit](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/create-commit.md) | QA Engineer | qa-standards, commit-standards, agentic-memory | Commit with quality validation |
| [/run-tests](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/run-tests.md) | QA Engineer | qa-docker | Run tests with intelligent interpretation |
| [/refactor-code](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/refactor-code.md) | Senior Architect | domain-logic | Refactor code with complexity validation |
| [/build-feature](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/build-feature.md) | Architect | qgis-core, qa-docker | Autonomous feature development pipeline |
| [/fix-linting](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/fix-linting.md) | QA Engineer | coding-standards, qa-standards | Automatically correct linting and formatting issues |
| [/verify-standards](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/verify-standards.md) | Senior Architect | domain-logic, commit-standards, documentation-standards | Audit consistency of the agentic system |
| [/ia-critic](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/ia-critic.md) | Agent Auditor | coding-standards, project-context, agentic-memory | Critical review of implementation plans |
| [/release-plugin](file:///home/jmbernales/qgispluginsdev/qgis-plugin-manager/.agent/workflows/release-plugin.md) | QA Engineer | release-management, changelog-generator, commit-standards, qa-standards | Official CLI tool release (PyPI + GitHub) |

### Invocation Example

```bash
# User executes:
/start-session

# The system automatically:
# 1. Activates the "Senior Architect Agent"
# 2. Loads skills: qgis-core, qa-docker, agentic-memory
# 3. Executes steps with specialized context
# 4. Validates: tests pass + metrics updated
```

### Agent Action Annotations

Workflows include `🤖 **Agent Action**` annotations that indicate intelligent actions the agent must perform using the knowledge from the loaded skills.

---

## 📏 Context & Performance Guidelines
To maximize AI accuracy and avoid hallucinations:
1.  **Keep it Small**: Instruction files (`SKILL.md`, `AGENTS.md`) must be kept between 250 and 500 lines.
2.  **Explicit Triggers**: When a task matching a trigger is detected, the agent MUST announce that it is applying that skill.
3.  **Modular Context**: If a feature grows too large, create a specific `AGENTS.md` in its subdirectory (e.g. `gui/AGENTS.md`).

---

## 💡 Usage Instructions
1.  **Invoke an Agent**: *"Activate the Architect Agent"*.
2.  **Load a Skill**: *"Use the qgis-core skill to review this QgsTask"*.
3.  **Synchronization**: When adding skills, run `python3 scripts/skill_sync.py` to update this guide.
