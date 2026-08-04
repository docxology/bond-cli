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

#: Mission codename of this package.
CLI_CODENAME = "THE FRONT DOOR"

#: Human-readable suite name.
SUITE_NAME = "PROJECT BOND"

#: Default recon goal when ``bond recon <film>`` is given no explicit goal.
DEFAULT_RECON_GOAL = "general reconnaissance"

#: Suite root: the parent of every package dir, and the fleet workspace root.
BOND_ROOT = Path(__file__).resolve().parents[3]

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
    """``bond list`` — all 27 films from the coordinator registry."""
    del args
    from bond_coordinator.registry import ROSTER

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


def cmd_status(args: argparse.Namespace) -> int:
    """``bond status`` — coordinator suite-status snapshot."""
    del args
    from bond_coordinator.status import build_status

    status = build_status()  # fresh ledger: the honest pre-mission state
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


def register_film_gadgets(registry: Any, slug: str) -> int:
    """Import ``slug``'s mission module and register its gadgets (real discovery).

    Returns the number of gadgets newly registered; a film without a
    ``register_gadgets`` entry, or one that fails to import, contributes 0
    (bulk gadget discovery never crashes the CLI).
    """
    inserted = [entry for entry in _film_search_paths(slug) if entry not in sys.path]
    for entry in inserted:
        sys.path.insert(0, entry)
    try:
        try:
            module = importlib.import_module(f"{slug}.mission")
        except Exception:
            return 0
        register = getattr(module, "register_gadgets", None)
        if not callable(register):
            return 0
        before = len(registry.gadgets_for(slug))
        register(registry)
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

    sub.add_parser("list", help="list all 27 films from the registry")

    for verb in ("brief", "recon", "plan", "execute", "debrief"):
        p = sub.add_parser(verb, help=f"{verb} a film's protocol stage")
        p.add_argument("film")
        if verb == "recon":
            p.add_argument("goal", nargs="?", default=None)

    run = sub.add_parser("run", help="run a canned orchestrator mission")
    run.add_argument("mission")

    sub.add_parser("status", help="suite status snapshot")

    gadgets = sub.add_parser("gadgets", help="gadget registry lookup")
    gadgets.add_argument("film", nargs="?", default=None)

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
