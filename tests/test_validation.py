from qgis_manager.validation import (
    get_optional_fields,
    get_required_fields,
    validate_email,
    validate_metadata,
    validate_url,
    validate_version,
)


def test_get_required_fields():
    required = get_required_fields()
    assert "name" in required
    assert "description" in required
    assert "version" in required
    assert "qgisMinimumVersion" in required
    assert "author" in required
    assert "email" in required


def test_get_optional_fields():
    optional = get_optional_fields()
    assert "homepage" in optional
    assert "repository" in optional
    assert "tags" in optional


def test_validate_version_valid():
    assert validate_version("1.0.0") is True
    assert validate_version("2.5.3") is True
    assert validate_version("0.1") is True
    assert validate_version("10.20.30") is True


def test_validate_version_invalid():
    assert validate_version("1") is False
    assert validate_version("v1.0.0") is False
    assert validate_version("1.0.0-beta") is False
    assert validate_version("invalid") is False


def test_validate_email_valid():
    assert validate_email("user@example.com") is True
    assert validate_email("test.user@domain.co.uk") is True
    assert validate_email("name+tag@example.org") is True


def test_validate_email_invalid():
    assert validate_email("invalid") is False
    assert validate_email("@example.com") is False
    assert validate_email("user@") is False
    assert validate_email("user @example.com") is False


def test_validate_url_valid():
    assert validate_url("https://example.com") is True
    assert validate_url("http://github.com/user/repo") is True
    assert validate_url("https://example.com/path?query=value") is True


def test_validate_url_invalid():
    assert validate_url("ftp://example.com") is False
    assert validate_url("example.com") is False
    assert validate_url("not a url") is False


def test_validate_metadata_complete():
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
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert len(result.warnings) == 0


def test_validate_metadata_missing_required():
    metadata = {
        "name": "Test Plugin",
        # Missing description, version, etc.
    }
    result = validate_metadata(metadata)
    assert result.is_valid is False
    assert len(result.errors) > 0
    assert any("description" in error for error in result.errors)


def test_validate_metadata_invalid_version():
    metadata = {
        "name": "Test Plugin",
        "description": "A test plugin",
        "version": "invalid",
        "qgisMinimumVersion": "3.0",
        "author": "Test Author",
        "email": "test@example.com",
    }
    result = validate_metadata(metadata)
    assert result.is_valid is False
    assert any("version" in error.lower() for error in result.errors)


def test_validate_metadata_invalid_email():
    metadata = {
        "name": "Test Plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "qgisMinimumVersion": "3.0",
        "author": "Test Author",
        "email": "invalid-email",
    }
    result = validate_metadata(metadata)
    assert result.is_valid is False
    assert any("email" in error.lower() for error in result.errors)


def test_validate_metadata_warnings():
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
    assert result.is_valid is True
    assert len(result.warnings) > 0
    assert any("homepage" in warning.lower() for warning in result.warnings)
