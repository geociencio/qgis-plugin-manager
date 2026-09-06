import unittest

from qgis_manager.templating import render, render_template


class TestTemplating(unittest.TestCase):
    def test_render(self):
        self.assertEqual(render("Hello {{ name }}!", name="World"), "Hello World!")
        self.assertEqual(render("{{ a }}{{ b }}", a="1", b="2"), "12")
        self.assertEqual(render("{{ slug }}.py", slug="my_plugin"), "my_plugin.py")

    def test_render_unknown_placeholder_left_untouched(self):
        self.assertEqual(render("{{ unknown }}", name="x"), "{{ unknown }}")

    def test_render_template(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmpl = Path(tmp_dir) / "t.txt"
            tmpl.write_text("name={{ name }}", encoding="utf-8")
            self.assertEqual(render_template(tmpl, name="Demo"), "name=Demo")


if __name__ == "__main__":
    unittest.main()
