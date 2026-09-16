# Documentation System R9 — V39 long-horizon readiness reconciliation

## Purpose

V39 reconciles a material expansion of the non-native production-like control plane and the scheduled V39 effectiveness measurement for learning 005. It does not change product implementation, native configuration, package content, product test oracle, LAB/SITE execution status, qualification or HOST_READY.

## Operational state transition

The production-like control plane changes from eight to ten supervised timers and from a 44-file to a 58-file safe control recovery set. New supervised controls are a daily full DR recovery rehearsal and a weekly fail-closed negative-verifier campaign. Health/recovery now explicitly order after and want runtime integrity verification, rather than depending only on timer offsets.

The full DR rehearsal consumes the portable transfer export into a disposable root, verifies/restores the control manifest, required tooling and timer definitions, compiles recovered Python control scripts, verifies 283 reviewed app files, creates a fresh venv and reproduces `0.1.0.dev21`, `86 NOT_RUN` and `host_ready=false`.

The fail-closed campaign imports the actual live backup/export/rebuild verifier modules and runs eight corrupted/stale/unsafe disposable cases. All eight were rejected and live artifacts were reverified afterward.

A read-only V02 staging preflight now wraps the exact authority validator and normalizes MISSING/INVALID/READY_FOR_INTAKE while verifying the staging tree is unchanged. It never writes the authoritative READY flag, trust anchor, LAB state or native results.

## Recovery-state migration finding

When the recovery schema expanded, the stricter rehearsal correctly failed against the old 44-file export. V39 preserves that failure as evidence and records the correct producer-before-consumer migration sequence: `backup -> mirror -> export -> rehearsal -> negative campaign -> health`. No recovery requirement was weakened to accept old-schema payload.

The private Google Drive metadata was also normalized: it pins only stable exact-candidate/rebuild identities. Rotating backup/export hashes are intentionally not pinned there because normal scheduled rotation changes them. Binary payload remains on-host and `OFF_HOST_DR_CLAIMED=false`.

## Lifecycle transition

Learning 005 reaches its scheduled V39 gate. V38 already finalized its transition-only activation to durable PASS/ACTIVE before the V39 review/audit contract replaces final-review/final-audit fields. Learning 005 becomes EFFECTIVE only if the exact final V39 tree and CI pass without another stale prior-promotion state.

Learning 006 generalizes recovery-state versioning and stable-vs-rotating identity. It is R7/A7-gated `ACTIVE_ON_PROMOTION` and remains `PENDING_MEASUREMENT` until V41. V39 activation is not effectiveness evidence for learning 006.

## Promotion contract

V39 predeclares `DOC-V2-R9-REVIEW-007` and `DOC-V2-R9-AUDIT-007`. The exact final design tree must pass lifecycle, 9-case adversarial regression, documentation governance, docs consistency, holistic audit, workflow continuity and runtime-state checks. Review and audit must bind the same design SHA. Promotion is verdict-only and must be followed by post-promotion CI.
