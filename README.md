# pwdhash-cli

A command line tool and Python library implementing the
[Stanford PwdHash](https://pwdhash.github.io/website/) password generator [1].

PwdHash turns one master password into a different password for every site:
`HMAC-MD5(master password, domain)`, encoded and shaped so that typical
password rules (upper and lower case letters, a digit, optionally a special
character) are met. The passwords are the same as those of the original
PwdHash browser extension and its JavaScript implementation, `pwdhash.js`.

## Installation

Python 3.10 or newer is required. The package is not published on PyPI;
install it from the repository, preferably as an isolated tool:

```sh
uv tool install "pwdhash-cli[clipboard] @ git+https://github.com/pywkm/pwdhash"
# or
pipx install "pwdhash-cli[clipboard] @ git+https://github.com/pywkm/pwdhash"
# or, into the current environment
pip install "pwdhash-cli[clipboard] @ git+https://github.com/pywkm/pwdhash"
```

The `clipboard` extra installs [pyperclip](https://pypi.org/project/pyperclip/).
Without it the generated password is printed instead of copied. On Linux
pyperclip needs `xclip`, `xsel` or `wl-clipboard` installed.

The `pwdhash` command is also provided by other PwdHash implementations on
PyPI (see [below](#other-python-implementations)), so do not install them
into the same environment.

## Command line usage

```console
$ pwdhash example.com
Password for example.com:
Password for example.com copied to clipboard.
Clipboard will be cleared in 20 s (Ctrl+C to clear now).
Clipboard cleared.
```

The domain may also be a URL (`pwdhash https://www.example.com/login`) or
left out, in which case it is asked for. The master password is always read
from the terminal without echo.

```
usage: pwdhash [-h] [--version] [-p | --clear-after SECONDS | --no-clear]
               [domain]

positional arguments:
  domain                domain name or URL (asked for when omitted)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -p, --print           print the password to stdout instead of copying it
  --clear-after SECONDS
                        clear the clipboard after SECONDS, unless its content
                        has changed (default: 20)
  --no-clear            leave the password in the clipboard
```

- The clipboard is cleared only if it still holds the generated password.
  Ctrl+C while waiting clears it at once.
- Messages and prompts go to stderr; with `--print` (or when the clipboard is
  not available) stdout holds just the password, so it can be piped.
- Exit codes: 0 on success, 2 for invalid arguments, an invalid domain or an
  empty password, 1 on end of input, 130 on Ctrl+C at a prompt.

`python -m pwdhash` works the same as `pwdhash`.

## Library usage

```python
>>> import pwdhash
>>> pwdhash.generate("secret", "https://www.example.co.uk/login")
'VzjTjze7'
>>> pwdhash.extract_domain("https://www.example.co.uk/login")
'example.co.uk'
```

- `generate(password, uri)` returns the PwdHash password. `uri` is a domain
  name or a URL. A leading `@@` (`PASSWORD_PREFIX`), which the browser
  extension uses to mark PwdHash fields, is ignored.
- `extract_domain(uri)` returns the domain the password is generated for:
  the last two labels of the host name, or three for known second level
  suffixes such as `co.uk`.
- Both raise `ValueError` when no host name can be found in `uri`.

The package is fully typed (`py.typed`).

## Compatibility with the original

For ordinary input (a lower case domain or URL without a port, a password
of any characters) the generated passwords are the same as those of
`pwdhash.js`. Characters are processed as JavaScript does: as UTF-16 code
units, of which only the low byte is used, so non-ASCII and even emoji
passwords give the same results as in the browser.

Deliberate differences, which make some inputs give a different (and
consistent) password than the original:

- `extract_domain` ignores the scheme (any scheme, in any case), user name
  and password, port, query, fragment and a trailing dot, and lowercases the
  result. The original would, for example, give different passwords for
  `Example.com` and `example.com`.

Known limitations:

- The list of second level suffixes (`co.uk`, `com.pl`, ...) is the
  original's and is outdated compared with the
  [Public Suffix List](https://publicsuffix.org/). It is kept on purpose:
  changing it would change the passwords for the affected sites.
- For long passwords (24 characters or more) containing special
  characters, `pwdhash.js` may append NUL characters to the result; this
  implementation leaves them out.
- Only PwdHash (version 1) is implemented, not PwdHash2.

## Other Python implementations

- [`pwdhash.py`](https://pypi.org/project/pwdhash.py/)
  ([abbot/pwdhash](https://github.com/abbot/pwdhash)) is the project this
  one was forked from in 2015, when it was ported to Python 3. Since then
  both have been developed separately. As of its version 0.2.0, it encodes
  the master password as UTF-8, so passwords with non-ASCII characters
  (e.g. Polish letters) give different results than `pwdhash.js`, and its
  `extract_domain` has the original's issues with case, ports and
  non-HTTP schemes. It copies to the clipboard with `pbcopy` or `xclip`.
- [`pwdhash`](https://pypi.org/project/pwdhash/)
  ([EricDuminil/pwdhash-py](https://github.com/EricDuminil/pwdhash-py)) is an
  independent implementation that also supports PwdHash2 and reading the
  password from stdin. As of its version 0.2.0, it prints the password by
  default and may differ from `pwdhash.js` for passwords with characters
  outside ASCII.

## Development

The project uses [uv](https://docs.astral.sh/uv/):

```sh
uv run pytest              # tests with coverage
uv run ruff check          # lint
uv run ruff format         # format
uv run mypy                # type check (strict)
uv build                   # wheel and sdist into dist/
```

The tests include golden vectors that pin the generated passwords; they must
not change.

## License and credits

BSD 3-Clause, see [LICENSE](LICENSE). Originally based on pwdhash.py by
Lev Shamardin.

The algorithm and the original JavaScript code:

    Copyright (C) Stanford University 2004-2006
    Author: Collin Jackson
    Other Contributors: Dan Boneh, John Mitchell, Nick Miyake, and Blake Ross
    Distributed under the BSD License

[1] Ross, B., Jackson, C., Miyake, N., Boneh, D., & Mitchell, J. C. (2005,
August). Stronger Password Authentication Using Browser Extensions. In Usenix
security (pp. 17-32).
