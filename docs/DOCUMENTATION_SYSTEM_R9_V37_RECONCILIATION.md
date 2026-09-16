# Documentation System R9 — V37 phased production-like export reconciliation

## Purpose

State V37 reconciles operational facts that changed after V36 while preserving all product/native boundaries. It does not introduce a new documentation release, product implementation, native configuration, test oracle, LAB result, qualification, SITE result or HOST_READY claim.

## Exact operational deltas

The validation lane now records a phased execution model and production-like control plane with eight supervised timers rather than seven. The added timer owns deterministic transfer-ready DR export refresh and verification every six hours. Runtime health treats export freshness/integrity, previous job success and the expected ten-minute timeout as hard invariants.

The safe control backup grows from 39 to 44 whitelisted files because it additionally carries the transfer-export builder/verifier, systemd service/timer and timeout drop-in. The NTFS host mirror carries the same 44-file control state. Neither backup includes protected authority, protected identity or credentials.

The portable transfer export is deterministic for identical payload state. It contains seven payloads: current verified control backup plus sidecar and exact non-secret dev21 rebuild artifacts. The heavy export drill uses the portable ZIP alone, verifies its embedded control backup, re-verifies 283/283 source bytes, builds a fresh isolated venv and reproduces `0.1.0.dev21`, `86 NOT_RUN` and `host_ready=false`.

A private Google Drive document stores checksum/identity metadata for the currently anchored deterministic export. The binary payload remains on the original host. V37 therefore keeps `OFF_HOST_DR_CLAIMED=false` and `OFFHOST_BINARY_PAYLOAD_UPLOADED=false`.

## Phase contract

The operational sequence is explicitly split into six phases so later sessions resume at a precise boundary:

1. **A — State/authority recheck:** confirm V02, LAB stopped, READY absent, trust absent.
2. **B — DR export automation:** repeatable atomic builder + verifier + heavy drill.
3. **C — Health integration:** supervised timer, timeout, hardening and health invariants.
4. **D — End-to-end recovery drill:** backup → mirror → export → recovery → health.
5. **E — Control-plane reconciliation:** validation evidence and canonical V37 review/audit.
6. **F — Native gate recheck:** re-evaluate external authority only after Phase E closes.

No phase before F can change V02 `DONE_WHEN`.

## Learning lifecycle constraint

Learning 004 remains pending until state version 38. V37 is intentionally one canonical transition before that gate. The lifecycle register is not edited in V37. Any attempt to mark learning 004 EFFECTIVE here is a review/audit failure.

## Promotion contract

V37 predeclares `DOC-V2-R9-REVIEW-005` and `DOC-V2-R9-AUDIT-005`. The design tree must pass the full lifecycle/adversarial/governance/docs/audit/continuity/runtime-state suite. Review and audit must bind the same exact design SHA. Promotion is verdict-only, followed by mandatory post-promotion CI.