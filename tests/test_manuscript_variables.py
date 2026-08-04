"""Tests for src/bond_cli/manuscript_variables.py — token map + config hydration."""

from __future__ import annotations

import json
import re

from conftest import PROJECT_ROOT

from bond_cli import manuscript_variables as mv


def test_build_tokens_values():
    tokens = mv.build_tokens(PROJECT_ROOT)
    assert tokens["PACKAGE_NAME"] == "bond-cli"
    assert tokens["CODENAME"] == "THE FRONT DOOR"
    assert tokens["SUITE_NAME"] == "PROJECT BOND"
    assert tokens["FILM_COUNT"] == "27"
    assert "list" in tokens["COMMANDS"]
    assert "gadgets" in tokens["COMMANDS"]


def test_read_identity_default_when_absent(tmp_path):
    ident = mv.read_identity(tmp_path)
    assert ident["package_name"] == "bond-cli"
    assert ident["codename"] == "THE FRONT DOOR"


def test_read_identity_from_config(tmp_path):
    cfg = tmp_path / "manuscript"
    cfg.mkdir()
    (cfg / "config.yaml").write_text(
        "package:\n  name: foo\n  codename: BAR\n", encoding="utf-8"
    )
    assert mv.read_identity(tmp_path) == {"package_name": "foo", "codename": "BAR"}


def test_read_identity_non_dict(tmp_path):
    cfg = tmp_path / "manuscript"
    cfg.mkdir()
    (cfg / "config.yaml").write_text("- just\n- a list\n", encoding="utf-8")
    assert mv.read_identity(tmp_path)["package_name"] == "bond-cli"


def test_generate_variables_writes(tmp_path):
    tokens = mv.generate_variables(tmp_path)
    assert tokens["CODENAME"] == "THE FRONT DOOR"
    path = tmp_path / "output" / "variables" / "manuscript_variables.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["CODENAME"] == "THE FRONT DOOR"


def test_load_generated(tmp_path):
    assert mv.load_generated(tmp_path) == {}
    mv.generate_variables(tmp_path)
    assert mv.load_generated(tmp_path)["CODENAME"] == "THE FRONT DOOR"


def test_all_manuscript_tokens_generated():
    """Every {{TOKEN}} in the numbered prose sections resolves in build_tokens()."""
    tokens = mv.build_tokens(PROJECT_ROOT)
    assert tokens
    numbered = sorted(PROJECT_ROOT.glob("manuscript/[0-9]*.md"))
    assert numbered, "expected numbered manuscript sections"
    for md in numbered:
        text = md.read_text(encoding="utf-8")
        for token in re.findall(r"\{\{([A-Z_][A-Z0-9_]*)\}\}", text):
            assert token in tokens, f"{md.name}: unresolved {{{{{token}}}}}"
