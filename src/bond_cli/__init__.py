"""bond-cli — THE FRONT DOOR: the unified terminal CLI for PROJECT BOND.

Thin dispatch over the fleet's built layers. All business logic lives in the
sibling packages (bond-api protocol, bond-coordinator registry/status,
bond-orchestrator missions/runner, bond-utilities Q-branch); this package only
routes arguments, loads providers, formats output, and maps outcomes to exit
codes.
"""

from __future__ import annotations

from . import dispatch, manuscript_variables

__all__ = ["dispatch", "manuscript_variables"]

__version__ = "3.0.0"
