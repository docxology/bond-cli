#!/usr/bin/env python3
"""Thin orchestrator: generate the manuscript ``{{TOKEN}}`` map and persist it.

Delegates to :func:`bond_cli.manuscript_variables.generate_variables`, which
reads identity tokens from ``manuscript/config.yaml`` and fleet tokens from the
built coordinator registry, then writes
``output/variables/manuscript_variables.json`` (sorted keys, deterministic).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_cli import manuscript_variables as mv


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    tokens = mv.generate_variables(project_root)
    out_path = project_root / "output" / "variables" / "manuscript_variables.json"
    print(f"wrote {out_path}")
    print(json.dumps(tokens, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
