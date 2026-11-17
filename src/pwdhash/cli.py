"""Command line interface."""

import argparse
import getpass
import sys
import time

from . import __version__
from .core import PASSWORD_PREFIX, generate
from .domains import extract_domain

DEFAULT_CLEAR_AFTER = 20.0

EXIT_OK = 0
EXIT_EOF = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130


def _positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid number: {value!r}") from None
    if not seconds > 0:  # also rejects nan
        raise argparse.ArgumentTypeError(f"must be greater than 0: {value!r}")
    return seconds


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pwdhash",
        description=(
            "Generate a PwdHash password for a domain. The master password is"
            " read from the terminal and the result is copied to the"
            " clipboard."
        ),
    )
    parser.add_argument(
        "domain",
        nargs="?",
        help="domain name or URL (asked for when omitted)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="print the password to stdout instead of copying it",
    )
    output.add_argument(
        "--clear-after",
        type=_positive_seconds,
        default=DEFAULT_CLEAR_AFTER,
        metavar="SECONDS",
        help=(
            "clear the clipboard after SECONDS, unless its content has"
            " changed (default: %(default)g)"
        ),
    )
    output.add_argument(
        "--no-clear",
        action="store_true",
        help="leave the password in the clipboard",
    )
    return parser


def _say(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def _copy(password: str) -> bool:
    """Copy ``password`` to the clipboard; return False when not possible."""
    try:
        import pyperclip
    except ImportError:
        _say(
            "Clipboard support is not installed (pip install 'pwdhash-cli[clipboard]')."
        )
        return False
    try:
        pyperclip.copy(password)
    except pyperclip.PyperclipException as error:
        _say(f"Clipboard is not available: {error}")
        return False
    return True


def _clear(password: str) -> None:
    """Clear the clipboard if it still holds ``password``."""
    import pyperclip

    try:
        if pyperclip.paste() != password:
            _say("Clipboard content has changed, left untouched.")
            return
        pyperclip.copy("")
    except pyperclip.PyperclipException as error:
        _say(f"Could not clear the clipboard: {error}")
        return
    _say("Clipboard cleared.")


def _wait_and_clear(password: str, seconds: float) -> None:
    _say(f"Clipboard will be cleared in {seconds:g} s (Ctrl+C to clear now).")
    try:
        time.sleep(seconds)
    except KeyboardInterrupt:
        _say("")
    _clear(password)


def main(argv: list[str] | None = None) -> int:
    """Run the command line interface and return the exit code."""
    args = _build_parser().parse_args(argv)

    try:
        uri = args.domain
        if uri is None:
            # the prompt goes to stderr, so that stdout holds only the password
            print("Domain: ", end="", file=sys.stderr, flush=True)
            uri = input()
        domain = extract_domain(uri)
        password = getpass.getpass(f"Password for {domain}: ")
    except ValueError as error:
        _say(f"pwdhash: error: {error}")
        return EXIT_USAGE
    except KeyboardInterrupt:
        _say("")
        return EXIT_INTERRUPTED
    except EOFError:
        _say("")
        return EXIT_EOF

    if not password.removeprefix(PASSWORD_PREFIX):
        _say("pwdhash: error: the password must not be empty")
        return EXIT_USAGE

    generated = generate(password, domain)

    if args.print or not _copy(generated):
        print(generated)
        return EXIT_OK

    _say(f"Password for {domain} copied to clipboard.")
    if not args.no_clear:
        _wait_and_clear(generated, args.clear_after)
    return EXIT_OK
