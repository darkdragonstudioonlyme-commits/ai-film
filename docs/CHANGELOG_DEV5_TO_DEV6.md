# CHANGELOG — dev5 to dev6

This implementation-only revision preserves exact reviewed V2 behavior.

## Added

- `native/assessment.py`: write-ahead E00-17 proposal publication and exact read-only recovery of already-existing bytes. It never sets `accepted_by_master`, `qualification_issued`, or `host_ready`.
- Prior-guest source selection in `native/evidence_pipeline.py`: C3/GATE capture may consume actual guest facts from exact hash-linked prior operation observations named by current/history plan digests; unrelated plans and ambiguous/tampered events are rejected.
- Early failure capsule in `NativeDriver.record_failure`: after durable INTENT but before a usable snapshot exists, a bounded protected journal event records normalized failure/fence facts without fabricating E00 observations.
- Author tests for assessment recovery, prior-guest provenance, and early failure capture.

## Changed

- E00-17 publication now records intent before create-only output, records observed output only after successful creation, and can be reconciled without overwrite.
- `pyproject.toml` version advanced to `0.1.0.dev6`.

## Still open

This is not author-complete. Non-DIRECT network transport, executable/dependency trust closure, remaining service/OOBE/restart/resume integration, full nested/prior-stage E00 semantics, and the complete causal 86-case controller harness remain open under IMPL-REM-01…08 / IMPL-BLOCK-01…03.
