---
name: project-context
description: Summary of the purpose and architecture of qgis-plugin-manager.
trigger: when starting new tasks, requesting summaries, or explaining the project architecture.
---

# Project Context: qgis-plugin-manager

`qgis-plugin-manager` is a Python CLI tool built to manage the lifecycle, versioning, scaffolding, and testing of QGIS plugins programmatically.

## When to use this skill
- At the start of a session to refresh the architecture of this CLI.
- When modifying or adding subcommands to the CLI using Typer.
- When the user requests a current status of the QGIS framework.

## Degree of Freedom
- **Strictly guided**: It must be considered that the current development focuses purely on modern Python (Typer and uv), NOT on internal QGIS logic.

## Instructions and Rules

### Core Architecture
- CLI built on **Typer**.
- Packaging and environment execution managed 100% by **uv**.
- Mandatory and strict static validations using **ruff** (linting) and **mypy** (typing).
- Follows the Antigravity Gen 5 agent standard: custom agent logic is isolated in `.agent`, while blueprints for creating QGIS plugins are injected from `scaffold/`.

### Main Folder Structure
- `src/qgis_manager/`: The main source code of the CLI application.
- `scripts/`: Base MCP tools and skill synchronization tools for the Gen 5 ecosystem.
- `scaffold/`: Base templates and blueprints (QGIS, Mining) that the CLI uses to inject configuration into target systems.
- `docs/`: Documentation, guides, and release notes mapped from `pyproject.toml`.

## Quality Checklist
- [ ] Do changes to the CLI maintain command compatibility (properly added to Typer)?
- [ ] Did local tests pass using `pytest`, `ruff`, and `mypy` via `uv run`?
- [ ] Does the change respect the separation between the manager tool (CLI) and the target templates/plugins?
