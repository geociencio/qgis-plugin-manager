"""Tests for the stdlib-only console adapter."""

from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from qgis_manager.cli import console


def test_echo_stdout_stderr_and_nl() -> None:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        console.echo("hello")
        console.echo("bad", err=True, nl=False)
    assert out.getvalue() == "hello\n"
    assert err.getvalue() == "bad"


def test_style_strips_color_when_not_a_tty() -> None:
    assert console.style("x", fg="red", bold=True) == "x"


def test_style_emits_ansi_on_tty() -> None:
    with (
        patch.object(console.sys.stdout, "isatty", return_value=True),
        patch.dict("os.environ", {}, clear=True),
    ):
        styled = console.style("x", fg="red", bold=True)
    assert "\033[1;31m" in styled and styled.endswith("\033[0m")


def test_style_respects_no_color() -> None:
    with (
        patch.object(console.sys.stdout, "isatty", return_value=True),
        patch.dict("os.environ", {"NO_COLOR": "1"}, clear=True),
    ):
        assert console.style("x", fg="red") == "x"


def test_confirm_variants() -> None:
    with patch("builtins.input", return_value=""):
        assert console.confirm("ok?", default=True) is True
    with patch("builtins.input", return_value="no"):
        assert console.confirm("ok?") is False
    with patch("builtins.input", side_effect=EOFError):
        assert console.confirm("ok?") is False


def test_prompt_variants() -> None:
    with patch("builtins.input", return_value="value"):
        assert console.prompt("name", default="fallback") == "value"
    with patch("builtins.input", return_value=""):
        assert console.prompt("name", default="fallback") == "fallback"
    with patch("builtins.input", side_effect=EOFError):
        assert console.prompt("name", default="fallback") == "fallback"


def test_progressbar_updates_label_and_position() -> None:
    with (
        patch.object(console.sys.stderr, "isatty", return_value=True),
        patch.object(console.sys.stderr, "write") as mock_write,
        patch.object(console.sys.stderr, "flush"),
    ):
        with console.progressbar(2, label="work") as bar:
            bar.update(1)
            bar.label = "next"
            bar.update(1)
    written = "".join(call.args[0] for call in mock_write.call_args_list)
    assert "work" in written
    assert "next" in written
    assert "(2/2)" in written


def test_progressbar_quiet_when_not_tty() -> None:
    with (
        patch.object(console.sys.stderr, "isatty", return_value=False),
        patch.object(console.sys.stderr, "write") as mock_write,
    ):
        with console.progressbar(1, label="work") as bar:
            bar.update(1)
    mock_write.assert_not_called()


def test_style_without_codes_on_tty() -> None:
    with (
        patch.object(console.sys.stdout, "isatty", return_value=True),
        patch.dict("os.environ", {}, clear=True),
    ):
        assert console.style("plain") == "plain"
        assert console.style("plain", fg="unknown") == "plain"


def test_style_disabled_for_dumb_terminal() -> None:
    with (
        patch.object(console.sys.stdout, "isatty", return_value=True),
        patch.dict("os.environ", {"TERM": "dumb"}, clear=True),
    ):
        assert console.style("plain", fg="red") == "plain"


def test_progressbar_clamps_and_quiet_finish() -> None:
    bar = console.ProgressBar(1, label="x")
    bar.update(99)
    assert bar.current == 1
    bar.finish()


def test_progressbar_without_position() -> None:
    with (
        patch.object(console.sys.stderr, "isatty", return_value=True),
        patch.object(console.sys.stderr, "write") as mock_write,
        patch.object(console.sys.stderr, "flush"),
    ):
        with console.progressbar(2, label="work", show_pos=False) as bar:
            bar.update(1)
    assert "(1/2)" not in "".join(call.args[0] for call in mock_write.call_args_list)
