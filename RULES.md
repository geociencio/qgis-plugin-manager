# Development Rules and Standards

This document outlines the coding standards and quality rules that the `qgis-plugin-manager` project follows.

## 🛠️ General Standards

- **Python Version**: 3.10+
- **Package Manager**: `uv`
- **Internal Formatting**: `black`
- **Docstrings**: Google/Sphinx style.
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/).

## 🔍 Quality Rules (Audited by qgis-analyzer)

The project aims for a high compliance score with QGIS development best practices.

### 1. Logging and Output
- **Rule**: Avoid raw `print()` statements for core logic that might run within QGIS.
- **Guideline**: Use `QgsMessageLog` for QGIS interaction or a standard `logging` module for CLI tools.

### 2. Plugin Structure
- **Rule**: Every plugin project must contain a valid `metadata.txt` and `__init__.py`.
- **Guideline**: `metadata.txt` must include mandatory fields: `name`, `description`, `version`, `qgisMinimumVersion`, `author`, `email`.

### 3. Safety and Deployment
- **Rule**: Never overwrite a user's existing plugin folder without a backup.
- **Guideline**: Use the built-in backup mechanism (`.bak.[timestamp]`) before deployment.

### 4. Cleanup
- **Rule**: Keep the repository clean of build artifacts.
- **Guideline**: Regularly use `qgis-manage clean` before committing or packaging.
