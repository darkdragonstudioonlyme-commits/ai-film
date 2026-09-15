# NEXT WORK ITEM — residual CR-P00-001 author-completeness audit

```yaml
WORKFLOW_ID: WF-P00-IMPL-CR001-RESIDUAL-AUDIT
LANE: IMPLEMENT
STATUS: READY
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-001
INPUT_COMMIT: 2ac37acdd3f81d3b86d4ffb019689655110a80c2
GOAL: "Determine actual remaining reviewed Phase00 implementation scope and close every genuine source/harness/docs/test gap before AUTHOR_COMPLETE."
SUCCESS_OUTPUT: "Evidence-backed residual gap inventory with either zero implementation gaps or exact next implementation increment(s)."
ON_SUCCESS: WF-P00-FINAL-AUTHOR-CANDIDATE
ON_FAIL: WF-P00-IMPL-RESIDUAL-FIX
```

## Audit method

1. Re-read the exact reviewed contract set (`PHASE00_INFRA_DESIGN_V2`, Acceptance Matrix V2, Failure/Recovery V2, Evidence Register V2) and compare against production source paths, not stale remaining-work prose.
2. Search explicit/implicit stubs: NOT_IMPLEMENTED, PARTIAL, TODO/FIXME, fail-closed placeholders, fixture-only seams, metadata-only tools, unreachable/unwired branches, missing production factory composition, unhandled recovery/publication states, incomplete authority/trust edges.
3. Audit all 86 harness procedures for executable source completeness separately from native execution status; `NOT_RUN` is expected until VALIDATION.
4. Audit production request/factory/session paths so author tests cannot pass only through synthetic lower ports that production never composes.
5. Reconcile old `IMPL-REM-01…08` / blocker docs with actual source; retire stale items rather than carrying obsolete debt forward.
6. For every suspected gap, cite exact contract requirement + source evidence and classify: IMPLEMENTATION_GAP, VALIDATION_ONLY, DOCUMENTATION_STALE, DESIGN_GAP, or CLOSED.
7. If implementation gaps remain, create the smallest coherent increment and continue IMPLEMENTATION. If none remain, update author-completeness docs/evidence and create final immutable candidate for formal CODE_REVIEW.

## Constraints

Do not execute native Windows/WSL/LAB/SITE validation during this audit. Do not convert `NOT_RUN` native cases into PASS. Do not lower acceptance or change reviewed contracts to eliminate a gap.
