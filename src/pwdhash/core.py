"""Core PwdHash algorithm."""

import base64
import hashlib
import hmac
import itertools
import re
from collections.abc import Iterator

from .domains import extract_domain

PASSWORD_PREFIX = "@@"


def _b64_hmac_md5(key: str, data: str) -> str:
    """
    return base64-encoded HMAC-MD5 for key and data, with trailing "="
    stripped.
    """

    digest = hmac.HMAC(str2bytes(key), str2bytes(data), hashlib.md5).digest()
    return base64.b64encode(digest).decode("ascii").rstrip("=")


def str2bytes(string: str) -> bytes:
    """
    Returns string encoded to bytes, in way that every letter is represented
    by only first byte after encoding it with "UTF-16-LE" encoding.
    For ascii characters this means that its return is the same as
    str.encode(), but for other unicode strings (eg. Polish) this does its job.
    Example: str2bytes("ąśćóasco") --> b"\x05[\x07\xf3asco"
    """
    u16le = "utf-16-le"
    encoded = (letter.encode(u16le)[0] for letter in string)
    return bytes(encoded)


def generate(password: str, uri: str) -> str:
    """
    generate the pwdhash password for master password and uri or
    domain name.
    """
    realm = extract_domain(uri)
    password = password.removeprefix(PASSWORD_PREFIX)

    password_hash = _b64_hmac_md5(password, realm)
    size = len(password) + len(PASSWORD_PREFIX)
    is_non_alphanumeric = bool(re.search(r"[^a-zA-Z0-9_]", password))

    return _apply_constraints(password_hash, size, is_non_alphanumeric)


def _apply_constraints(password_hash: str, size: int, is_non_alphanumeric: bool) -> str:
    """
    Fiddle with the password a bit after hashing it so that it will
    get through most website filters. We require one upper and lower
    case, one digit, and we look at the user's password to determine
    if there should be at least one alphanumeric or not.
    """
    starting_size = 0 if size < 4 else size - 4
    result = password_hash[:starting_size]

    extras: Iterator[int] = itertools.chain(
        (ord(ch) for ch in password_hash[starting_size:]), itertools.repeat(0)
    )
    extra_chars = (chr(ch) for ch in extras)

    def next_between(start: str, end: str) -> str:
        interval = ord(end) - ord(start) + 1
        offset = next(extras) % interval
        return chr(ord(start) + offset)

    chars_ranges = (("A", "Z"), ("a", "z"), ("0", "9"))

    for first, last in chars_ranges:
        any_of_chars = re.compile(f"[{first}-{last}]")
        if any_of_chars.search(result):
            result += next(extra_chars)
        else:
            result += next_between(first, last)

    non_word = re.compile(r"\W")
    if non_word.search(result) and is_non_alphanumeric:
        result += next(extra_chars)
    else:
        result += "+"

    while non_word.search(result) and not is_non_alphanumeric:
        result = non_word.sub(next_between("A", "Z"), result, 1)

    flip_place = next(extras) % len(result)
    result = result[flip_place:] + result[:flip_place]

    return result.strip("\x00")
