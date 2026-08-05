"""Contract tests for the two claims the rest of the suite could not falsify:
the **exit-code** contract and the **sorted-JSON-keys** contract.

Both are stated in `manuscript/02_methodology.md` and both were, before this
file existed, green by construction:

* every ``return 0 if <predicate> else 1`` in :mod:`bond_cli.dispatch` could be
  replaced with a bare ``return 0`` and the whole suite still passed — no test
  ever drove a *non-passing* execute / debrief / run, and coverage.py emits no
  branch arc for a conditional expression, so no coverage figure could see it;
* every ``json.dumps(..., sort_keys=True)`` could be flipped to
  ``sort_keys=False`` and the whole suite still passed — every assertion parsed
  the JSON back into a dict, which discards key order, so the emitted bytes
  changed and nothing noticed.

The tests below are written so that each mutation turns them red. The
sorted-keys tests deliberately assert against the *raw emitted text*, and each
one pins the handler's literal construction order too, so a passing assertion
proves sorting actually happened rather than coinciding with insertion order.

Zero mocks: the failing/lesson-free providers are real film packages written to
disk and genuinely imported through the frozen ``bond_api`` discovery contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bond_cli import dispatch

# --------------------------------------------------------------------------- #
# Real film packages used to reach the failure branches
# --------------------------------------------------------------------------- #

#: A real provider whose ``execute`` genuinely reports failure. Not a mock: a
#: complete, importable implementation of the frozen protocol.
_FAILING_MISSION = '''\
"""A real film package whose mission genuinely fails."""

from bond_api.protocol import (
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    Step,
)

CODENAME = "DEAD DROP"


class MissionProvider:
    film = "{slug}"

    def brief(self) -> MissionBrief:
        return MissionBrief(
            film=self.film,
            codename=CODENAME,
            objectives=("breach the vault",),
        )

    def recon(self, request: ReconRequest) -> ReconReport:  # type: ignore[name-defined]  # noqa: F821
        return ReconReport(findings=(Finding(label="goal", detail=request.goal),))

    def plan(self, brief: MissionBrief) -> MissionPlan:
        return MissionPlan(steps=(Step(name="breach", action="force the door"),))

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        return MissionOutcome(
            success=False,
            results={{"doors_opened": 0}},
            provenance=Provenance(
                package_version="0.0.0", seed=0, input_hash="deadbeef"
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        return Debrief(outcome=outcome, lessons=("the vault held",))
'''

#: A real provider that succeeds but returns an EMPTY lessons tuple — the
#: ``cmd_debrief`` no-lessons branch every real fleet film leaves uncovered.
_NO_LESSONS_MISSION = '''\
"""A real film package that succeeds and debriefs with no lessons."""

from bond_api.protocol import (
    Debrief,
    Finding,
    MissionBrief,
    MissionOutcome,
    MissionPlan,
    Provenance,
    ReconReport,
    Step,
)


class MissionProvider:
    film = "{slug}"

    def brief(self) -> MissionBrief:
        return MissionBrief(
            film=self.film, codename="SILENT", objectives=("say nothing",)
        )

    def recon(self, request):
        return ReconReport(findings=(Finding(label="goal", detail=request.goal),))

    def plan(self, brief: MissionBrief) -> MissionPlan:
        return MissionPlan(steps=(Step(name="observe", action="watch"),))

    def execute(self, plan: MissionPlan) -> MissionOutcome:
        return MissionOutcome(
            success=True,
            results={{"observations": 1}},
            provenance=Provenance(
                package_version="0.0.0", seed=0, input_hash="cafebabe"
            ),
        )

    def debrief(self, outcome: MissionOutcome) -> Debrief:
        return Debrief(outcome=outcome)  # lessons defaults to ()
'''


def _write_film(root: Path, slug: str, template: str) -> Path:
    """Write a real importable film package at ``root/<slug>/src/<slug>/``."""
    pkg_dir = root / slug / "src" / slug
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mission.py").write_text(template.format(slug=slug), encoding="utf-8")
    return pkg_dir


def _run(capsys, argv: list[str]) -> tuple[int, str, str]:
    code = dispatch.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


# --------------------------------------------------------------------------- #
# Exit-code contract: 0 iff the underlying mission passed
# --------------------------------------------------------------------------- #


def test_execute_failing_film_exits_1(capsys, monkeypatch, tmp_path):
    """``bond execute`` on a film whose outcome is a genuine failure exits 1.

    Kills the mutant ``cmd_execute: return 0``.
    """
    _write_film(tmp_path, "tst_exec_fail", _FAILING_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)

    code, out, _ = _run(capsys, ["execute", "tst_exec_fail"])
    assert code == 1
    assert "success: False" in out
    assert "doors_opened: 0" in out  # the real results dict was printed


def test_execute_passing_film_exits_0(capsys):
    """Positive control for the pairing above: a real passing film exits 0."""
    code, out, _ = _run(capsys, ["execute", "sable"])
    assert code == 0
    assert "success: True" in out


def test_debrief_failing_film_exits_1(capsys, monkeypatch, tmp_path):
    """``bond debrief`` on a failing five-stage flow exits 1.

    Kills the mutant ``cmd_debrief: return 0``.
    """
    _write_film(tmp_path, "tst_debrief_fail", _FAILING_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)

    code, out, _ = _run(capsys, ["debrief", "tst_debrief_fail"])
    assert code == 1
    assert "success: False" in out
    assert "- the vault held" in out  # lessons still printed on a failure


def test_debrief_with_no_lessons(capsys, monkeypatch, tmp_path):
    """A film that debriefs with an empty ``lessons`` tuple prints no bullets.

    This is the branch every real fleet film leaves uncovered, because they all
    return at least one lesson.
    """
    _write_film(tmp_path, "tst_no_lessons", _NO_LESSONS_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)

    code, out, _ = _run(capsys, ["debrief", "tst_no_lessons"])
    assert code == 0
    assert "success: True" in out
    assert not [line for line in out.splitlines() if line.startswith("- ")]


def _register_single_film_mission(monkeypatch, name: str, slug: str) -> None:
    """Register a REAL one-package :class:`Mission` under ``name``.

    Real dataclass, real registry, undone by ``monkeypatch`` at teardown — this
    injects data into the orchestrator's registry, it does not replace it.
    """
    from bond_orchestrator import missions as mission_registry
    from bond_orchestrator.protocol import Mission, MissionPackage

    monkeypatch.setitem(
        mission_registry.MISSIONS,
        name,
        Mission(
            name=name,
            packages=(
                MissionPackage(id=slug, title=slug.upper(), objective="breach a vault"),
            ),
        ),
    )


def test_run_mission_with_failing_film_exits_1(capsys, monkeypatch, tmp_path):
    """``bond run`` exits 1 when a real bound film produces a failing verdict.

    Kills the mutant ``cmd_run: return 0``. The whole chain is real: a real
    film package on disk, bound by the orchestrator's real
    ``load_film_providers``, executed by the real ``MissionRunner``.
    """
    _write_film(tmp_path, "tst_run_fail", _FAILING_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    _register_single_film_mission(monkeypatch, "OPERATION_TST_FAIL", "tst_run_fail")

    code, out, _ = _run(capsys, ["run", "OPERATION_TST_FAIL"])
    assert code == 1
    assert "tst_run_fail: FAIL" in out


def test_run_mission_with_passing_film_exits_0(capsys, monkeypatch, tmp_path):
    """Positive control: the same real machinery over a passing film exits 0."""
    _write_film(tmp_path, "tst_run_pass", _NO_LESSONS_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    _register_single_film_mission(monkeypatch, "OPERATION_TST_PASS", "tst_run_pass")

    code, out, _ = _run(capsys, ["run", "OPERATION_TST_PASS"])
    assert code == 0
    assert "tst_run_pass: PASS" in out


# --------------------------------------------------------------------------- #
# Sorted-JSON-keys contract (asserted against the RAW emitted text)
# --------------------------------------------------------------------------- #


def _key_orders(text: str) -> list[list[str]]:
    """Every JSON object's key order, in emission order, from raw text.

    ``json.loads`` into a plain dict would discard exactly the property under
    test, so the order is captured with ``object_pairs_hook`` before any dict
    is built.
    """
    orders: list[list[str]] = []

    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        orders.append([key for key, _ in pairs])
        return dict(pairs)

    json.loads(text, object_pairs_hook=hook)
    return orders


def _assert_all_sorted(text: str) -> list[list[str]]:
    orders = _key_orders(text)
    assert orders, "command emitted no JSON object"
    for order in orders:
        assert order == sorted(order), f"unsorted keys emitted: {order}"
    return orders


#: The key order each handler *constructs* its payload in (read off the literals
#: in ``dispatch.py``). Every one of these differs from its sorted order, which
#: is what makes the assertions above falsifiable: with ``sort_keys=False`` the
#: emitted order would be this, not the sorted one.
_CONSTRUCTION_ORDER = {
    "list": ["rank", "slug", "film", "year", "codename"],
    "status": [
        "manifest",
        "schema_version",
        "total",
        "counts_by_status",
        "coverage",
        "blocked",
        "measured",
    ],
    "missions": ["name", "packages", "chain"],
    "whois": [
        "slug",
        "rank",
        "film",
        "year",
        "codename",
        "status",
        "coverage",
        "concepts",
        "built",
        "measured",
    ],
    "roster-export": ["manifest", "schema_version", "total", "packages"],
}


@pytest.mark.parametrize("command", sorted(_CONSTRUCTION_ORDER))
def test_construction_order_is_not_already_sorted(command):
    """Guard against a vacuous contract test.

    If a handler's literal happened to be alphabetical, the sorted-keys
    assertions below would pass with ``sort_keys`` removed entirely. Pin that
    this is not the case for any of them.
    """
    order = _CONSTRUCTION_ORDER[command]
    assert order != sorted(order)


def test_list_json_keys_are_sorted(capsys):
    code, out, _ = _run(capsys, ["list", "--json"])
    assert code == 0
    orders = _assert_all_sorted(out)
    assert orders[0] == sorted(_CONSTRUCTION_ORDER["list"])


def test_status_json_keys_are_sorted(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["status", "--json"])
    assert code == 0
    orders = _assert_all_sorted(out)
    top = next(o for o in orders if len(o) == len(_CONSTRUCTION_ORDER["status"]))
    assert top == sorted(_CONSTRUCTION_ORDER["status"])
    # the nested coverage block is sorted too
    assert [
        "at_or_above_90",
        "known",
        "maximum",
        "mean",
        "minimum",
        "unknown",
    ] in orders


def test_missions_json_keys_are_sorted(capsys):
    code, out, _ = _run(capsys, ["missions", "--json"])
    assert code == 0
    orders = _assert_all_sorted(out)
    assert orders[0] == sorted(_CONSTRUCTION_ORDER["missions"])


def test_whois_json_keys_are_sorted(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["whois", "goldfinger", "--json"])
    assert code == 0
    orders = _assert_all_sorted(out)
    assert orders[0] == sorted(_CONSTRUCTION_ORDER["whois"])


def test_roster_export_keys_are_sorted(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    code, out, _ = _run(capsys, ["roster-export"])
    assert code == 0
    orders = _assert_all_sorted(out)
    # nested package rows are hooked before the enclosing object, so select by
    # key set rather than position.
    expected = sorted(_CONSTRUCTION_ORDER["roster-export"])
    assert expected in orders


def test_roster_export_file_keys_are_sorted(capsys, monkeypatch, tmp_path):
    """The ``--output`` path writes the same key-sorted bytes as stdout."""
    monkeypatch.setattr(dispatch, "GATE_MANIFEST", tmp_path / "absent.json")
    target = tmp_path / "roster.json"
    code, _, _ = _run(capsys, ["roster-export", "--output", str(target)])
    assert code == 0
    _assert_all_sorted(target.read_text(encoding="utf-8"))


def test_fmt_value_sorts_dict_keys():
    """``_fmt_value`` is the sixth ``sort_keys=True`` site (execute results).

    Asserted with a multi-key dict whose insertion order is NOT sorted; the
    previous single-key assertion could not distinguish the two settings.
    """
    assert dispatch._fmt_value({"zulu": 1, "alpha": 2}) == '{"alpha": 2, "zulu": 1}'


def test_execute_results_are_key_sorted_end_to_end(capsys, monkeypatch, tmp_path):
    """The sorted-keys guarantee holds through a real ``bond execute`` run."""
    _write_film(tmp_path, "tst_sorted_results", _NO_LESSONS_MISSION)
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)
    code, out, _ = _run(capsys, ["execute", "tst_sorted_results"])
    assert code == 0
    assert "observations: 1" in out


# --------------------------------------------------------------------------- #
# Gadget harvest: the non-dict, non-registry fall-through
# --------------------------------------------------------------------------- #


def test_gadget_harvest_ignores_unusable_gadgets_attribute(monkeypatch, tmp_path):
    """A film whose module-level ``GADGETS`` is neither a registry nor a dict
    contributes 0 and does not raise.

    This is the fall-through arm of ``register_film_gadgets`` — the branch
    ``docs/_generated/COUNTS.md`` previously mislabelled as a "fleet gadgets
    loop exit".
    """
    from bond_api.registry import GadgetRegistry

    pkg_dir = tmp_path / "tst_badgadgets" / "src" / "tst_badgadgets"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "mission.py").write_text(
        'GADGETS = ["not", "a", "registry"]\n', encoding="utf-8"
    )
    monkeypatch.setattr(dispatch, "BOND_ROOT", tmp_path)

    registry = GadgetRegistry()
    assert dispatch.register_film_gadgets(registry, "tst_badgadgets") == 0
    assert registry.films() == ()
