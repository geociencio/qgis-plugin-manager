import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch

from qgis_manager.core import (
    create_plugin_package,
    get_git_info,
    is_prerelease,
    stamp_metadata_text,
)


class TestCorePackage(unittest.TestCase):
    def test_create_plugin_package(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("print('hello')\n", encoding="utf-8")

            output = tmp_path / "out"
            zip_path = create_plugin_package(tmp_path, output_dir=output)

            self.assertTrue(zip_path.exists())
            self.assertTrue(zip_path.name.endswith(".zip"))
            # SHA256 checksum file
            checksum_file = Path(str(zip_path) + ".sha256")
            self.assertTrue(checksum_file.exists())
            # ZIP contains the plugin files under slug/
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
            self.assertTrue(any(n.endswith("plugin.py") for n in names))
            self.assertTrue(any(n.endswith("metadata.txt") for n in names))

    def test_create_plugin_package_callback(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("print('hello')\n", encoding="utf-8")

            calls = []
            create_plugin_package(tmp_path, callback=lambda n: calls.append(n))

            self.assertGreater(len(calls), 0)

    def test_create_plugin_package_include_dev(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "docs").mkdir()
            (tmp_path / "docs" / "readme.md").write_text("docs", encoding="utf-8")

            output = tmp_path / "out"
            zip_path = create_plugin_package(
                tmp_path, output_dir=output, include_dev=True
            )
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
            self.assertTrue(any("docs" in n for n in names))

    def test_is_prerelease(self):
        self.assertTrue(is_prerelease("1.0.0-rc1"))
        self.assertTrue(is_prerelease("1.0.0-beta2"))
        self.assertTrue(is_prerelease("1.0.0-alpha"))
        self.assertTrue(is_prerelease("1.0.0.dev0"))
        self.assertFalse(is_prerelease("1.0.0"))
        self.assertFalse(is_prerelease("2.3.4"))

    def test_stamp_metadata_text_updates_and_appends(self):
        text = "; comment\n[general]\nname=My Plugin\nversion=1.0.0\n"
        result = stamp_metadata_text(
            text,
            version="2.0.0",
            commit_sha="abc123",
            commit_number=42,
            timestamp="2026-01-01T00:00:00Z",
            experimental=False,
        )
        self.assertIn("version=2.0.0", result)
        self.assertIn("commitSha1=abc123", result)
        self.assertIn("commitNumber=42", result)
        self.assertIn("dateTime=2026-01-01T00:00:00Z", result)
        self.assertIn("experimental=False", result)
        self.assertIn("; comment", result)
        self.assertIn("name=My Plugin", result)

    def test_stamp_metadata_text_appends_before_next_section(self):
        text = "[general]\nname=X\nversion=1.0.0\n\n[tags]\nfoo=bar\n"
        result = stamp_metadata_text(text, commit_sha="abc")
        self.assertLess(result.index("version=1.0.0"), result.index("commitSha1=abc"))
        self.assertLess(result.index("commitSha1=abc"), result.index("[tags]"))

    def test_stamp_metadata_text_no_updates(self):
        text = "[general]\nname=X\n"
        self.assertEqual(stamp_metadata_text(text), text)

    @patch("qgis_manager.core.package.subprocess.run")
    def test_get_git_info(self, mock_run):
        mock_run.side_effect = [Mock(stdout="abc123\n"), Mock(stdout="42\n")]
        self.assertEqual(get_git_info(Path(".")), ("abc123", 42))

    @patch("qgis_manager.core.package.subprocess.run", side_effect=FileNotFoundError)
    def test_get_git_info_not_a_repo(self, _mock_run):
        self.assertEqual(get_git_info(Path(".")), (None, None))

    @patch("qgis_manager.core.package.get_git_info", return_value=("abc123", 10))
    def test_create_plugin_package_stamp(self, _mock_git):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "metadata.txt").write_text(
                "[general]\nname=My Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (tmp_path / "plugin.py").write_text("x=1\n", encoding="utf-8")

            zip_path = create_plugin_package(
                tmp_path, output_dir=tmp_path / "out", stamp=True
            )

            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                metadata_name = next(n for n in names if n.endswith("metadata.txt"))
                content = zf.read(metadata_name).decode("utf-8")

            self.assertIn("commitSha1=abc123", content)
            self.assertIn("commitNumber=10", content)
            self.assertIn("dateTime=", content)
            self.assertIn("experimental=False", content)
            self.assertIn("version=1.0.0", content)
            # Source metadata.txt must not be modified
            self.assertNotIn("commitSha1", (tmp_path / "metadata.txt").read_text())

    def test_stamped_metadata_without_metadata_file(self):
        from qgis_manager.core.package import _build_stamped_metadata

        with tempfile.TemporaryDirectory() as tmp_dir:
            self.assertIsNone(_build_stamped_metadata(Path(tmp_dir), "1.0.0"))

    def test_create_package_rejects_unsafe_release_version(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo\nversion=1.0.0\n", encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                create_plugin_package(root, release_version="..")

    def test_normalized_permissions_and_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (root / "plugin.py").write_text("x=1\n", encoding="utf-8")
            zip_path = create_plugin_package(
                root,
                output_dir=root / "out",
                normalize_permissions=True,
            )
            with zipfile.ZipFile(zip_path) as archive:
                for info in archive.infolist():
                    self.assertEqual(
                        (info.external_attr >> 16) & 0o777, 0o644, info.filename
                    )
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))

    def test_normalized_executable_mode(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            script = root / "run.py"
            script.write_text("print('x')\n", encoding="utf-8")
            script.chmod(0o755)
            zip_path = create_plugin_package(
                root, output_dir=root / "out", normalize_permissions=True
            )
            with zipfile.ZipFile(zip_path) as archive:
                info = archive.getinfo("demo_plugin/run.py")
            self.assertEqual((info.external_attr >> 16) & 0o777, 0o755)

    def test_source_date_epoch_controls_zip_timestamp(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo Plugin\nversion=1.0.0\n", encoding="utf-8"
            )
            (root / "plugin.py").write_text("x=1\n", encoding="utf-8")
            with patch.dict("os.environ", {"SOURCE_DATE_EPOCH": "1700000000"}):
                zip_path = create_plugin_package(
                    root, output_dir=root / "out", normalize_permissions=True
                )
            with zipfile.ZipFile(zip_path) as archive:
                date = archive.getinfo("demo_plugin/plugin.py").date_time
        self.assertEqual(date, (2023, 11, 14, 22, 13, 20))
