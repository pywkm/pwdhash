"""Python implementation of the Stanford PwdHash password generator."""

from importlib.metadata import version

from .core import PASSWORD_PREFIX, generate
from .domains import extract_domain

__version__ = version("pwdhash-cli")

__all__ = [
    "PASSWORD_PREFIX",
    "__version__",
    "extract_domain",
    "generate",
]
