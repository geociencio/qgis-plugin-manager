# Contributing to QGIS Plugin Manager

Thank you for your interest in contributing to the QGIS Plugin Manager!

## 🚀 Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/geociencio/qgis-plugin-manager.git
    cd qgis-plugin-manager
    ```

2.  **Install dependencies** (using `uv`):
    ```bash
    uv sync
    ```

3.  **Install pre-commit hooks**:
    ```bash
    uv run pre-commit install
    ```

## 🛠️ Development Workflow

### Running Tests
We use `pytest` for testing:
```bash
uv run pytest
```

### Linting and Formatting
We use `ruff` for both linting and formatting:
```bash
uv run ruff check src/
uv run ruff format src/
```

### Type Checking
We use `mypy`:
```bash
uv run mypy src/
```

## 📝 Commit Guidelines
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

## 📜 License
By contributing, you agree that your contributions will be licensed under the **GNU General Public License v2.0 or later**.
