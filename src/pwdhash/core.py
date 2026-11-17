"""Core PwdHash algorithm, ported from the original pwdhash.js."""

import base64
import hashlib
import hmac
import itertools
import re

from .domains import extract_domain

PASSWORD_PREFIX = "@@"

# JavaScript's \W without the "u" flag: ASCII only, unlike Python's str \W
_NON_WORD = re.compile(r"[^A-Za-z0-9_]")


def _utf16_units(string: str) -> bytes:
    """Return ``string`` as UTF-16-LE, i.e. two bytes per JavaScript char.

    Characters outside the BMP (e.g. emoji) take two UTF-16 code units,
    just like in JavaScript strings. Lone surrogates are passed through.
    """
    return string.encode("utf-16-le", "surrogatepass")


def str2bytes(string: str) -> bytes:
    """Return ``string`` as bytes the way pwdhash.js feeds it to HMAC-MD5.

    Every UTF-16 code unit is represented by its low byte
    (``charCodeAt(i) & 0xFF``). ASCII characters stay as they are, other BMP
    characters (e.g. Polish) give one byte each and characters outside the
    BMP (e.g. emoji) give two bytes.

    Example: ``str2bytes("ąśćóasco") == b"\\x05[\\x07\\xf3asco"``
    """
    return _utf16_units(string)[::2]


def _b64_hmac_md5(key: str, data: str) -> str:
    """Return the base64-encoded HMAC-MD5 of ``data``, without "=" padding."""
    digest = hmac.HMAC(str2bytes(key), str2bytes(data), hashlib.md5).digest()
    return base64.b64encode(digest).decode("ascii").rstrip("=")


def generate(password: str, uri: str) -> str:
    """Return the PwdHash password for ``password`` on the site ``uri``.

    ``uri`` may be a domain name or a URL; the realm is taken from it with
    `extract_domain`. An optional ``PASSWORD_PREFIX`` ("@@") at the start of
    ``password`` is ignored, as in the browser extension.

    Raises ValueError when no domain can be extracted from ``uri``.
    """
    realm = extract_domain(uri)
    password = password.removeprefix(PASSWORD_PREFIX)

    password_hash = _b64_hmac_md5(password, realm)
    # the length is counted in UTF-16 code units, like JavaScript's .length
    size = len(_utf16_units(password)) // 2 + len(PASSWORD_PREFIX)
    is_non_alphanumeric = _NON_WORD.search(password) is not None

    return _apply_constraints(password_hash, size, is_non_alphanumeric)


def _apply_constraints(password_hash: str, size: int, is_non_alphanumeric: bool) -> str:
    """Shape ``password_hash`` so that it passes typical password rules.

    The result has ``size`` characters (at least 4) and contains an upper
    case letter, a lower case letter and a digit. It contains a
    non-alphanumeric character exactly when the master password does.

    The first ``size - 4`` characters of the hash are kept and one character
    is appended for each rule: the next unused hash character if the rule is
    already met, otherwise a character derived from it. Finally the result
    is rotated by an amount taken from the hash. Mirrors ``applyConstraints``
    from pwdhash.js, so the output must stay exactly the same.
    """
    starting_size = max(size - 4, 0)
    result = password_hash[:starting_size]

    # character codes of the unused part of the hash, then zeros, like
    # nextExtra() in JavaScript
    extras = itertools.chain(
        map(ord, password_hash[starting_size:]), itertools.repeat(0)
    )

    def next_extra_char() -> str:
        return chr(next(extras))

    def next_between(first: str, last: str) -> str:
        interval = ord(last) - ord(first) + 1
        return chr(ord(first) + next(extras) % interval)

    for first, last in (("A", "Z"), ("a", "z"), ("0", "9")):
        if re.search(f"[{first}-{last}]", result):
            result += next_extra_char()
        else:
            result += next_between(first, last)

    if is_non_alphanumeric and _NON_WORD.search(result):
        result += next_extra_char()
    else:
        result += "+"

    if not is_non_alphanumeric:
        while _NON_WORD.search(result):
            result = _NON_WORD.sub(next_between("A", "Z"), result, count=1)

    rotation = next(extras) % len(result)
    result = result[rotation:] + result[:rotation]

    # pwdhash.js keeps the NUL characters used as padding once the hash runs
    # out; they are dropped here (a known, intentional difference)
    return result.strip("\x00")
