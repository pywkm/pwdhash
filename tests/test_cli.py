import runpy
import sys
import types
from collections.abc import Callable
from typing import Any

import pytest

from pwdhash import __version__, cli

PASSWORD = "password12345"
EXPECTED = "0JMBoaKI7NFhObN"


class FakeClipboardError(Exception):
    pass


class FakeClipboard:
    """Stand-in for the pyperclip module."""

    def __init__(self) -> None:
        self.content = "previous"
        self.copied: list[str] = []
        self.broken = False

    def copy(self, text: str) -> None:
        if self.broken:
            raise FakeClipboardError("no clipboard mechanism")
        self.copied.append(text)
        self.content = text

    def paste(self) -> str:
        if self.broken:
            raise FakeClipboardError("no clipboard mechanism")
        return self.content


@pytest.fixture
def clipboard(monkeypatch: pytest.MonkeyPatch) -> FakeClipboard:
    fake = FakeClipboard()
    module = types.ModuleType("pyperclip")
    module.__dict__.update(
        PyperclipException=FakeClipboardError, copy=fake.copy, paste=fake.paste
    )
    monkeypatch.setitem(sys.modules, "pyperclip", module)
    return fake


@pytest.fixture
def prompts(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    asked: list[str] = []

    def getpass(prompt: str) -> str:
        asked.append(prompt)
        return PASSWORD

    monkeypatch.setattr("getpass.getpass", getpass)
    return asked


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    slept: list[float] = []
    monkeypatch.setattr("time.sleep", slept.append)
    return slept


def raising(error: BaseException) -> Callable[..., Any]:
    def function(*_args: object) -> Any:
        raise error

    return function


def test_should_copy_and_clear_clipboard(
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
    sleeps: list[float],
) -> None:
    assert cli.main(["http://www.example.com/x"]) == 0

    assert prompts == ["Password for example.com: "]
    assert clipboard.copied == [EXPECTED, ""]
    assert sleeps == [20.0]
    out, err = capsys.readouterr()
    assert out == ""
    assert EXPECTED not in err
    assert "Password for example.com copied to clipboard." in err
    assert "cleared in 20 s (Ctrl+C to clear now)" in err
    assert "Clipboard cleared." in err


def test_should_clear_after_given_time(
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
    sleeps: list[float],
) -> None:
    assert cli.main(["--clear-after", "2.5", "example.com"]) == 0

    assert sleeps == [2.5]
    assert clipboard.copied == [EXPECTED, ""]
    assert "cleared in 2.5 s" in capsys.readouterr().err


def test_should_not_clear_when_clipboard_changed(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
) -> None:
    def user_copies_something(_seconds: float) -> None:
        clipboard.content = "something else"

    monkeypatch.setattr("time.sleep", user_copies_something)

    assert cli.main(["example.com"]) == 0

    assert clipboard.copied == [EXPECTED]
    assert clipboard.content == "something else"
    assert "left untouched" in capsys.readouterr().err


def test_should_clear_now_on_ctrl_c(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
) -> None:
    monkeypatch.setattr("time.sleep", raising(KeyboardInterrupt()))

    assert cli.main(["example.com"]) == 0

    assert clipboard.copied == [EXPECTED, ""]
    assert "Clipboard cleared." in capsys.readouterr().err


def test_should_report_failure_to_clear(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
) -> None:
    def clipboard_breaks(_seconds: float) -> None:
        clipboard.broken = True

    monkeypatch.setattr("time.sleep", clipboard_breaks)

    assert cli.main(["example.com"]) == 0

    assert "Could not clear the clipboard: no clipboard mechanism" in (
        capsys.readouterr().err
    )


def test_should_not_clear_with_no_clear(
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
    sleeps: list[float],
) -> None:
    assert cli.main(["--no-clear", "example.com"]) == 0

    assert clipboard.copied == [EXPECTED]
    assert sleeps == []
    assert "cleared" not in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["-p", "--print"])
def test_should_print_password(
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
    sleeps: list[float],
    flag: str,
) -> None:
    assert cli.main([flag, "example.com"]) == 0

    assert clipboard.copied == []
    assert sleeps == []
    out, err = capsys.readouterr()
    assert out == f"{EXPECTED}\n"
    assert err == ""


def test_should_print_password_when_clipboard_unavailable(
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    clipboard: FakeClipboard,
    sleeps: list[float],
) -> None:
    clipboard.broken = True

    assert cli.main(["example.com"]) == 0

    assert sleeps == []
    out, err = capsys.readouterr()
    assert out == f"{EXPECTED}\n"
    assert "Clipboard is not available: no clipboard mechanism" in err


def test_should_print_password_without_pyperclip(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
    sleeps: list[float],
) -> None:
    monkeypatch.setitem(sys.modules, "pyperclip", None)  # makes import fail

    assert cli.main(["example.com"]) == 0

    assert sleeps == []
    out, err = capsys.readouterr()
    assert out == f"{EXPECTED}\n"
    assert "pwdhash.py[clipboard]" in err


def test_should_ask_for_domain_when_no_argument(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
) -> None:
    monkeypatch.setattr("builtins.input", lambda: " example.com \n")

    assert cli.main(["--print"]) == 0

    out, err = capsys.readouterr()
    assert out == f"{EXPECTED}\n"
    assert err == "Domain: "


@pytest.mark.parametrize("domain", ["", "   ", "/path", "http://"])
def test_should_reject_invalid_domain(
    capsys: pytest.CaptureFixture[str], prompts: list[str], domain: str
) -> None:
    assert cli.main([domain]) == 2

    assert prompts == []
    out, err = capsys.readouterr()
    assert out == ""
    assert err == f"pwdhash: error: Cannot extract domain from {domain!r}\n"


def test_should_reject_empty_password(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("getpass.getpass", lambda _prompt: "")

    assert cli.main(["--print", "example.com"]) == 2

    out, err = capsys.readouterr()
    assert out == ""
    assert err == "pwdhash: error: the password must not be empty\n"


@pytest.mark.parametrize(
    ("target", "error", "code"),
    [
        ("builtins.input", KeyboardInterrupt(), 130),
        ("builtins.input", EOFError(), 1),
        ("getpass.getpass", KeyboardInterrupt(), 130),
        ("getpass.getpass", EOFError(), 1),
    ],
)
def test_should_exit_quietly_on_interrupt(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    target: str,
    error: BaseException,
    code: int,
) -> None:
    monkeypatch.setattr("getpass.getpass", lambda _prompt: PASSWORD)
    monkeypatch.setattr(target, raising(error))
    argv = [] if target == "builtins.input" else ["example.com"]

    assert cli.main(argv) == code

    out, err = capsys.readouterr()
    assert out == ""
    assert err.endswith("\n")
    assert "Traceback" not in err


def test_should_show_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--version"])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"pwdhash {__version__}\n"


@pytest.mark.parametrize(
    "argv",
    [
        ["--clear-after", "0", "example.com"],
        ["--clear-after", "-1", "example.com"],
        ["--clear-after", "nan", "example.com"],
        ["--clear-after", "soon", "example.com"],
        ["--print", "--no-clear", "example.com"],
        ["--print", "--clear-after", "5", "example.com"],
        ["--no-clear", "--clear-after", "5", "example.com"],
        ["example.com", "extra"],
    ],
)
def test_should_reject_invalid_arguments(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(argv)

    assert exit_info.value.code == 2
    assert "usage: pwdhash" in capsys.readouterr().err


def test_should_read_sys_argv_by_default(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
) -> None:
    monkeypatch.setattr("sys.argv", ["pwdhash", "--print", "example.com"])

    assert cli.main() == 0

    assert capsys.readouterr().out == f"{EXPECTED}\n"


def test_should_run_as_module(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    prompts: list[str],
) -> None:
    monkeypatch.setattr("sys.argv", ["pwdhash", "--print", "example.com"])

    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("pwdhash", run_name="__main__")

    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"{EXPECTED}\n"
