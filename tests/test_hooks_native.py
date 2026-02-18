import shutil
import tempfile
import unittest
from pathlib import Path

from src.qgis_manager.hooks import run_hook


class TestNativeHooks(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.hooks_file = self.test_dir / "plugin_hooks.py"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_native_hook_execution(self):
        # Create a plugin_hooks.py that writes to a file
        marker_file = self.test_dir / "hook_executed.txt"
        content = f"""
def pre_deploy(context):
    with open(r'{marker_file}', 'w') as f:
        f.write('success')
    return True
"""
        self.hooks_file.write_text(content)

        # Run hook
        success = run_hook("pre-deploy", None, self.test_dir)

        self.assertTrue(success)
        self.assertTrue(marker_file.exists())
        self.assertEqual(marker_file.read_text(), "success")

    def test_native_hook_failure(self):
        content = """
def pre_deploy(context):
    return False
"""
        self.hooks_file.write_text(content)

        success = run_hook("pre-deploy", None, self.test_dir)
        self.assertFalse(success)

    def test_native_hook_with_context(self):
        marker_file = self.test_dir / "ctx_val.txt"
        content = f"""
def pre_deploy(context):
    val = context.get('my_val', 'none')
    with open(r'{marker_file}', 'w') as f:
        f.write(val)
    return True
"""
        self.hooks_file.write_text(content)

        ctx = {"my_val": "hello_context"}
        run_hook("pre-deploy", None, self.test_dir, context=ctx)

        self.assertTrue(marker_file.exists())
        self.assertEqual(marker_file.read_text(), "hello_context")

    def test_fallback_to_command(self):
        # No native hook, but a command
        # On linux 'touch' should work
        marker_file = self.test_dir / "cmd_executed.txt"
        cmd = f"touch {marker_file}"

        success = run_hook("pre-deploy", cmd, self.test_dir)

        self.assertTrue(success)
        self.assertTrue(marker_file.exists())


if __name__ == "__main__":
    unittest.main()
