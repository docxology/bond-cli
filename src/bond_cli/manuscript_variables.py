"""Manuscript variable hydration for bond-cli (THE FRONT DOOR).

Builds the ``{{TOKEN}}`` substitution map referenced by the manuscript prose.
Identity tokens (package name, codename) come from ``manuscript/config.yaml``;
fleet-derived tokens come from the built coordinator registry (the 27-film
roster) and the CLI's own deterministic command registry. Nothing here reads
wall-clock or runtime gate output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml

from .dispatch import CLI_CODENAME, COMMANDS, SUITE_NAME

#: Defaults used when ``manuscript/config.yaml`` is absent (tests, drafts).
_DEFAULT_IDENTITY = {
    "package_name": "bond-cli",
    "codename": CLI_CODENAME,
}


def read_identity(project_root: str | Path) -> dict[str, str]:
    """Read the manuscript identity from ``manuscript/config.yaml`` when present.

    Falls back to the package defaults (name + codename) when the config is
    absent, unreadable, or not a mapping.
    """
    config_path = Path(project_root) / "manuscript" / "config.yaml"
    if not config_path.is_file():
        return dict(_DEFAULT_IDENTITY)
    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):  # pragma: no cover - unreadable/malformed
        return dict(_DEFAULT_IDENTITY)
    if not isinstance(raw, dict):
        return dict(_DEFAULT_IDENTITY)
    package = raw.get("package")
    if not isinstance(package, dict):
        return dict(_DEFAULT_IDENTITY)
    return {
        "package_name": str(package.get("name") or _DEFAULT_IDENTITY["package_name"]),
        "codename": str(package.get("codename") or _DEFAULT_IDENTITY["codename"]),
    }


def _film_count() -> int:
    from bond_coordinator.registry import ROSTER

    return len(ROSTER)


def build_tokens(project_root: str | Path) -> dict[str, str]:
    """Return the full ``{{TOKEN}}`` → value map for the manuscript."""
    identity = read_identity(project_root)
    return {
        "SUITE_NAME": SUITE_NAME,
        "PACKAGE_NAME": identity["package_name"],
        "CODENAME": identity["codename"],
        "FILM_COUNT": str(_film_count()),
        "COMMANDS": ", ".join(COMMANDS),
    }


def generate_variables(
    project_root: str | Path,
    *,
    require_analysis_outputs: bool = False,
) -> dict[str, str]:
    """Generate and persist the token map to
    ``output/variables/manuscript_variables.json``.

    The front door has no analysis outputs, so ``require_analysis_outputs`` is
    accepted for pipeline parity but never gates.
    """
    del require_analysis_outputs  # identity/registry tokens need no analysis run
    tokens = build_tokens(project_root)
    out_dir = Path(project_root) / "output" / "variables"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manuscript_variables.json").write_text(
        json.dumps(tokens, indent=2, sort_keys=True), encoding="utf-8"
    )
    return tokens


def load_generated(project_root: str | Path) -> dict[str, str]:
    """Read back the generated token map from disk, or ``{}`` if absent."""
    path = Path(project_root) / "output" / "variables" / "manuscript_variables.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # pragma: no cover - corrupt file
        return {}
    payload = cast("dict[str, object]", data)
    return {
        str(k): str(v) for k, v in payload.items() if isinstance(v, (str, int, float))
    }
