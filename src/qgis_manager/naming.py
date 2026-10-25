"""Slug generation and validation for plugin/project names."""

import re
import unicodedata

#: A slug that is safe to use as a directory/module name inside a QGIS profile.
_SLUG_RE = re.compile(r"^[a-z_][a-z0-9_]*$")

#: Names that cannot be used as a directory on Windows.
_RESERVED_SLUGS = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


def slugify(text: str) -> str:
    """Convert text to a safe ASCII directory/module name slug.

    Non-ASCII characters are transliterated or dropped (``Café`` -> ``cafe``),
    spaces and separators collapse to underscores, and a leading underscore is
    added when the result would start with a digit so it remains a valid Python
    identifier.  An empty string is returned when no ASCII alphanumeric
    character is left; callers must reject that result.

    Args:
        text: Input string to be converted into a slug.

    Returns:
        A lowercase ASCII slug using only letters, digits and underscores.
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    if ascii_text and ascii_text[0].isdigit():
        return f"_{ascii_text}"
    return ascii_text


def validate_slug(slug: str, *, source: str = "plugin") -> str:
    """Validate a plugin slug before using it in a filesystem operation.

    Empty slugs are the dangerous case: joining them with a plugins directory
    yields the directory itself, so a recursive delete/sync could affect every
    installed plugin.  Only ASCII lowercase letters, digits and underscores are
    accepted (the first character may be an underscore).

    Args:
        slug: Slug to validate.
        source: Human-readable origin of the slug, used in the error message.

    Returns:
        The validated slug.

    Raises:
        ValueError: If the slug is empty or contains unsafe characters.
    """
    if not slug or not _SLUG_RE.fullmatch(slug) or slug in _RESERVED_SLUGS:
        raise ValueError(
            f"Invalid {source} slug {slug!r}. The name must contain at least "
            "one ASCII letter or digit and may only use letters, digits and "
            "underscores after normalization."
        )
    return slug
