"""Phase-5 hardening tests — manifest-reconciliation edge cases, the manuscript
token contract, and the claim ledger.

Every case here pins a real file on disk (a real gate manifest, a real config,
a real importable film package) and drives the real dispatch entry point. Zero
mocks, no ambient fleet state: each test that touches the gate manifest points
``dispatch.GATE_MANIFEST`` at a tmp path, so the result never depends on
whether this workspace happens to carry a measured manifest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from conftest import PROJECT_ROOT

from bond_cli import dispatch
from bond_cli import manuscript_variables as mv


def _run(capsys, argv):
    code = dispatch.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


def _write_rows(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text(json.dumps({"packages": rows}), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# measured-coverage extraction (a measured 0.0 is a measurement, not "unknown")
# --------------------------------------------------------------------------- #


def test_measured_coverage_zero_is_a_real_measurement(capsys, monkeypatch, tmp_path):
    """A gate row reporting 0.0% must surface as 0.0, never as unknown.

    Regression: the reconciler used a truthiness test, which laundered a
    measured zero into ``None`` — an unmeasured-looking package that had in
    fact been measured at zero coverage.
    """
    manifest = _write_rows(
        tmp_path / "gate_manifest.json",
        [{"package": "dr_no", "rc": 1, "coverage": 0.0}],
    )
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["whois", "dr_no", "--json"])
    assert code == 0
    measured = json.loads(out)["measured"]
    assert measured["coverage"] == 0.0
    assert measured["status"] == "red"


def test_measured_coverage_non_numeric_is_unknown(capsys, monkeypatch, tmp_path):
    manifest = _write_rows(
        tmp_path / "gate_manifest.json",
        [{"package": "dr_no", "rc": 0, "coverage": "n/a"}],
    )
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["whois", "dr_no", "--json"])
    assert code == 0
    assert json.loads(out)["measured"]["coverage"] is None


def test_measured_coverage_rejects_bool():
    # JSON `true` is an int subclass in Python; it is not a coverage figure.
    assert dispatch._measured_coverage({"coverage": True}) is None
    assert dispatch._measured_coverage({}) is None
    assert dispatch._measured_coverage({"coverage": 91}) == 91.0


# --------------------------------------------------------------------------- #
# partial manifests: a film with no row keeps its registry record
# --------------------------------------------------------------------------- #


def test_partial_manifest_keeps_unmeasured_records(capsys, monkeypatch, tmp_path):
    manifest = _write_rows(
        tmp_path / "gate_manifest.json",
        [{"package": "dr_no", "rc": 0, "coverage": 93.5}],
    )
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["status", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["measured"] is True
    assert data["counts_by_status"]["ready"] == 1
    assert data["counts_by_status"]["scaffolded"] == data["total"] - 1
    assert data["coverage"]["known"] == 1
    assert data["coverage"]["mean"] == 93.5


def test_whois_unmeasured_film_under_partial_manifest(capsys, monkeypatch, tmp_path):
    manifest = _write_rows(
        tmp_path / "gate_manifest.json",
        [{"package": "dr_no", "rc": 0, "coverage": 93.5}],
    )
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    assert json.loads(out)["measured"] is None


def test_whois_malformed_manifest_reports_no_measurement(capsys, monkeypatch, tmp_path):
    bad = tmp_path / "gate_manifest.json"
    bad.write_text("{ not json", encoding="utf-8")
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", bad)
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    assert json.loads(out)["measured"] is None


def test_manifest_rows_without_package_key_fall_back(capsys, monkeypatch, tmp_path):
    manifest = _write_rows(tmp_path / "gate_manifest.json", [{"rc": 0}])
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["status", "--json"])
    assert code == 0
    assert json.loads(out)["measured"] is False


# --------------------------------------------------------------------------- #
# roster-export without a manifest (the plain-registry branch)
# --------------------------------------------------------------------------- #


def test_roster_export_unmeasured_uses_plain_registry(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["roster-export"])
    assert code == 0
    data = json.loads(out)
    from bond_coordinator.registry import ROSTER

    assert data["total"] == len(ROSTER)
    assert [row["slug"] for row in data["packages"]] == [r.slug for r in ROSTER]
    assert data["packages"][0]["status"] == ROSTER[0].status.value


# --------------------------------------------------------------------------- #
# gadget harvest: callable GADGETS factory on a provider-bound film
# --------------------------------------------------------------------------- #


def test_gadgets_callable_factory_on_provider_bound_film(monkeypatch, tmp_path):
    """A film that exposes BOTH a callable ``GADGETS`` factory and a
    ``MissionProvider`` class: the provider is constructed (shelf looks empty),
    the module attribute is re-read as the factory, and the factory is invoked
    a second time. This is the deepest branch of the tolerant harvest."""
    from bond_api.registry import GadgetRegistry

    pkg_dir = tmp_path / "tst_factprov" / "src" / "tst_factprov"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mission.py").write_text(
        "def _make() -> dict[str, str]:\n"
        '    return {"factprov": "factory + provider gadget"}\n'
        "GADGETS = _make\n"
        "class MissionProvider:\n"
        "    def __init__(self) -> None:\n"
        "        self.film = 'tst_factprov'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    registry = GadgetRegistry()
    assert dispatch.register_film_gadgets(registry, "tst_factprov") == 1
    assert registry.gadgets_for("tst_factprov") == ("factprov",)


def test_gadget_harvest_survives_a_broken_film(monkeypatch, tmp_path):
    """A film whose mission module raises on import contributes 0 and does not
    abort the sweep (the tolerance contract for whole-fleet ``bond gadgets``)."""
    from bond_api.registry import GadgetRegistry

    pkg_dir = tmp_path / "tst_broken" / "src" / "tst_broken"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mission.py").write_text(
        'raise RuntimeError("Q-branch fire")\n', encoding="utf-8"
    )
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    registry = GadgetRegistry()
    assert dispatch.register_film_gadgets(registry, "tst_broken") == 0
    assert registry.films() == ()


# --------------------------------------------------------------------------- #
# brief formatting: the optional asset/constraint sections
# --------------------------------------------------------------------------- #


def test_fmt_brief_omits_empty_optional_sections():
    """A real MissionBrief with no assets and no constraints prints neither
    heading (the sections are optional in the frozen protocol)."""
    from bond_api.protocol import MissionBrief

    text = dispatch._fmt_brief(
        MissionBrief(film="tst", codename="BARE", objectives=("hold the line",))
    )
    assert text.splitlines() == [
        "film: tst",
        "codename: BARE",
        "objectives:",
        "  - hold the line",
    ]


def test_fmt_brief_renders_assets_and_constraints():
    from bond_api.protocol import Asset, Constraint, MissionBrief

    text = dispatch._fmt_brief(
        MissionBrief(
            film="tst",
            codename="FULL",
            objectives=("hold the line",),
            assets=(Asset(kind="vehicle", name="DB5"),),
            constraints=(Constraint(kind="time", detail="48h window"),),
        )
    )
    assert "assets:" in text
    assert "  - vehicle: DB5" in text
    assert "constraints:" in text
    assert "  - time: 48h window" in text


# --------------------------------------------------------------------------- #
# manuscript token contract
# --------------------------------------------------------------------------- #


def test_tokens_bind_to_the_live_registries():
    """Every numeric token is derived, never stapled: assert each against the
    registry it claims to summarise."""
    from bond_coordinator.registry import ROSTER
    from bond_orchestrator.missions import MISSION_NAMES

    tokens = mv.build_tokens(PROJECT_ROOT)
    assert tokens["COMMAND_COUNT"] == str(len(dispatch.COMMANDS))
    assert tokens["COMMANDS"] == ", ".join(dispatch.COMMANDS)
    assert tokens["JSON_COMMAND_COUNT"] == str(len(dispatch.JSON_COMMANDS))
    assert tokens["LAYER_COUNT"] == str(len(dispatch.DEPENDENCY_LAYERS))
    assert tokens["FILM_COUNT"] == str(len(ROSTER))
    assert tokens["MISSION_COUNT"] == str(len(MISSION_NAMES))
    assert tokens["MISSION_NAMES"] == ", ".join(MISSION_NAMES)


#: argv (minus ``--json``) needed to reach each command's parser.
_ARGV_FOR = {
    "list": [],
    "status": [],
    "missions": [],
    "whois": ["goldfinger"],
    "brief": ["sable"],
    "recon": ["sable"],
    "plan": ["sable"],
    "execute": ["sable"],
    "debrief": ["sable"],
    "run": ["OPERATION_SINGLET"],
    "gadgets": [],
    "roster-export": [],
}


def test_json_commands_claim_is_enforced_by_the_parser():
    """``JSON_COMMANDS`` is a claim about the argv surface. Prove both halves:
    every listed command parses ``--json``, and every unlisted command rejects
    it with argparse's exit code 2."""
    parser = dispatch.build_parser()
    assert set(_ARGV_FOR) == set(dispatch.COMMANDS)  # the table covers the surface

    for command in dispatch.JSON_COMMANDS:
        args = parser.parse_args([command, *_ARGV_FOR[command], "--json"])
        assert args.json is True

    for command in dispatch.COMMANDS:
        if command in dispatch.JSON_COMMANDS:
            continue
        with pytest.raises(SystemExit) as exc:
            parser.parse_args([command, *_ARGV_FOR[command], "--json"])
        assert exc.value.code == 2


def test_paper_version_token_matches_config():
    config = yaml.safe_load(
        (PROJECT_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    )
    tokens = mv.build_tokens(PROJECT_ROOT)
    assert tokens["PACKAGE_VERSION"] == str(config["paper"]["version"])


def test_read_identity_non_mapping_package_block(tmp_path):
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "config.yaml").write_text("package: bond-cli\n", encoding="utf-8")
    assert mv.read_identity(tmp_path) == {
        "package_name": "bond-cli",
        "codename": "THE FRONT DOOR",
    }


def test_read_paper_version_fallbacks(tmp_path):
    from bond_cli import __version__

    assert mv.read_paper_version(tmp_path) == __version__  # no config at all

    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    config = manuscript / "config.yaml"

    config.write_text("- a list\n", encoding="utf-8")
    assert mv.read_paper_version(tmp_path) == __version__

    config.write_text("paper: not-a-mapping\n", encoding="utf-8")
    assert mv.read_paper_version(tmp_path) == __version__

    config.write_text("paper:\n  title: x\n", encoding="utf-8")
    assert mv.read_paper_version(tmp_path) == __version__

    config.write_text("paper:\n  version: 9.9.9\n", encoding="utf-8")
    assert mv.read_paper_version(tmp_path) == "9.9.9"


# --------------------------------------------------------------------------- #
# claim ledger: sourced numbers must match the sources they name
# --------------------------------------------------------------------------- #


def test_claim_ledger_matches_its_sources():
    """The ledger states numbers with a named source; re-derive each from that
    source so a ledger row cannot silently go stale."""
    from bond_coordinator.registry import ROSTER
    from bond_orchestrator.missions import MISSION_NAMES

    ledger = yaml.safe_load(
        (PROJECT_ROOT / "data" / "claim_ledger.yaml").read_text(encoding="utf-8")
    )
    claims = {row["id"]: row["value"] for row in ledger["claims"]}
    expected = {
        "film_count": len(ROSTER),
        "command_count": len(dispatch.COMMANDS),
        "json_command_count": len(dispatch.JSON_COMMANDS),
        "dependency_layers": len(dispatch.DEPENDENCY_LAYERS),
        "mission_count": len(MISSION_NAMES),
    }
    assert claims == expected


# --------------------------------------------------------------------------- #
# V3 — the layer contract is a gate, not just prose
# --------------------------------------------------------------------------- #


def _all_strings(node: object) -> list[str]:
    """Every string leaf in the layer-contract YAML tree, recursively."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        out: list[str] = []
        for value in node.values():
            out.extend(_all_strings(value))
        return out
    if isinstance(node, (list, tuple)):
        out = []
        for item in node:
            out.extend(_all_strings(item))
        return out
    return []


def _collect_python_sources() -> str:
    """All ``.py`` files under ``src/`` and ``scripts/``, concatenated.

    Used to make the manuscript's ``cross_cutting`` claims mechanically
    checkable: if an agent adds a forbidden import/pattern to those trees,
    the suite goes red instead of silently falsifying the contract.
    """
    chunks: list[str] = []
    for base in (PROJECT_ROOT / "src", PROJECT_ROOT / "scripts"):
        chunks.extend(
            path.read_text(encoding="utf-8") for path in sorted(base.rglob("*.py"))
        )
    return "\n".join(chunks)


def test_layer_contract_prohibited_imports_are_gated():
    """V3: three ``cross_cutting`` rules in ``manuscript/layer_contract.yaml``
    are checkable against the source trees.  If any is violated, this fails.

    - no ``infrastructure.*`` imports anywhere in ``src/`` or ``scripts/``;
    - no wall-clock reads (``import time`` / ``datetime`` / ``.now()``);
    - no terminal-width probing or environment reads.
    """
    contract = yaml.safe_load(
        (PROJECT_ROOT / "manuscript" / "layer_contract.yaml").read_text(
            encoding="utf-8"
        )
    )
    rules = "\n".join(_all_strings(contract))
    src = _collect_python_sources()

    # The contract must still *state* each rule (so deleting it from the YAML
    # fails the gate rather than making the assertion trivially pass).
    assert "infrastructure." in rules and "No infrastructure" in rules
    assert "wall-clock" in rules
    assert "terminal-width probing" in rules and "environment reads" in rules

    assert "infrastructure." not in src, (
        "infrastructure import leaked into src/scripts/"
    )
    assert not re.search(
        r"(^|\n)(import time|from datetime import|import datetime)", src
    )
    assert ".now()" not in src
    assert "getenv" not in src and "os.environ" not in src
    assert "get_terminal_size" not in src
