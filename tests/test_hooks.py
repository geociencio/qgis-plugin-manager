import tempfile
import unittest
from pathlib import Path

from qgis_manager.hooks import run_hook


class TestHooks(unittest.TestCase):
    def test_run_hook_success(self):
        # Setup
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            hook_name = "test-hook"
            # Use a Python one-liner to avoid shell-specific quoting issues.
            command = (
                'python -c "from pathlib import Path; '
                "Path('output.txt').write_text('hello')\""
            )

            # Execute
            result = run_hook(hook_name, command, tmp_path)

            # Verify
            self.assertTrue(result)
            self.assertTrue((tmp_path / "output.txt").exists())
            self.assertEqual((tmp_path / "output.txt").read_text().strip(), "hello")

    def test_run_hook_failure(self):
        # Setup
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            hook_name = "fail-hook"
            command = "exit 1"

            # Execute
            result = run_hook(hook_name, command, tmp_path)

            # Verify
            self.assertFalse(result)

    def test_run_hook_empty(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            self.assertTrue(run_hook("empty", "", tmp_path))


if __name__ == "__main__":
    unittest.main()
