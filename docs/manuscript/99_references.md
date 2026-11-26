# References

## In-suite packages (the {{LAYER_COUNT}} built layers this front door consumes)

- **bond-utilities — Q-BRANCH**: ciphers, codenames, clocks, deterministic randomness, mission IO (vendored copy, `vendor/bond-utilities`).
- **bond-api — THE PROTOCOL**: the frozen `MissionProvider` contract, discovery, and the `GadgetRegistry` (vendored copy, `vendor/bond-api`).
- **bond-coordinator — MISSION CONTROL**: the {{FILM_COUNT}}-film registry, mission ledger, and suite status (vendored copy, `vendor/bond-coordinator`).
- **bond-orchestrator — DAG 00**: the multi-package mission runner with checkpoint/resume and provenance, and the {{MISSION_COUNT}} canned missions (vendored copy, `vendor/bond-orchestrator`).

## External standards and sources

Cited from `references.bib`:

- Bethard, S. (2009). *PEP 389 — argparse: New Command Line Parsing Module*. Python Enhancement Proposal 389. [@bethard2009argparse]
- Python Software Foundation. *argparse — Parser for command-line options, arguments and sub-commands*. The Python Standard Library documentation. [@pythonargparse]
- Bray, T. (Ed.) (2017). *The JavaScript Object Notation (JSON) Data Interchange Format*. RFC 8259 / STD 90, IETF. doi:10.17487/RFC8259 [@rfc8259]
- IEEE and The Open Group (2018). *The Open Group Base Specifications Issue 7, 2018 edition (IEEE Std 1003.1-2017)*, Chapter 12: Utility Conventions. [@posix2018]
- Raymond, E. S. (2003). *The Art of Unix Programming*. Addison-Wesley. [@raymond2003unix]
- Preston-Werner, T. *Semantic Versioning 2.0.0*. [@semver2]
- Python Software Foundation. *inspect — Inspect live objects*. The Python Standard Library documentation. [@pythoninspect]
