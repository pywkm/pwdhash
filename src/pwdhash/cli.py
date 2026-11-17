"""Command line interface."""

import getpass
import sys

import pyperclip

from .core import generate
from .domains import extract_domain


def main() -> None:
    uri = sys.argv[1] if len(sys.argv) > 1 else input("Domain: ").strip()

    domain = extract_domain(uri)
    password = getpass.getpass(f"Password for {domain}: ")
    generated = generate(password, domain)

    try:
        pyperclip.copy(generated)
        print("\nHashed password was copied to clipboard.")
    except pyperclip.PyperclipException as error:
        print(error)
        print(f"\nHashed password: {generated}")
