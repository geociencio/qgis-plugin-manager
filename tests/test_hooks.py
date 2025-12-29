from pathlib import Path

from qgis_manager.hooks import run_hook


def test_run_hook_success(tmp_path: Path):
    # Setup
    hook_name = "test-hook"
    # Use a Python one-liner to avoid shell-specific quoting issues.
    command = (
        "python -c \"from pathlib import Path; Path('output.txt').write_text('hello')\""
    )

    # Execute
    result = run_hook(hook_name, command, tmp_path)

    # Verify
    assert result is True
    assert (tmp_path / "output.txt").exists()
    assert (tmp_path / "output.txt").read_text().strip() == "hello"


def test_run_hook_failure(tmp_path: Path):
    # Setup
    hook_name = "fail-hook"
    command = "exit 1"

    # Execute
    result = run_hook(hook_name, command, tmp_path)

    # Verify
    assert result is False


def test_run_hook_empty(tmp_path: Path):
    assert run_hook("empty", "", tmp_path) is True
