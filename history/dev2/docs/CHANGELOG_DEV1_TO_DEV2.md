# Changelog — dev1 → dev2

Status remains partial. Frozen design/public contracts unchanged.

Added concrete native foundation modules, read-only trust adapter and actual design-review normalization; native C0 inventory/metadata entry source; native supervisor and actuator components; fixed collector scripts; original-plan reconciliation; bounded DIRECT HTTPS component; protected snapshot/scanner/publisher; limited native foundation harness; two syntax-envelope schemas; source identity and static-check tooling.

Changed Coordinator to persist additional native child witnesses and retain a native mutex until controller exit when unresolved. Changed POSIX native-preflight expected error from generic backend-unavailable to WINDOWS_X64_REQUIRED, reflecting the newly routed C0 entry; other active interfaces still reject as unimplemented. No test was turned into a skip or an acceptance waiver.

Added native fake API, transport, trust/path, snapshot and journal tests. Existing source tests retained; initial dev2 reason-mismatch failure and dev1 historical reports are preserved. Actual native T/F outcomes remain NOT_RUN.

Updated native-test inventory with limited foundation contributions without closing parent or expanded cases. Root state advances V6→V7; V6 and old reports live under history/dev1.

The source diff is relative to bytes in the parent ZIP, not inferred from chat summaries. It includes source/config/schema/native/tests/tools/packaging metadata, not a claim that the full deployment has been implemented.
