#!/usr/bin/env python3
"""Thin argv shaper for the ``bond`` CLI (THE FRONT DOOR).

Bootstraps ``src/`` onto ``sys.path`` and delegates entirely to
:func:`bond_cli.dispatch.main`. The installed console script ``bond``
(``[project.scripts]``) is the identical entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_cli.dispatch import main

if __name__ == "__main__":
    raise SystemExit(main())
