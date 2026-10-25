import tempfile
import unittest
from pathlib import Path

from qgis_manager.validation import (
    get_required_fields,
    validate_boolean_field,
    validate_category,
    validate_email,
    validate_metadata,
    validate_official_compliance,
    validate_tags,
    validate_url,
    validate_version,
)


class TestValidation(unittest.TestCase):
    def test_get_required_fields(self):
        required = get_required_fields()
        self.assertIn("name", required)
        self.assertIn("description", required)
        self.assertIn("about", required)
        self.assertIn("version", required)
        self.assertIn("qgisMinimumVersion", required)
        self.assertIn("author", required)
        self.assertIn("email", required)
        self.assertNotIn("repository", required)

    def test_validate_version_valid(self):
        self.assertTrue(validate_version("1.0.0"))
        self.assertTrue(validate_version("2.5.3"))
        self.assertTrue(validate_version("0.1"))
        self.assertTrue(validate_version("10.20.30"))
        self.assertTrue(validate_version("1.0.0-beta"))

    def test_validate_version_short_form_only_when_allowed(self):
        self.assertTrue(validate_version("3.0", allow_short=True))
        self.assertFalse(validate_version("3.0", allow_short=False))
        self.assertTrue(validate_version("3.0.0", allow_short=False))

    def test_validate_version_invalid(self):
        self.assertFalse(validate_version("1"))
        self.assertFalse(validate_version("v1.0.0"))
        self.assertFalse(validate_version("1.0.invalid"))
        self.assertFalse(validate_version("invalid"))

    def test_validate_email_valid(self):
        self.assertTrue(validate_email("user@example.com"))
        self.assertTrue(validate_email("test.user@domain.co.uk"))
        self.assertTrue(validate_email("name+tag@example.org"))

    def test_validate_email_invalid(self):
        self.assertFalse(validate_email("invalid"))
        self.assertFalse(validate_email("@example.com"))
        self.assertFalse(validate_email("user@"))
        self.assertFalse(validate_email("user @example.com"))

    def test_validate_url_valid(self):
        self.assertTrue(validate_url("https://example.com"))
        self.assertTrue(validate_url("http://github.com/user/repo"))
        self.assertTrue(validate_url("https://example.com/path?query=value"))

    def test_validate_url_invalid(self):
        self.assertFalse(validate_url("ftp://example.com"))
        self.assertFalse(validate_url("example.com"))
        self.assertFalse(validate_url("not a url"))

    def test_validate_metadata_complete(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "about": "A longer description of the test plugin",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
            "homepage": "https://example.com",
            "repository": "https://github.com/user/repo",
            "tags": "test,plugin",
        }
        result = validate_metadata(metadata)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)

    def test_validate_metadata_requires_about(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
        }
        result = validate_metadata(metadata)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("'about'" in error for error in result.errors))

    def test_validate_metadata_missing_repository_is_warning(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "about": "About",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
        }
        result = validate_metadata(metadata)
        self.assertTrue(result.is_valid)
        self.assertTrue(any("'repository'" in w for w in result.warnings))

    def test_validate_metadata_rejects_short_plugin_version(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "about": "About",
            "version": "1.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
            "repository": "https://example.com/repo",
        }
        result = validate_metadata(metadata)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Invalid version format" in e for e in result.errors))

    def test_validate_metadata_boolean_values(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "about": "About",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
            "repository": "https://example.com/repo",
            "experimental": "False",
            "deprecated": "False",
            "hasProcessingProvider": "False",
        }
        result = validate_metadata(metadata)
        self.assertFalse(
            any("should be 'True' or 'False'" in w for w in result.warnings)
        )

        metadata["experimental"] = "yes"
        result = validate_metadata(metadata)
        self.assertTrue(
            any("'experimental'" in w and "should be" in w for w in result.warnings)
        )

    def test_validate_metadata_missing_required(self):
        metadata = {
            "name": "Test Plugin",
            # Missing description, version, etc.
        }
        result = validate_metadata(metadata)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("description" in error for error in result.errors))

    def test_validate_metadata_invalid_version(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "version": "invalid",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
        }
        result = validate_metadata(metadata)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("version" in error.lower() for error in result.errors))

    def test_validate_metadata_invalid_email(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "invalid-email",
        }
        result = validate_metadata(metadata)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("email" in error.lower() for error in result.errors))

    def test_validate_metadata_warnings(self):
        metadata = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "about": "About",
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
            "repository": "https://example.com/repo",
            # Missing recommended fields: homepage and tags
        }
        result = validate_metadata(metadata)
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertTrue(
            any("homepage" in warning.lower() for warning in result.warnings)
        )

    def test_validate_category(self):
        self.assertTrue(validate_category("Vector"))
        self.assertTrue(validate_category("Processing"))
        self.assertFalse(validate_category("Unknown"))

    def test_validate_tags(self):
        self.assertTrue(validate_tags("raster, processing"))
        self.assertFalse(validate_tags(""))
        self.assertFalse(validate_tags(",,"))

    def test_validate_boolean_field(self):
        self.assertTrue(validate_boolean_field("True"))
        self.assertTrue(validate_boolean_field("False"))
        self.assertFalse(validate_boolean_field("true"))
        self.assertFalse(validate_boolean_field("yes"))

    def test_validate_official_compliance_binary(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "LICENSE").write_text("GPL", encoding="utf-8")
            (root / "plugin.so").touch()

            result = validate_official_compliance(root)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("binaries" in e.lower() for e in result.errors))

    def test_validate_official_compliance_missing_license(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            result = validate_official_compliance(root)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("LICENSE" in e for e in result.errors))

    def test_validate_official_compliance_license_variant(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "LICENSE.md").write_text("GPL", encoding="utf-8")

            result = validate_official_compliance(root)
            self.assertFalse(result.is_valid)
            self.assertTrue(any("LICENSE" in e for e in result.errors))

    def test_validate_official_compliance_ignores_venv_binaries(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "LICENSE").write_text("GPL", encoding="utf-8")
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo\n", encoding="utf-8"
            )
            venv_lib = root / ".venv" / "lib"
            venv_lib.mkdir(parents=True)
            (venv_lib / "native.so").touch()

            result = validate_official_compliance(root)
            self.assertTrue(result.is_valid, result.errors)

    def test_validate_official_compliance_requires_repo_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "LICENSE").write_text("GPL", encoding="utf-8")
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo\n", encoding="utf-8"
            )

            result = validate_official_compliance(root, {"name": "Demo"})
            self.assertFalse(result.is_valid)
            self.assertTrue(any("'about'" in e for e in result.errors))
            self.assertTrue(any("'repository'" in e for e in result.errors))

    def test_validate_official_compliance_valid(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "LICENSE").write_text("GPL", encoding="utf-8")
            (root / "metadata.txt").write_text(
                "[general]\nname=Demo\n", encoding="utf-8"
            )

            result = validate_official_compliance(root)
            self.assertTrue(result.is_valid, result.errors)


if __name__ == "__main__":
    unittest.main()
