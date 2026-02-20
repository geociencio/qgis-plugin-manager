import unittest

from qgis_manager.validation import (
    get_optional_fields,
    get_required_fields,
    validate_email,
    validate_metadata,
    validate_url,
    validate_version,
)


class TestValidation(unittest.TestCase):
    def test_get_required_fields(self):
        required = get_required_fields()
        self.assertIn("name", required)
        self.assertIn("description", required)
        self.assertIn("version", required)
        self.assertIn("qgisMinimumVersion", required)
        self.assertIn("author", required)
        self.assertIn("email", required)

    def test_get_optional_fields(self):
        optional = get_optional_fields()
        self.assertIn("homepage", optional)
        self.assertIn("repository", optional)
        self.assertIn("tags", optional)

    def test_validate_version_valid(self):
        self.assertTrue(validate_version("1.0.0"))
        self.assertTrue(validate_version("2.5.3"))
        self.assertTrue(validate_version("0.1"))
        self.assertTrue(validate_version("10.20.30"))
        self.assertTrue(validate_version("1.0.0-beta"))

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
            "version": "1.0.0",
            "qgisMinimumVersion": "3.0",
            "author": "Test Author",
            "email": "test@example.com",
            # Missing recommended fields
        }
        result = validate_metadata(metadata)
        self.assertTrue(result.is_valid)
        self.assertGreater(len(result.warnings), 0)
        self.assertTrue(
            any("homepage" in warning.lower() for warning in result.warnings)
        )


if __name__ == "__main__":
    unittest.main()
