"""bond-cli — THE FRONT DOOR: unified terminal CLI for the PROJECT BOND suite.

Thin dispatch over the fleet's built layers. All business logic lives in the
sibling packages; this module only routes arguments, loads providers with the
FROZEN bond-api contract, formats output, and maps outcomes to exit codes.

Commands (verb-first; the film/argument comes after the verb)::

    bond list                     all 27 films (coordinator registry)
    bond brief <film>             a film's MissionBrief
    bond recon <film> [goal]      a film's ReconReport
    bond plan <film>              a film's MissionPlan
    bond execute <film>           execute a film's plan -> MissionOutcome
    bond debrief <film>           full five-stage flow -> Debrief
    bond run <mission>            run a canned orchestrator mission
    bond status                   suite status snapshot (coordinator)
    bond gadgets [film]           gadget registry lookup (bond-api)
    bond missions                 canned orchestrator missions
    bond whois <film>             registry + measured identity of a film
    bond roster-export            fleet roster as JSON (--output writes a file)

``list``, ``status``, ``missions`` and ``whois`` accept ``--json`` for
machine-readable output; ``roster-export`` is JSON by construction. Human
tables are rendered color-safe by :mod:`bond_cli.table` (fixed-width
alignment, never ANSI).

Exit codes: ``0`` on success, ``1`` on a command failure (unknown film, a
non-passing execute/debrief, failed run), ``2`` on argparse misuse.

Determinism: film providers are fixed-seed/deterministic, output ordering is
canonical (roster order, sorted result keys), and no command writes wall-clock
data anywhere.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from .table import format_table

#: Mission codename of this package.
CLI_CODENAME = "THE FRONT DOOR"

#: Human-readable suite name.
SUITE_NAME = "PROJECT BOND"

#: Default recon goal when ``bond recon <film>`` is given no explicit goal.
DEFAULT_RECON_GOAL = "general reconnaissance"

#: Suite root: the parent of every package dir, and the fleet workspace root.
BOND_ROOT = Path(__file__).resolve().parents[3]

#: Aggregate gate manifest (written by the fleet gate runner): slug -> measured
#: gate result.  ``bond status`` reads this so the front door reflects REAL
#: measured fleet state (coverage + readiness), not a pre-mission ledger.
GATE_MANIFEST = BOND_ROOT / "output" / "aggregate" / "gate_manifest.json"

#: The ordered command registry (drives help + manuscript COMMANDS token).
COMMANDS: tuple[str, ...] = (
    "list",
    "brief",
    "recon",
    "plan",
    "execute",
    "debrief",
    "run",
    "status",
    "gadgets",
    "missions",
    "whois",
    "roster-export",
)


class CliError(Exception):
    """A command-level failure the CLI turns into exit code 1."""


# --------------------------------------------------------------------------- #
# Film discovery
# --------------------------------------------------------------------------- #


def _film_search_paths(slug: str) -> list[str]:
    """Existing search paths for a film provider: the fleet dir, then bond-api's
    films. ``bond_api`` validates that every provided path is a directory, so
    missing candidates (e.g. ``sable`` living only under ``bond-api/films``)
    are filtered out here."""
    return [
        str(path)
        for path in (
            BOND_ROOT / slug / "src",
            BOND_ROOT / "bond-api" / "films",
        )
        if path.is_dir()
    ]


def load_film(slug: str) -> Any:
    """Load a film's :class:`~bond_api.protocol.MissionProvider` (real).

    Uses the FROZEN bond-api discovery contract; raises :class:`CliError`
    (exit 1) when the film is missing or malformed.
    """
    from bond_api.discovery import DiscoveryError, load_provider

    try:
        return load_provider(slug, search_paths=_film_search_paths(slug))
    except DiscoveryError as exc:
        raise CliError(f"film {slug!r} is not available: {exc}") from exc


# --------------------------------------------------------------------------- #
# Output formatting (deterministic)
# --------------------------------------------------------------------------- #


def _fmt_brief(brief: Any) -> str:
    lines = [f"film: {brief.film}", f"codename: {brief.codename}", "objectives:"]
    lines.extend(f"  - {obj}" for obj in brief.objectives)
    if brief.assets:
        lines.append("assets:")
        lines.extend(f"  - {asset.kind}: {asset.name}" for asset in brief.assets)
    if brief.constraints:
        lines.append("constraints:")
        lines.extend(f"  - {c.kind}: {c.detail}".rstrip(":") for c in brief.constraints)
    return "\n".join(lines)


def _fmt_value(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)


# --------------------------------------------------------------------------- #
# Command handlers (uniform ``(args) -> int`` signature)
# --------------------------------------------------------------------------- #


def cmd_list(args: argparse.Namespace) -> int:
    """``bond list [--json]`` — all 27 films from the coordinator registry."""
    from bond_coordinator.registry import ROSTER

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "rank": rec.rank,
                        "slug": rec.slug,
                        "film": rec.film,
                        "year": rec.year,
                        "codename": rec.codename,
                    }
                    for rec in ROSTER
                ],
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    for rec in ROSTER:
        print(f"{rec.rank:>2}  {rec.slug:<28} {rec.film} ({rec.year})  {rec.codename}")
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    """``bond brief <film>`` — print a film's MissionBrief."""
    provider = load_film(args.film)
    print(_fmt_brief(provider.brief()))
    return 0


def cmd_recon(args: argparse.Namespace) -> int:
    """``bond recon <film> [goal]`` — print a film's ReconReport findings."""
    from bond_api.protocol import ReconRequest

    provider = load_film(args.film)
    report = provider.recon(ReconRequest(goal=args.goal or DEFAULT_RECON_GOAL))
    for finding in report.findings:
        print(f"- {finding.label}: {finding.detail}".rstrip(":"))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """``bond plan <film>`` — print a film's MissionPlan steps."""
    provider = load_film(args.film)
    plan = provider.plan(provider.brief())
    for step in plan.steps:
        print(f"- {step.name} [{step.action}]")
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    """``bond execute <film>`` — execute a film's plan and print the outcome."""
    provider = load_film(args.film)
    outcome = provider.execute(provider.plan(provider.brief()))
    print(f"success: {outcome.success}")
    for key in sorted(outcome.results):
        print(f"  {key}: {_fmt_value(outcome.results[key])}")
    provenance = outcome.provenance
    print(
        f"provenance: package={provenance.package_version} seed={provenance.seed} "
        f"input_hash={provenance.input_hash}"
    )
    return 0 if outcome.success else 1


def cmd_debrief(args: argparse.Namespace) -> int:
    """``bond debrief <film>`` — run the full five-stage flow, print the debrief."""
    from bond_api.protocol import ReconRequest, run_mission

    provider = load_film(args.film)
    debrief = run_mission(provider, ReconRequest(goal=DEFAULT_RECON_GOAL))
    outcome = debrief.outcome
    print(f"film: {provider.film}")
    print(f"brief codename: {provider.brief().codename}")
    print(f"success: {outcome.success}")
    if debrief.lessons:
        for lesson in debrief.lessons:
            print(f"- {lesson}")
    return 0 if outcome.success else 1


def cmd_run(args: argparse.Namespace) -> int:
    """``bond run <mission>`` — execute a canned orchestrator mission end-to-end.

    Uses the real film providers when a film package is built on disk; falls
    back to the orchestrator's built-in deterministic provider otherwise.
    """
    from bond_orchestrator.missions import UnknownMissionError, get_mission
    from bond_orchestrator.runner import MissionRunner

    try:
        mission = get_mission(args.mission)
    except UnknownMissionError as exc:
        print(f"bond: {exc}", file=sys.stderr)
        return 2

    providers: dict[str, Any] = {
        package_id: _resolve_provider(package_id)
        for package_id in mission.package_ids()
    }

    report = MissionRunner(providers).run(mission)
    print(report.consolidated_debrief())
    return 0 if report.all_verdicts_pass() else 1


def _resolve_provider(package_id: str) -> Any:
    """Bind ``package_id`` to its real film adapter, or the orchestrator's
    built-in deterministic provider when the film is not built on disk."""
    from bond_orchestrator.film_providers import FilmProviderError, load_film_providers
    from bond_orchestrator.providers import get_provider

    try:
        adapters = load_film_providers((package_id,), BOND_ROOT)
        return adapters[package_id]
    except FilmProviderError:
        return get_provider(package_id)


def _measured_roster() -> tuple[Any, ...] | None:
    """Return the roster reconciled against the aggregate gate manifest.

    Each film with a measured gate row gets its REAL status (``ready`` when the
    gate passed, ``red`` when it failed) and its measured coverage %.  Returns
    ``None`` when the manifest is absent (fresh/unknown fleet state).
    """
    if not GATE_MANIFEST.is_file():
        return None
    from dataclasses import replace

    from bond_coordinator.registry import ROSTER
    from bond_coordinator.types import PackageStatus

    try:
        manifest = json.loads(GATE_MANIFEST.read_text())
        rows = {p["package"]: p for p in manifest.get("packages", [])}
    except (OSError, ValueError, KeyError):
        return None

    reconciled: list[Any] = []
    for record in ROSTER:
        row = rows.get(record.slug)
        if row is None:
            reconciled.append(record)
            continue
        status = PackageStatus.READY if row.get("rc") == 0 else PackageStatus.RED
        coverage: float | None = row.get("coverage")
        reconciled.append(
            replace(record, status=status, coverage=coverage if coverage else None)
        )
    return tuple(reconciled)


def cmd_status(args: argparse.Namespace) -> int:
    """``bond status [--json]`` — suite-status snapshot (measured when known)."""
    from bond_coordinator.status import build_status

    roster = _measured_roster()
    status = build_status(roster=roster) if roster is not None else build_status()
    if args.json:
        print(
            json.dumps(
                {
                    "manifest": "bond-cli-status",
                    "schema_version": 1,
                    "total": status.total,
                    "counts_by_status": {
                        state.value: count
                        for state, count in status.counts_by_status.items()
                    },
                    "coverage": {
                        "known": status.coverage.known,
                        "unknown": status.coverage.unknown,
                        "mean": status.coverage.mean,
                        "minimum": status.coverage.minimum,
                        "maximum": status.coverage.maximum,
                        "at_or_above_90": status.coverage.at_or_above_floor,
                    },
                    "blocked": [
                        {"slug": blocked.slug, "reason": blocked.reason}
                        for blocked in status.blocked_packages
                    ],
                    "measured": roster is not None,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    print(f"{SUITE_NAME} suite status ({CLI_CODENAME})")
    print(f"total films: {status.total}")
    for state, count in status.counts_by_status.items():
        print(f"  {state.value}: {count}")
    coverage = status.coverage
    mean = f"{coverage.mean:.1f}%" if coverage.mean is not None else "N/A"
    print(
        f"coverage: mean={mean} min={coverage.minimum}% max={coverage.maximum}% "
        f"at_or_above_90={coverage.at_or_above_floor} ({coverage.known} measured)"
    )
    if status.blocked_packages:
        print("blocked:")
        for blocked in status.blocked_packages:
            print(f"  - {blocked.slug}: {blocked.reason}")
    return 0


def cmd_missions(args: argparse.Namespace) -> int:
    """``bond missions [--json]`` — the orchestrator's canned missions."""
    from bond_orchestrator.missions import MISSION_NAMES, MISSIONS

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "name": name,
                        "packages": list(MISSIONS[name].package_ids()),
                        "chain": " → ".join(MISSIONS[name].package_ids()),
                    }
                    for name in MISSION_NAMES
                ],
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    print(
        format_table(
            ["MISSION", "PACKAGES"],
            [
                [name, " → ".join(MISSIONS[name].package_ids())]
                for name in MISSION_NAMES
            ],
        )
    )
    return 0


def _film_built(slug: str) -> bool:
    """Whether the film's provider module exists on disk (fleet or reference)."""
    return (BOND_ROOT / slug / "src" / slug / "mission.py").is_file() or (
        BOND_ROOT / "bond-api" / "films" / slug / "mission.py"
    ).is_file()


def cmd_whois(args: argparse.Namespace) -> int:
    """``bond whois <film> [--json]`` — registry + measured identity of a film."""
    from bond_coordinator.registry import get_package

    try:
        record = get_package(args.film)
    except KeyError as exc:
        raise CliError(f"no registry record for film {args.film!r}: {exc}") from exc

    measured: dict[str, Any] | None = None
    roster = _measured_roster()
    if roster is not None:
        for candidate in roster:
            if candidate.slug == args.film:
                measured = {
                    "status": candidate.status.value,
                    "coverage": candidate.coverage,
                }
                break

    payload = {
        "slug": record.slug,
        "rank": record.rank,
        "film": record.film,
        "year": record.year,
        "codename": record.codename,
        "status": record.status.value,
        "coverage": record.coverage,
        "concepts": list(record.concepts),
        "built": _film_built(record.slug),
        "measured": measured,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(
        format_table(
            ["FIELD", "VALUE"], [[key, value] for key, value in payload.items()]
        )
    )
    return 0


def _roster_payload(roster: tuple[Any, ...]) -> list[dict[str, Any]]:
    """JSON-safe roster rows (used by ``roster-export``)."""
    return [
        {
            "rank": record.rank,
            "slug": record.slug,
            "film": record.film,
            "year": record.year,
            "codename": record.codename,
            "status": record.status.value,
            "coverage": record.coverage,
            "concepts": list(record.concepts),
        }
        for record in roster
    ]


def cmd_roster_export(args: argparse.Namespace) -> int:
    """``bond roster-export [--output PATH]`` — the fleet roster as JSON.

    Exports the reconciled roster (measured status/coverage from the gate
    manifest) when the manifest exists, else the plain registry. JSON is
    key-sorted and deterministic.
    """
    roster = _measured_roster()
    if roster is None:
        from bond_coordinator.registry import ROSTER

        roster = ROSTER
    payload = json.dumps(
        {
            "manifest": "bond-cli-roster-export",
            "schema_version": 1,
            "total": len(roster),
            "packages": _roster_payload(roster),
        },
        indent=2,
        sort_keys=True,
    )
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
        print(target)
        return 0
    print(payload)
    return 0


def register_film_gadgets(registry: Any, slug: str) -> int:
    """Import ``slug``'s mission module and register its gadgets (real discovery).

    Tolerates every fleet convention: a ``register_gadgets(registry)`` hook or
    a zero-arg ``register_gadgets()`` hook, a module-level ``GADGETS`` registry
    (bond-api GadgetRegistry / plain dict / callable factory), and gadgets
    bound only when ``MissionProvider()`` is constructed.  A film with nothing
    to offer, or one that fails to import, contributes 0 (bulk gadget
    discovery never crashes the CLI).

    Returns the number of gadgets newly registered.
    """
    inserted = [entry for entry in _film_search_paths(slug) if entry not in sys.path]
    for entry in inserted:
        sys.path.insert(0, entry)
    try:
        try:
            module = importlib.import_module(f"{slug}.mission")
        except Exception:
            return 0
        before = len(registry.gadgets_for(slug))

        # 1) the register_gadgets hook exists in either arity.
        register = getattr(module, "register_gadgets", None)
        if callable(register):
            try:
                register(registry)
            except TypeError:
                register()  # zero-arg hook: populates module-level GADGETS

        # 2) merge the module-level GADGETS source regardless of hook style.
        gadgets = getattr(module, "GADGETS", None)
        provider_cls = getattr(module, "MissionProvider", None)
        if callable(gadgets) and not hasattr(gadgets, "items"):
            gadgets = gadgets()  # callable factory returning the registry
        shelf_empty = (
            not (hasattr(gadgets, "gadgets_for") and gadgets.gadgets_for(slug))
            if gadgets is not None
            else True
        )
        if shelf_empty and isinstance(provider_cls, type):
            provider_cls()  # provider-bound convention registers at construction
            gadgets = getattr(module, "GADGETS", None) or gadgets
        if gadgets is not None:
            if callable(gadgets) and not hasattr(gadgets, "items"):
                gadgets = gadgets()  # callable factory returning the registry
            if hasattr(gadgets, "gadgets_for") and hasattr(gadgets, "lookup"):
                registry.register(
                    slug,
                    {
                        name: gadgets.lookup(slug, name)
                        for name in gadgets.gadgets_for(slug)
                    },
                )
            elif isinstance(gadgets, dict):
                registry.register(slug, gadgets)
        return len(registry.gadgets_for(slug)) - before
    finally:
        for entry in inserted:
            sys.path.remove(entry)  # we inserted each; guaranteed present


#: Films scanned by ``bond gadgets`` with no argument (default: the whole roster
#: plus the reference film). Overridable for fast/deterministic tests.
GADGET_FILM_SLUGS: tuple[str, ...] = ()


def _default_gadget_slugs() -> tuple[str, ...]:
    from bond_coordinator.registry import ROSTER

    return (*tuple(rec.slug for rec in ROSTER), "sable")


def cmd_gadgets(args: argparse.Namespace) -> int:
    """``bond gadgets [film]`` — GadgetRegistry lookup."""
    from bond_api.registry import GadgetRegistry

    registry = GadgetRegistry()
    slugs = (
        (args.film,) if args.film else (GADGET_FILM_SLUGS or _default_gadget_slugs())
    )
    for slug in slugs:
        register_film_gadgets(registry, slug)

    if args.film:
        names = registry.gadgets_for(args.film)
        if not names:
            print(f"no gadgets registered for film {args.film!r}")
            return 1
        for name in names:
            print(name)
        return 0

    if not registry.films():
        print("no film gadgets registered in the fleet")
        return 1
    for film in registry.films():
        names = registry.gadgets_for(film)
        print(f"{film:<28} {', '.join(names)}")
    return 0


# --------------------------------------------------------------------------- #
# arg-parsing + dispatch
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    """Build the argv surface (thin: argument shaping only)."""
    parser = argparse.ArgumentParser(
        prog="bond",
        description=f"{SUITE_NAME} front door ({CLI_CODENAME}) — film "
        "brief/recon/plan/execute/debrief, orchestrator missions, suite status, gadgets.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="list all 27 films from the registry")
    list_parser.add_argument("--json", action="store_true", help="emit JSON rows")

    for verb in ("brief", "recon", "plan", "execute", "debrief"):
        p = sub.add_parser(verb, help=f"{verb} a film's protocol stage")
        p.add_argument("film")
        if verb == "recon":
            p.add_argument("goal", nargs="?", default=None)

    run = sub.add_parser("run", help="run a canned orchestrator mission")
    run.add_argument("mission")

    status_parser = sub.add_parser("status", help="suite status snapshot")
    status_parser.add_argument("--json", action="store_true", help="emit JSON snapshot")

    gadgets = sub.add_parser("gadgets", help="gadget registry lookup")
    gadgets.add_argument("film", nargs="?", default=None)

    missions = sub.add_parser("missions", help="list canned orchestrator missions")
    missions.add_argument("--json", action="store_true", help="emit JSON rows")

    whois = sub.add_parser("whois", help="registry + measured identity of a film")
    whois.add_argument("film")
    whois.add_argument("--json", action="store_true", help="emit JSON payload")

    export = sub.add_parser("roster-export", help="fleet roster as JSON")
    export.add_argument(
        "--output", default=None, help="write JSON to PATH instead of stdout"
    )

    return parser


def _handlers() -> dict[str, Callable[[argparse.Namespace], int]]:
    return {
        "list": cmd_list,
        "brief": cmd_brief,
        "recon": cmd_recon,
        "plan": cmd_plan,
        "execute": cmd_execute,
        "debrief": cmd_debrief,
        "run": cmd_run,
        "status": cmd_status,
        "gadgets": cmd_gadgets,
        "missions": cmd_missions,
        "whois": cmd_whois,
        "roster-export": cmd_roster_export,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point (console script ``bond`` + ``scripts/bond.py``)."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _handlers()[args.command](args)
    except CliError as exc:
        print(f"bond: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
