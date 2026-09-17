# Continuity event receipts

This domain stores immutable evidence for effectiveness measurement of workflow interruption/resume behavior. Live mutable run state remains on the owning lane in workflow-runs/<RUN_ID>.md; these receipts do not replace that ledger.

## When to write a receipt

Write a receipt only after a real interruption/resume has been reconciled. Normal progress updates, deliberate pauses, repeated preflight checks and chat messages saying continue are not qualifying events by themselves. Do not backfill an event unless interruption and resume identities are independently evidenced.

PASS events prove that the same logical RUN_ID was adopted, no duplicate logical run was created, and no completed expensive step was repeated unless relevant identity changed. FAIL events are preserved with measurement_eligible=false and are never hidden merely to improve the success metric.

## JSON schema

Each *.json file has schema_version=1 and exactly these fields:

- event_id — CONTINUITY-EVENT-* unique receipt identifier.
- event_kind — INTERRUPTED_RESUME.
- run_id / workflow_id / owner_lane / base_identity — exact logical run identity.
- interrupted_step / resumed_step — stable step identifiers.
- same_run_id — boolean.
- identity_changed — boolean; permits a necessary repeated affected step, never a duplicate logical run.
- duplicate_logical_runs — non-negative integer.
- repeated_completed_expensive_steps — non-negative integer.
- resume_disposition — REUSE_VERIFIED_OUTPUT, RECONCILE_AND_CONTINUE, or SAFE_REEXECUTE_AFFECTED_STEP.
- interruption_evidence / resume_evidence — non-empty lists containing exact evidence references and at least one 40-hex commit identity each.
- event_identity_sha256 — SHA-256 of canonical JSON over all fields except event_id and event_identity_sha256. Excluding event_id prevents double-counting the same semantic event under multiple receipt names.
- result — PASS or FAIL.
- measurement_eligible — boolean. Only PASS + true receipts count toward effectiveness.

## Measurement rule

The canonical state publishes qualifying_event_count and required_event_count. tools/check_continuity_measurements.py derives the actual count and fails on drift, duplicate semantic events, tamper, malformed evidence, PASS events with duplicate logical runs, or repeated completed expensive steps without identity change.

When qualifying count reaches the learning gate, status becomes READY_FOR_EFFECTIVENESS_REVIEW. The checker never changes LEARNING_STATE to EFFECTIVE; review/audit must still bind a metric receipt.
