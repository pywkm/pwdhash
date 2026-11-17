import runpy

import pyperclip
import pytest

from pwdhash import cli

PASSWORD = "password12345"
EXPECTED = "0JMBoaKI7NFhObN"


@pytest.fixture
def fake_getpass(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    prompts: list[str] = []

    def getpass(prompt: str) -> str:
        prompts.append(prompt)
        return PASSWORD

    monkeypatch.setattr("getpass.getpass", getpass)
    return prompts


@pytest.fixture
def clipboard(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    copied: list[str] = []
    monkeypatch.setattr("pyperclip.copy", copied.append)
    return copied


def test_should_copy_hash_to_clipboard(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_getpass: list[str],
    clipboard: list[str],
) -> None:
    monkeypatch.setattr("sys.argv", ["pwdhash", "http://www.example.com/x"])

    cli.main()

    assert clipboard == [EXPECTED]
    assert fake_getpass == ["Password for example.com: "]
    out = capsys.readouterr().out
    assert "copied to clipboard" in out
    assert EXPECTED not in out


def test_should_ask_for_domain_when_no_argument(
    monkeypatch: pytest.MonkeyPatch, fake_getpass: list[str], clipboard: list[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["pwdhash"])
    monkeypatch.setattr("builtins.input", lambda prompt: " example.com \n")

    cli.main()

    assert clipboard == [EXPECTED]


def test_should_print_hash_when_clipboard_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    fake_getpass: list[str],
) -> None:
    def broken_copy(_text: str) -> None:
        raise pyperclip.PyperclipException("no clipboard mechanism")

    monkeypatch.setattr("sys.argv", ["pwdhash", "example.com"])
    monkeypatch.setattr("pyperclip.copy", broken_copy)

    cli.main()

    out = capsys.readouterr().out
    assert "no clipboard mechanism" in out
    assert f"Hashed password: {EXPECTED}" in out


def test_should_run_as_module(
    monkeypatch: pytest.MonkeyPatch, fake_getpass: list[str], clipboard: list[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["pwdhash", "example.com"])

    runpy.run_module("pwdhash", run_name="__main__")

    assert clipboard == [EXPECTED]
