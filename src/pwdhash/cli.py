"""Command line interface."""

import getpass
import sys

import pyperclip

from .core import generate
from .domains import extract_domain


def main():
    if len(sys.argv) > 1:
        uri = sys.argv[1]
    else:
        uri = input("Domain: ").strip()

    domain = extract_domain(uri)
    password = getpass.getpass(f"Password for {domain}: ")
    generated = generate(password, domain)

    try:
        pyperclip.copy(generated)
        print("\nHashed password was copied to clipboard.")
    except pyperclip.PyperclipException as error:
        print(error)
        print(f"\nHashed password: {generated}")
