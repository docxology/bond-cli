# Reproducibility

{{PACKAGE_NAME}} inherits the fleet's determinism guarantees and adds a few of its own:

- **Delegation, not duplication.** Every command calls a built layer; there is no second implementation to drift from the source of truth.
- **Frozen discovery.** Films are located through the FROZEN `bond_api` contract; output uses canonical ordering (roster order, sorted result keys).
- **Fixed seeds.** Film providers are deterministic; `bond run` reproduces an identical consolidated debrief for an unchanged fleet.
- **No wall-clock in persisted artifacts.** The CLI prints nothing time-based to files; the manuscript token map embeds no timestamps.
- **Tests as evidence.** The suite runs real subprocess invocations against the real packages and asserts byte-stable command output where the layers are deterministic.
