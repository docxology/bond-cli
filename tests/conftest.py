"""Shared pytest helpers — zero mocks, real providers + real subprocess.

The front door is tested in-process (``bond_cli.dispatch.main``) against REAL
film providers (the light reference film ``sable`` for the protocol lifecycle,
a real fleet film for gadgets/missions where NumPy is required), plus a
subprocess smoke layer for the ``scripts/bond.py`` entry point.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
