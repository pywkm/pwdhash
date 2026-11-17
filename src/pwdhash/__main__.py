"""Allow running the command line interface with ``python -m pwdhash``."""

import sys

from .cli import main

sys.exit(main())
