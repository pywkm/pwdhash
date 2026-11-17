# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-17

### Breaking changes

- The distribution is renamed to `pwdhash-cli`; the import name (`pwdhash`)
  and the `pwdhash` command stay the same.
- Python 3.10 or newer is required.
- `pyperclip` is no longer a required dependency; install the `clipboard`
  extra (`pwdhash-cli[clipboard]`) to copy passwords to the clipboard.
  Without it the password is printed.
- `pwdhash.str2bytes` is no longer public.
- `console_main` is replaced by `pwdhash.cli.main(argv=None)`, which returns
  the exit code.
- An empty master password (also one that is just the `@@` prefix) is
  rejected by the command line tool instead of generating a password.

### Changed (generated passwords)

For ordinary input (a lower case domain or URL without a port) the passwords
are the same as before and as in `pwdhash.js`. They change only for:

- passwords containing characters outside the Basic Multilingual Plane
  (e.g. emoji): they are now processed as UTF-16 code units, like in
  `pwdhash.js`, so the results match the original, which they previously
  did not;
- domains and URLs that `extract_domain` now normalizes: it ignores the
  scheme (any scheme, in any case), user name and password, port, query,
  fragment and a trailing dot, and lowercases the result. For example
  `Example.com`, `HTTPS://example.com/x` and `example.com:8080` now all give
  the password of `example.com`. An IPv6 address is returned in brackets,
  without the port. This deliberately differs from `pwdhash.js`.

### Added

- New command line interface: `--version`, `-p/--print`,
  `--clear-after SECONDS` and `--no-clear`.
- The clipboard is cleared automatically after 20 seconds, but only if it
  still holds the generated password; Ctrl+C clears it at once.
- Messages go to stderr and the password printed with `--print` to stdout.
  Exit codes: 2 for invalid input, 1 on end of input, 130 on Ctrl+C.
- `python -m pwdhash`.
- `pwdhash.__version__`, a public `__all__` and type hints (`py.typed`).

### Fixed

- `extract_domain` raises `ValueError` with a clear message for input without
  a host name (e.g. empty or blank) instead of `AttributeError` or returning
  nonsense.

### Internal

- `src` layout package (`pwdhash.core`, `pwdhash.domains`, `pwdhash.cli`)
  built from `pyproject.toml` with uv; `setup.py`, `setup.cfg`, `tox.ini`
  and `MANIFEST.in` are removed.
- Tests use pytest, with golden vectors pinning the generated passwords.
  Linting with ruff, type checking with mypy in strict mode.
- GitHub Actions replace Travis CI (Python 3.10–3.14 on Linux, Windows and
  macOS), with Dependabot updates.

## [0.2.0] - 2026-11-17

- Python 3.9 or newer only; Python 2 compatibility code removed.
- Fixed a crash when the clipboard is not available.

[1.0.0]: https://github.com/pywkm/pwdhash/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/pywkm/pwdhash/releases/tag/v0.2.0
