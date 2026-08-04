"""Phase-4 deep-improvement tests: new commands, --json, color-safe tables,
and gadget-convention tolerance (real files + real imports, zero mocks)."""

from __future__ import annotations

import json
from pathlib import Path

from conftest import PROJECT_ROOT

from bond_cli import dispatch
from bond_cli.table import format_table


def _run(capsys, argv):
    code = dispatch.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


def _write_manifest(path: Path, *, rc: int = 0, coverage: float = 96.0) -> Path:
    """Write a real gate manifest at ``path`` covering every roster film."""
    from bond_coordinator.registry import ROSTER

    path.write_text(
        json.dumps(
            {
                "packages": [
                    {"package": r.slug, "rc": rc, "passed": 1, "coverage": coverage}
                    for r in ROSTER
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def _make_fake_film(root: Path, slug: str, mission_src: str) -> Path:
    """Write a real importable film package under ``root/<slug>/src/<slug>/``."""
    pkg_dir = root / slug / "src" / slug
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mission.py").write_text(mission_src, encoding="utf-8")
    return pkg_dir


# --------------------------------------------------------------------------- #
# missions
# --------------------------------------------------------------------------- #


def test_missions_human(capsys):
    code, out, _ = _run(capsys, ["missions"])
    assert code == 0
    assert "OPERATION_OMNIBUS" in out
    assert "goldfinger → goldeneye → no_time_to_die" in out
    assert "\x1b[" not in out  # color-safe: no ANSI codes


def test_missions_json(capsys):
    code, out, _ = _run(capsys, ["missions", "--json"])
    assert code == 0
    data = json.loads(out)
    assert len(data) == 3
    names = [row["name"] for row in data]
    assert names == sorted(names)
    omnibus = next(row for row in data if row["name"] == "OPERATION_OMNIBUS")
    assert omnibus["packages"] == ["goldfinger", "goldeneye", "no_time_to_die"]


# --------------------------------------------------------------------------- #
# whois
# --------------------------------------------------------------------------- #


def test_whois_human(capsys):
    code, out, _ = _run(capsys, ["whois", "goldfinger"])
    assert code == 0
    assert "goldfinger" in out
    assert "GRAND SLAM" in out
    assert "Goldfinger" in out
    assert "built" in out


def test_whois_json(capsys):
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["slug"] == "goldfinger"
    assert data["rank"] == 3
    assert data["year"] == 1964
    assert data["codename"] == "GRAND SLAM"
    assert isinstance(data["concepts"], list)
    assert data["built"] is True


def test_whois_reference_path_built(capsys, monkeypatch, tmp_path):
    # A roster film found under bond-api/films (reference layout) counts as built.
    films_dir = tmp_path / "bond-api" / "films" / "goldfinger"
    films_dir.mkdir(parents=True)
    (films_dir / "mission.py").write_text(
        "class MissionProvider:\n    pass\n", encoding="utf-8"
    )
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    assert json.loads(out)["built"] is True


def test_whois_reference_film_not_in_roster(capsys):
    # The bond-api reference film (sable) is not one of the 27 roster films.
    code, _, err = _run(capsys, ["whois", "sable"])
    assert code == 1
    assert "no registry record" in err


def test_whois_unknown_film(capsys):
    code, _, err = _run(capsys, ["whois", "not_a_film_zzz"])
    assert code == 1
    assert "no registry record" in err


def test_whois_not_built_flag(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path / "empty")
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    assert json.loads(out)["built"] is False


def test_whois_measured(capsys, monkeypatch, tmp_path):
    manifest = _write_manifest(tmp_path / "gate_manifest.json")
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    measured = json.loads(out)["measured"]
    assert measured is not None
    assert measured["status"] == "ready"
    assert measured["coverage"] == 96.0


# --------------------------------------------------------------------------- #
# roster-export
# --------------------------------------------------------------------------- #


def test_roster_export_stdout(capsys):
    code, out, _ = _run(capsys, ["roster-export"])
    assert code == 0
    data = json.loads(out)
    assert data["manifest"] == "bond-cli-roster-export"
    assert data["total"] == 27
    assert len(data["packages"]) == 27
    assert data["packages"][0]["slug"] == "dr_no"
    assert data["packages"][0]["rank"] == 1
    assert "concepts" in data["packages"][0]


def test_roster_export_to_file(tmp_path, capsys):
    target = tmp_path / "nested" / "roster.json"
    code, out, _ = _run(capsys, ["roster-export", "--output", str(target)])
    assert code == 0
    assert target.exists()
    assert str(target) in out
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["total"] == 27


def test_roster_export_measured(capsys, monkeypatch, tmp_path):
    manifest = _write_manifest(tmp_path / "gate_manifest.json", rc=0, coverage=97.5)
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["roster-export"])
    assert code == 0
    row = next(p for p in json.loads(out)["packages"] if p["slug"] == "dr_no")
    assert row["status"] == "ready"
    assert row["coverage"] == 97.5


# --------------------------------------------------------------------------- #
# list / status --json
# --------------------------------------------------------------------------- #


def test_list_json(capsys):
    code, out, _ = _run(capsys, ["list", "--json"])
    assert code == 0
    data = json.loads(out)
    assert len(data) == 27
    assert data[0]["slug"] == "dr_no"
    assert data[0]["year"] == 1962


def test_status_json(capsys, monkeypatch, tmp_path):
    # Pin the manifest away so this asserts the unmeasured (registry-only) branch;
    # a real fleet manifest may exist at the canonical path in this workspace.
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["status", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["manifest"] == "bond-cli-status"
    assert data["total"] == 27
    assert "scaffolded" in data["counts_by_status"]
    assert "generated_at" not in data  # no wall-clock in persisted artifacts
    assert data["measured"] is False


def test_status_json_measured(capsys, monkeypatch, tmp_path):
    manifest = _write_manifest(tmp_path / "gate_manifest.json", rc=0, coverage=98.0)
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)
    code, out, _ = _run(capsys, ["status", "--json"])
    assert code == 0
    data = json.loads(out)
    assert data["measured"] is True
    assert data["counts_by_status"]["ready"] == 27
    assert data["coverage"]["mean"] == 98.0


# --------------------------------------------------------------------------- #
# color-safe table helper
# --------------------------------------------------------------------------- #


def test_format_table_alignment():
    table = format_table(["A", "B"], [("1", "x"), ("longer", "y")])
    assert table == "A       B\n1       x\nlonger  y"


def test_format_table_no_ansi():
    assert "\x1b[" not in format_table(["H"], [("value",)])


def test_format_table_edge_cases():
    assert format_table(["A"], []) == "A"
    assert format_table([], [("x",)]) == ""


# --------------------------------------------------------------------------- #
# gadget convention tolerance (real tmp film packages)
# --------------------------------------------------------------------------- #


def _gadget_registry_for(monkeypatch, tmp_path, slug, mission_src):
    from bond_api.registry import GadgetRegistry

    _make_fake_film(tmp_path, slug, mission_src)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    registry = GadgetRegistry()
    added = dispatch.register_film_gadgets(registry, slug)
    return registry, added


def test_gadgets_zero_arg_hook(monkeypatch, tmp_path):
    registry, added = _gadget_registry_for(
        monkeypatch,
        tmp_path,
        "tst_zerohook",
        "GADGETS: dict[str, str] = {}\n"
        "def register_gadgets() -> None:\n"
        '    GADGETS["zerohook"] = "zero-arg hook gadget"\n',
    )
    assert added == 1
    assert registry.gadgets_for("tst_zerohook") == ("zerohook",)


def test_gadgets_plain_dict(monkeypatch, tmp_path):
    registry, added = _gadget_registry_for(
        monkeypatch,
        tmp_path,
        "tst_dictgad",
        'GADGETS = {"plain": "plain dict gadget"}\n',
    )
    assert added == 1
    assert registry.gadgets_for("tst_dictgad") == ("plain",)


def test_gadgets_callable_factory(monkeypatch, tmp_path):
    registry, added = _gadget_registry_for(
        monkeypatch,
        tmp_path,
        "tst_factory",
        "def _make() -> dict[str, str]:\n"
        '    return {"factory": "factory gadget"}\n'
        "GADGETS = _make\n",
    )
    assert added == 1
    assert registry.gadgets_for("tst_factory") == ("factory",)


def test_gadgets_bond_api_registry(monkeypatch, tmp_path):
    registry, added = _gadget_registry_for(
        monkeypatch,
        tmp_path,
        "tst_registry",
        "from bond_api.registry import GadgetRegistry\n"
        "GADGETS = GadgetRegistry()\n"
        'GADGETS.register("tst_registry", {"regreg": "registry gadget"})\n',
    )
    assert added == 1
    assert registry.gadgets_for("tst_registry") == ("regreg",)


# --------------------------------------------------------------------------- #
# manuscripts: COMMANDS token reflects the deepened surface
# --------------------------------------------------------------------------- #


def test_commands_token_includes_new_verbs():
    from bond_cli import manuscript_variables as mv

    tokens = mv.build_tokens(PROJECT_ROOT)
    for verb in ("missions", "whois", "roster-export"):
        assert verb in tokens["COMMANDS"]
