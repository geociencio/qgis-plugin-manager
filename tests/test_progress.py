import unittest

from qgis_manager.cli.progress import make_compile_callback


class FakeBar:
    def __init__(self) -> None:
        self.label = ""
        self.updates: list[int] = []

    def update(self, n: int) -> None:
        self.updates.append(n)


class TestProgress(unittest.TestCase):
    def test_start_branch_selects_icon(self):
        bar = FakeBar()
        callback = make_compile_callback(bar)

        callback("START:Recurso icon.png")
        self.assertIn("🔨", bar.label)
        self.assertIn("Recurso icon.png", bar.label)

        callback("START:Trad es.ts")
        self.assertIn("🌍", bar.label)

        callback("START:Documentación")
        self.assertIn("📚", bar.label)

    def test_progress_branch_updates_label(self):
        bar = FakeBar()
        callback = make_compile_callback(bar)

        callback("PROGRESS:compiling something")
        self.assertTrue(bar.label.startswith("📚"))

    def test_done_branch_increments_bar(self):
        bar = FakeBar()
        callback = make_compile_callback(bar)

        callback("DONE:Recurso icon.png")
        self.assertEqual(bar.updates, [1])

    def test_shortens_long_messages(self):
        bar = FakeBar()
        callback = make_compile_callback(bar)

        callback("START:Recurso " + "x" * 100)
        self.assertIn("...", bar.label)


if __name__ == "__main__":
    unittest.main()
