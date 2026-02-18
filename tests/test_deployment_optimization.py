import shutil
import tempfile
import time
import unittest
from pathlib import Path

from src.qgis_manager.core import rotate_backups, sync_directory
from src.qgis_manager.ignore import PathFilter


class TestDeploymentOptimization(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.src = self.test_dir / "src"
        self.dst = self.test_dir / "dst"
        self.src.mkdir()
        self.dst.mkdir()

        # Empty PathFilter (don't ignore anything for testing sync)
        self.matcher = PathFilter(self.src, [])

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_rotate_backups(self):
        slug = "myplugin"
        # Create 5 backups
        for i in range(1, 6):
            # Use format that sorts correctly
            bak = self.dst / f"{slug}.bak.2026010{i}000000"
            bak.mkdir()

        rotate_backups(self.dst, slug, limit=3)

        remaining = list(self.dst.glob(f"{slug}.bak.*"))
        self.assertEqual(len(remaining), 3)

        # Verify the newest remain (03, 04, 05)
        names = sorted([r.name for r in remaining])
        self.assertIn(f"{slug}.bak.20260105000000", names)
        self.assertIn(f"{slug}.bak.20260104000000", names)
        self.assertIn(f"{slug}.bak.20260103000000", names)

    def test_sync_directory_initial(self):
        (self.src / "file1.txt").write_text("content1")
        (self.src / "subdir").mkdir()
        (self.src / "subdir" / "file2.txt").write_text("content2")

        sync_directory(self.src, self.dst, self.matcher)

        self.assertTrue((self.dst / "file1.txt").exists())
        self.assertTrue((self.dst / "subdir" / "file2.txt").exists())
        self.assertEqual((self.dst / "file1.txt").read_text(), "content1")

    def test_sync_directory_update(self):
        f1 = self.src / "file1.txt"
        f1.write_text("content1")
        sync_directory(self.src, self.dst, self.matcher)

        # Capture mtime
        dst_f1 = self.dst / "file1.txt"
        old_mtime = dst_f1.stat().st_mtime

        # Small delay to ensure timestamp change if we update
        time.sleep(0.1)

        # 1. No change -> mtime should be same
        sync_directory(self.src, self.dst, self.matcher)
        self.assertEqual(dst_f1.stat().st_mtime, old_mtime)

        # 2. Change content -> mtime should update
        f1.write_text("new content")
        sync_directory(self.src, self.dst, self.matcher)
        self.assertNotEqual(dst_f1.stat().st_mtime, old_mtime)
        self.assertEqual(dst_f1.read_text(), "new content")

    def test_sync_directory_cleanup(self):
        (self.src / "file1.txt").write_text("content1")
        (self.src / "file2.txt").write_text("content2")
        sync_directory(self.src, self.dst, self.matcher)

        self.assertTrue((self.dst / "file2.txt").exists())

        # Remove in source
        (self.src / "file2.txt").unlink()
        sync_directory(self.src, self.dst, self.matcher)

        # Should be removed in destination
        self.assertFalse((self.dst / "file2.txt").exists())
        self.assertTrue((self.dst / "file1.txt").exists())


if __name__ == "__main__":
    unittest.main()
