# dev4 → dev5

Parent: exact `IMPL-P00-001_IMPLEMENTATION_PACKAGE_V4.zip`, SHA-256 `b1fb1ba7f4797048a4498387302b8e0c4fb66929ac4e10912a920f069e68d357`.

## Source changes

Original-request recovery now handles detached C0 reads before a mutation fence exists. Native read results inside actions use action-read records rather than creating orphan detached results. Read releases bind exact old request/read/witness or separately measured absence. Recovery journal links renewed request identity without replacing original plan bytes.

C0 capture and proposal binding now connect native metadata to unapproved deterministic plans. Journal byte reservation is enforced before native reads and every append/readback. Source references stay digest-pinned; fixture observations are not native inputs.

Primary CLI now dispatches pinned plans to concrete native adapters; previous unconditional active-entry stub is removed. C3 preconditions inspect pending reboot and installer state; first-user initialization can be observed through a current receipt instead of blindly replaying OOBE. Source factory construction and interface outcome handling have new tests.

Evidence snapshots now persist exact stage context. Requiredness cannot be inferred from status, and attempted C3/restore context is checked against source intents. Publication has a write-ahead output record, alias map persisted before output, retained output failure and read-only final-archive recovery. A failed native step attempts a protected snapshot without overriding the original failure.

A native LAB route controller and journal oracles were added. They are a partial contribution to the harness, not the full T/F fault suite or qualification issuer.

## Author checks and history

Dev4 baseline was rerun: 534 PASS. Final actual dev5 results are in the workspace report. Intermediate histories preserve publisher fixture wiring failure, CLI expected-error update, and a test-fixture journal representation error. They were fixed and regression rerun; no target VALIDATION_FAILURE is inferred. No native/guest/network test occurred.

## Scope

Blueprint, frozen FD-01…08 and approved D00-01…14 unchanged. Missing source is still tracked; no architecture redesign, code-review approval, phase gate or baseline promotion. Old reports/documents are historical, not evidence of current native readiness.

## Author regression correction — route pause identity

Four new negative oracle cases initially failed: a SAFE_PAUSE belonging to another original plan/request, tampered evidence digest, and missing matching CLEAR could still be recognized. The oracle now binds original plan/request, validates pause-observation digest and requires the linked durable release. One positive and four negative cases were added. This is an author-discovered source defect corrected before delivery, not native validation or a code-review verdict. First failing report and final passing report are retained.
