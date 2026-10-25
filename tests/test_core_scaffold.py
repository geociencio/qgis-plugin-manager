import tempfile
import unittest
from pathlib import Path

from qgis_manager.core import (
    clean_artifacts,
    init_plugin_project,
)


class TestCoreScaffold(unittest.TestCase):
    def test_clean_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            pycache = tmp_path / "__pycache__"
            pycache.mkdir()
            pyc_file = tmp_path / "file.pyc"
            pyc_file.touch()

            # Execute
            clean_artifacts(tmp_path)

            # Verify
            self.assertFalse(pycache.exists())
            self.assertFalse(pyc_file.exists())

    def test_init_plugin_project(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Setup
            plugin_name = "My New Plugin"
            author = "John Doe"
            email = "john@example.com"
            description = "Cool description"

            # Execute
            init_plugin_project(tmp_path, plugin_name, author, email, description)

            # Verify directory
            plugin_dir = tmp_path / "my_new_plugin"
            self.assertTrue(plugin_dir.exists())
            self.assertTrue(plugin_dir.is_dir())

            # Verify metadata.txt
            metadata_file = plugin_dir / "metadata.txt"
            self.assertTrue(metadata_file.exists())
            content = metadata_file.read_text()
            self.assertIn("name=My New Plugin", content)
            self.assertIn("author=John Doe", content)
            self.assertIn("email=john@example.com", content)
            self.assertIn("description=Cool description", content)

    def test_init_plugin_project_processing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            init_plugin_project(
                Path(tmp_dir), "My Plugin", "A", "a@b.c", template="processing"
            )
            plugin_dir = Path(tmp_dir) / "my_plugin"
            self.assertTrue((plugin_dir / "my_plugin.py").exists())
            self.assertTrue((plugin_dir / "my_plugin_provider.py").exists())
            self.assertTrue((plugin_dir / "my_plugin_algorithm.py").exists())
            self.assertTrue((plugin_dir / "__init__.py").exists())
            self.assertTrue((plugin_dir / "metadata.txt").exists())
            provider = (plugin_dir / "my_plugin_provider.py").read_text()
            self.assertIn("MyPluginAlgorithm", provider)

    def test_init_plugin_project_dockwidget(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            init_plugin_project(
                Path(tmp_dir), "My Plugin", "A", "a@b.c", template="dockwidget"
            )
            plugin_dir = Path(tmp_dir) / "my_plugin"
            self.assertTrue((plugin_dir / "my_plugin.py").exists())
            self.assertTrue((plugin_dir / "my_plugin_dockwidget.py").exists())
            self.assertTrue((plugin_dir / "my_plugin_dockwidget_base.ui").exists())
            self.assertTrue((plugin_dir / "metadata.txt").exists())

    def test_init_plugin_project_unknown_template(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(ValueError):
                init_plugin_project(Path(tmp_dir), "X", "A", "a@b.c", template="nope")

    def test_init_plugin_project_rejects_empty_slug(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(ValueError, "Invalid plugin name slug"):
                init_plugin_project(Path(tmp_dir), "!!!", "A", "a@b.c")

    def test_init_plugin_project_metadata_is_valid(self):
        from qgis_manager.discovery import get_plugin_metadata
        from qgis_manager.validation import validate_metadata

        with tempfile.TemporaryDirectory() as tmp_dir:
            init_plugin_project(Path(tmp_dir), "Valid Plugin", "A", "a@b.co")
            project = Path(tmp_dir) / "valid_plugin"
            result = validate_metadata(get_plugin_metadata(project))
            self.assertTrue(result.is_valid, result.errors)

    def test_init_plugin_project_generates_valid_python_for_unusual_names(self):
        import ast

        names = ["My-Weird Plugin (Ñ)", "123 Plugin", "None"]
        for template in ("default", "processing", "dockwidget"):
            for name in names:
                with self.subTest(template=template, name=name):
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        init_plugin_project(
                            Path(tmp_dir), name, "A", "a@b.c", template=template
                        )
                        projects = [p for p in Path(tmp_dir).iterdir() if p.is_dir()]
                        self.assertEqual(len(projects), 1)
                        project = projects[0]
                        self.assertNotIn("-", project.name)
                        self.assertNotIn("(", project.name)
                        py_files = list(project.glob("*.py"))
                        self.assertTrue(py_files)
                        for py_file in py_files:
                            ast.parse(py_file.read_text(encoding="utf-8"))

    def test_clean_artifacts_compiled(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "dialog.ui").touch()
            (tmp_path / "dialog.py").write_text("compiled", encoding="utf-8")
            (tmp_path / "resources.qrc").touch()
            (tmp_path / "resources.py").write_text("compiled", encoding="utf-8")
            help_html = tmp_path / "help" / "html"
            help_html.mkdir(parents=True)
            (help_html / "index.html").write_text("docs", encoding="utf-8")

            clean_artifacts(tmp_path)

            self.assertFalse((tmp_path / "dialog.py").exists())
            self.assertFalse((tmp_path / "resources.py").exists())
            self.assertFalse((tmp_path / "help" / "html").exists())
            # Sources are preserved
            self.assertTrue((tmp_path / "dialog.ui").exists())
            self.assertTrue((tmp_path / "resources.qrc").exists())

    def test_clean_artifacts_dry_run_preserves_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "a.ui").write_text("<ui/>", encoding="utf-8")
            (root / "a.py").write_text("# generated", encoding="utf-8")
            (root / "__pycache__").mkdir()

            actions = clean_artifacts(root, dry_run=True)

            self.assertTrue((root / "a.py").exists())
            self.assertTrue((root / "__pycache__").exists())
            self.assertTrue(any("remove a.py" in action for action in actions))

    def test_clean_artifacts_keep_generated(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "a.qrc").write_text("<RCC/>", encoding="utf-8")
            (root / "a.py").write_text("# generated", encoding="utf-8")

            actions = clean_artifacts(root, keep_generated=True)

            self.assertTrue((root / "a.py").exists())
            self.assertTrue(any("keep a.py" in action for action in actions))
