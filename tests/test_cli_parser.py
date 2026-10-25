"""Tests for the custom argparse help formatter."""

from qgis_manager.cli.parser import HelpfulArgumentParser, _HelpFormatter


def test_formatter_usage_uses_default_prefix() -> None:
    formatter = _HelpFormatter("demo")
    text = formatter._format_usage(None, [], [], None)
    assert "Usage:" in text


def test_help_without_title_description_or_epilog() -> None:
    parser = HelpfulArgumentParser(prog="demo", add_help=False)
    text = parser.format_help()
    assert "Usage:" in text
    assert "demo" in text


def test_help_with_title_description_and_epilog() -> None:
    parser = HelpfulArgumentParser(
        prog="demo",
        description="Demo description",
        epilog="Examples: demo",
        add_help=False,
    )
    parser.set_title("demo v1.0")
    text = parser.format_help()
    assert "demo v1.0" in text
    assert "Demo description" in text
    assert "Examples: demo" in text
