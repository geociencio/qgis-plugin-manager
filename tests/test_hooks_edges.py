"""Additional hook execution branches."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.hooks import HookPolicy, execute_python_hook, run_hook


class TestHooksEdges(unittest.TestCase):
    def test_python_hook_without_matching_function(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "plugin_hooks.py").write_text(
                "def other_hook(context):\n    return True\n",
                encoding="utf-8",
            )
            self.assertTrue(execute_python_hook(root, "pre_deploy", {}))

    def test_run_python_script_hook(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            marker = root / "marker.txt"
            script = root / "hook.py"
            script.write_text(
                f"from pathlib import Path\nPath({str(marker)!r}).write_text('ok')\n",
                encoding="utf-8",
            )
            self.assertTrue(run_hook("pre_deploy", str(script), root))
            self.assertEqual(marker.read_text(encoding="utf-8"), "ok")

    def test_run_hook_non_shell_policy(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            with patch("qgis_manager.hooks.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                result = run_hook(
                    "pre_deploy",
                    f"{sys.executable} -c \"print('ok')\"",
                    root,
                    policy=HookPolicy(shell=False),
                )
        self.assertTrue(result)
        self.assertFalse(mock_run.call_args.kwargs["shell"])
        self.assertIsInstance(mock_run.call_args.args[0], list)

    @patch("qgis_manager.hooks.subprocess.run")
    def test_run_hook_failure_with_output(self, mock_run):
        mock_run.return_value = Mock(returncode=2, stdout="out", stderr="err")
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_hook("pre_deploy", "false", Path(tmp_dir))
        self.assertFalse(result)
