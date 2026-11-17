import pyperclip
import pytest

import pwdhash

PASSWORD = "password12345"
EXPECTED = "0JMBoaKI7NFhObN"


@pytest.fixture
def fake_getpass(monkeypatch):
    prompts = []

    def getpass(prompt):
        prompts.append(prompt)
        return PASSWORD

    monkeypatch.setattr(pwdhash.getpass, "getpass", getpass)
    return prompts


@pytest.fixture
def clipboard(monkeypatch):
    copied = []
    monkeypatch.setattr(pwdhash.pyperclip, "copy", copied.append)
    return copied


def test_should_copy_hash_to_clipboard(monkeypatch, capsys, fake_getpass,
                                       clipboard):
    monkeypatch.setattr("sys.argv", ["pwdhash", "http://www.example.com/x"])

    pwdhash.console_main()

    assert clipboard == [EXPECTED]
    assert fake_getpass == ["Password for example.com: "]
    out = capsys.readouterr().out
    assert "copied to clipboard" in out
    assert EXPECTED not in out


def test_should_ask_for_domain_when_no_argument(monkeypatch, fake_getpass,
                                                clipboard):
    monkeypatch.setattr("sys.argv", ["pwdhash"])
    monkeypatch.setattr("builtins.input", lambda prompt: " example.com \n")

    pwdhash.console_main()

    assert clipboard == [EXPECTED]


def test_should_print_hash_when_clipboard_unavailable(monkeypatch, capsys,
                                                      fake_getpass):
    def broken_copy(_text):
        raise pyperclip.PyperclipException("no clipboard mechanism")

    monkeypatch.setattr("sys.argv", ["pwdhash", "example.com"])
    monkeypatch.setattr(pwdhash.pyperclip, "copy", broken_copy)

    pwdhash.console_main()

    out = capsys.readouterr().out
    assert "no clipboard mechanism" in out
    assert "Hashed password: {}".format(EXPECTED) in out
