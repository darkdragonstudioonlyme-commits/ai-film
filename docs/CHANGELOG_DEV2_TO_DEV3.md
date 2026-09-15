# Changelog dev2 → dev3

Parent: exact implementation V2 ZIP, SHA-256 `6affa22508c02db4a3c6fda404ab17575494c9dbdc93dda2eb896e79f92a29c1`.

Source comparison is in `source_diff.patch` and `evidence/SOURCE_CHANGE_INVENTORY.json`; unchanged contracts and native test inventory retain their original bytes.

## Added

Per-step SessionRunner, concrete native factory/driver, actual observation/proof/system-state adapters, narrow generated-identity resolver, fixed Python guest agent/transport, context-separated network agent, terminal sweep/history, E00 field/stage catalog, create-only protected snapshot store/pipeline and native binding/volume validation. Three test modules add 146 actual workspace cases over dev2.

## Changed

Coordinator single-acquisition reconciliation support; missing-target-safe PASSIVE/SUPPORT plans; fixture rejection at the native trust boundary; fixed feature command vectors and explicit servicing outputs; serializable actuator results; atomic metadata child ownership; LAB-vs-SITE terminal predicate separation; bundle privacy/integrity propagation; static parsing includes guest Python source.

Author integration corrections include preserving 2/22/23 bundle outcomes, not reallocating already committed snapshot bytes during final checks, reserving multiple pending snapshots, replacing the pre-C3 whole-runtime boundary with the actual protected data/config boundary, and binding restored owner postchecks to the recorded pre-C3 proof. A completed native run lacking fresh effective assertions now blocks explicitly instead of returning a metadata-only NOOP.

## Unchanged / not delivered

No FD/D00/AC or authoritative artifact changes. No native execution or qualification. No complete active CLI, no complete native NOOP/safe-pause/cancel path, no full route/failure harness, and no full-scope code-review candidate. Existing five foundation procedures are retained, not falsely presented as new complete harness support.
