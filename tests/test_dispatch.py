"""In-process tests for bond_cli.dispatch — real delegation, zero mocks."""

from __future__ import annotations

import json

import pytest

from bond_cli import dispatch


def _run(capsys, argv):
    code = dispatch.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


# --------------------------------------------------------------------------- #
# list / status (registry + coordinator, no film imports)
# --------------------------------------------------------------------------- #


def test_list_returns_all_films(capsys):
    code, out, _ = _run(capsys, ["list"])
    assert code == 0
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 27
    assert any("goldfinger" in ln and "GRAND SLAM" in ln for ln in lines)
    assert lines[0].startswith(" 1")


def test_status_snapshot(capsys):
    code, out, _ = _run(capsys, ["status"])
    assert code == 0
    assert "suite status" in out
    assert "total films: 27" in out
    assert "coverage:" in out


def test_status_blocked(capsys, monkeypatch):
    """A RED package surfaces as blocked (real build_status over a custom roster)."""
    from dataclasses import replace

    import bond_coordinator.status as st
    from bond_coordinator.registry import get_package
    from bond_coordinator.types import PackageStatus

    red = replace(get_package("goldfinger"), status=PackageStatus.RED)
    real_build = st.build_status
    monkeypatch.setattr(st, "build_status", lambda **kw: real_build(roster=(red,)))
    code, out, _ = _run(capsys, ["status"])
    assert code == 0
    assert "blocked:" in out
    assert "goldfinger" in out


# --------------------------------------------------------------------------- #
# protocol lifecycle — reference film (sable, numpy-free)
# --------------------------------------------------------------------------- #


def test_brief_sable(capsys):
    code, out, _ = _run(capsys, ["brief", "sable"])
    assert code == 0
    assert "film: sable" in out
    assert "codename: THE PROTOCOL" in out
    assert "objectives:" in out


def test_recon_sable(capsys):
    code, out, _ = _run(capsys, ["recon", "sable"])
    assert code == 0
    assert out.strip()  # findings printed


def test_recon_sable_with_goal(capsys):
    code, out, _ = _run(capsys, ["recon", "sable", "prove the contract"])
    assert code == 0
    assert "prove the contract" in out


def test_plan_sable(capsys):
    code, out, _ = _run(capsys, ["plan", "sable"])
    assert code == 0
    assert "execute" in out


def test_execute_sable(capsys):
    code, out, _ = _run(capsys, ["execute", "sable"])
    assert code == 0
    assert "success: True" in out
    assert "provenance:" in out


def test_debrief_sable(capsys):
    code, out, _ = _run(capsys, ["debrief", "sable"])
    assert code == 0
    assert "success: True" in out
    assert "film: sable" in out


# --------------------------------------------------------------------------- #
# real fleet film path (NumPy-backed)
# --------------------------------------------------------------------------- #


def test_debrief_goldfinger(capsys):
    code, out, _ = _run(capsys, ["debrief", "goldfinger"])
    assert code == 0
    assert "film: goldfinger" in out
    assert "success: True" in out
    assert "GRAND SLAM" in out


def test_run_singlet(capsys):
    code, out, _ = _run(capsys, ["run", "OPERATION_SINGLET"])
    assert code == 0
    assert "consolidated debrief" in out
    assert "goldfinger" in out


def test_run_fallback_to_builtin(capsys, monkeypatch):
    """When a real film can't be bound, fall back to the orchestrator's built-in
    deterministic provider (real FilmProviderError, no mocks)."""
    import bond_orchestrator.film_providers as fp

    def _boom(*args, **kwargs):
        raise fp.FilmProviderError("film not built")

    monkeypatch.setattr(fp, "load_film_providers", _boom)
    code, out, _ = _run(capsys, ["run", "OPERATION_SINGLET"])
    assert code == 0
    assert "consolidated debrief" in out
    assert "goldfinger" in out


# --------------------------------------------------------------------------- #
# gadgets
# --------------------------------------------------------------------------- #


def test_gadgets_film_real(capsys):
    code, out, _ = _run(capsys, ["gadgets", "skyfall"])
    assert code == 0
    assert out.strip()  # skyfall registers gadgets


def test_gadgets_film_none(capsys):
    # sable (reference) registers no gadgets -> lookup fails, exit 1
    code, out, _ = _run(capsys, ["gadgets", "sable"])
    assert code == 1
    assert "no gadgets registered for film 'sable'" in out


def test_gadgets_all_films(capsys, monkeypatch):
    monkeypatch.setattr(dispatch, "GADGET_FILM_SLUGS", ("skyfall", "sable"))
    code, out, _ = _run(capsys, ["gadgets"])
    assert code == 0
    assert "skyfall" in out


def test_gadgets_empty_registry(capsys, monkeypatch):
    monkeypatch.setattr(dispatch, "GADGET_FILM_SLUGS", ("sable",))  # registers nothing
    code, out, _ = _run(capsys, ["gadgets"])
    assert code == 1
    assert "no film gadgets registered" in out


def test_default_gadget_slugs():
    slugs = dispatch._default_gadget_slugs()
    assert len(slugs) == 28  # 27 roster films + the reference film
    assert slugs[-1] == "sable"


def test_register_gadgets_no_module(tmp_path):
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    assert dispatch.register_film_gadgets(registry, "no_such_film_zzz") == 0
    assert registry.films() == ()


def test_register_gadgets_module_without_hook():
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    assert dispatch.register_film_gadgets(registry, "sable") == 0  # no hook
    assert registry.films() == ()


def test_register_gadgets_real():
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    added = dispatch.register_film_gadgets(registry, "skyfall")
    assert added > 0
    assert registry.gadgets_for("skyfall")


def test_register_gadgets_provider_bound_construction(capsys):
    """goldfinger binds gadgets in MissionProvider.__init__ (empty GADGETS at import).

    register_film_gadgets must construct the provider and then harvest the
    populated module-level registry — the deep reason the whole-fleet sweep
    works even for provider-bound films.
    """
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    added = dispatch.register_film_gadgets(registry, "goldfinger")
    assert added > 0
    names = registry.gadgets_for("goldfinger")
    assert "market_corner" in names

    # And the CLI surfaces them.
    code, out, _ = _run(capsys, ["gadgets", "goldfinger"])
    assert code == 0
    assert "market_corner" in out and "laser_threat" in out


def test_status_measured_from_gate_manifest(capsys, monkeypatch, tmp_path):
    """bond status reflects REAL measured fleet state when the gate manifest exists."""
    from bond_coordinator.registry import ROSTER

    manifest = tmp_path / "gate_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "packages": [
                    {
                        "package": r.slug,
                        "rc": 0,
                        "passed": 1,
                        "coverage": round(95 + (i % 5), 1),
                    }
                    for i, r in enumerate(ROSTER)
                ]
            }
        )
    )
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", manifest)

    code, out, _ = _run(capsys, ["status"])
    assert code == 0
    assert "ready: 27" in out
    assert "measured)" in out
    # Coverage is computed from the reconciled roster, never N/A now.
    assert "mean=" in out and "N/A" not in out


def test_status_falls_back_without_manifest(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["status"])
    assert code == 0
    assert "total films: 27" in out
    assert "scaffolded: 27" in out
    assert "mean=N/A" in out


def test_status_malformed_manifest_falls_back(capsys, monkeypatch, tmp_path):
    bad = tmp_path / "gate_manifest.json"
    bad.write_text("not json")
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", bad)
    code, out, _ = _run(capsys, ["status"])
    assert code == 0
    assert "total films: 27" in out


# --------------------------------------------------------------------------- #
# failure / exit-code paths
# --------------------------------------------------------------------------- #


def test_unknown_film_exit_1(capsys):
    code, _, err = _run(capsys, ["brief", "definitely_not_a_film"])
    assert code == 1
    assert "not available" in err


def test_unknown_mission_exit_2(capsys):
    code, _, err = _run(capsys, ["run", "OPERATION_NOT_REAL"])
    assert code == 2
    assert "unknown mission" in err


def test_unknown_subcommand():
    with pytest.raises(SystemExit) as exc:
        dispatch.main(["frobnicate"])
    assert exc.value.code == 2


def test_missing_film_argument():
    with pytest.raises(SystemExit) as exc:
        dispatch.main(["brief"])
    assert exc.value.code == 2


def test_fmt_value_json():
    assert dispatch._fmt_value({"a": 1}) == '{"a": 1}'
    assert dispatch._fmt_value(3) == "3"
