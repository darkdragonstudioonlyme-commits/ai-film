# HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015

```yaml
HEALTH_ID: HEALTH_REVIEW-DOCSYS-R9-V41-AUTHORITY-015
TYPE: POST_PROMOTION_SEMANTIC_AUTHORITY_DRIFT
BASE_MAIN_COMMIT: c8c7f3db649d03ce913bb4b386f74a9fd8a107d4
PRIOR_FINAL_REVIEW_ID: DOC-V2-R9-REVIEW-011
PRIOR_FINAL_AUDIT_ID: DOC-V2-R9-AUDIT-011
PRIOR_EXACT_DESIGN_SHA: 237228e0c5ed3e3cde20379cb6099365f2ef938b
NEW_REVISION: R11_V41_AUTHORITY_REFERENCE_CONSISTENCY
NEW_REVIEW_ID: DOC-V2-R9-REVIEW-012
NEW_AUDIT_ID: DOC-V2-R9-AUDIT-012
DETECTOR_MEASUREMENT_COMMIT: 0d106cbad7e144b737cb43eb17409339d107021d
DETECTOR_GREEN_RUN: 35223256888
DETECTOR_GREEN_JOB: 105208358932
PRODUCT_SOURCE_CHANGED: false
NATIVE_VALIDATION_ADVANCED: false
STATUS: CORRECTION_CANDIDATE_REQUIRES_R12_A12
```

## Observation

After R11/A11 promotion completed and `main` CI was green, a fresh canonical reread found a contradiction between structured governance and live prose:

- `PROJECT_STATE.md` structured fields selected R11/A11, but its final validity sentence still said independent R10/A10 review;
- `AI_FILM_STATE_CHECKPOINT_V41.md` listed the R11/A11 record paths but retained a heading and promotion sentence that treated R10/A10 as current authority;
- `docs/DOCUMENTATION_SYSTEM_R9_V41_FORENSIC_HARDENING.md` contained one unqualified sentence saying R10/A10 decide semantic receipt validity.

The old R10/A10 artifacts are legitimate historical evidence for their old SHA, but they were explicitly superseded for promotion. Therefore those unqualified live-authority sentences were semantically false even though all structural CI checks passed.

## Root cause

The control plane validated required tokens, lifecycle structure, exact verdict records, stage roles and Markdown/JSON state at selected fields, but it had no machine-readable pointer to the active design surface and no dynamic invariant tying live `R<n>/A<n>` prose to `FINAL_REVIEW_ID` / `FINAL_AUDIT_ID`.

This is a method weakness, not a reason to erase prior PASS evidence: R11/A11 correctly reviewed their exact target under the then-existing checks, while the checks were incomplete for cross-surface authority semantics.

## Detector execution evidence

The first candidate detector failed closed on the new design branch in run `35223022725`, exposing three line-local historical-context false positives. After wording refinement, run `35223154818` failed on the remaining `reusing` morphology case. The checker was then generalized from literal `reused` to reuse-stem context rather than disabling the invariant.

Exact detector commit `0d106cbad7e144b737cb43eb17409339d107021d` passed run `35223256888` / job `105208358932`: learning lifecycle, 16 adversarial lifecycle cases, documentation governance, active documentation consistency, workflow continuity and holistic audit were all green.

This sequence is retained as negative/positive control-plane evidence. It demonstrates fail-closed behavior plus correction of false positives without removing the semantic invariant.

## Learning/control-plane reconciliation

- `LEARNING-CONTROL-001` reached its real `STATE_OR_CHECKER_SCHEMA_EVOLUTION` trigger. Its immutable metric allows checker edits when a semantic invariant changes; this incident required exactly such an invariant. The candidate metric-bound receipt is `learning/measurements/MEASUREMENT-LEARNING-CONTROL-001-001.md` and remains subject to R12/A12 semantic review.
- `LEARNING-AUTHORITY-REFERENCE-CONSISTENCY-008` records the reusable rule. It is only `ACTIVE_ON_PROMOTION` through predeclared R12/A12 evidence and remains `PENDING_MEASUREMENT` afterward.
- `LEARNING-EVIDENCE-SEMANTICS-007` is finalized from its already-completed R11/A11 activation evidence and no longer depends on the current promotion's final fields.

## Correction candidate

1. Allocate new R12/A12 verdict identities for the changed exact tree; never reuse R11/A11.
2. Add `DESIGN_RECORD` to canonical governance and enforce Markdown/JSON parity for governance identity fields.
3. Derive the expected live verdict pair from canonical final IDs and scan current state, current checkpoint and active design record for mismatched pairs.
4. Permit mismatched pairs only when the same line explicitly marks them as prior/old/historical/superseded/reuse/earlier/previous/pre-promotion evidence.
5. Add persistent adversarial active-doc tests proving stale live authority fails, explicit historical authority passes and structured-governance parity drift fails.
6. Finalize learning 007 from `ACTIVE_ON_PROMOTION` to `ACTIVE` using its already-completed R11/A11 activation evidence.
7. Submit CONTROL-001 effectiveness and learning 008 activation as candidate lifecycle transitions for independent R12/A12 verification.

## Non-claims

No product source, LAB execution, native procedure status, SITE evidence, qualification or HOST_READY state changed. GitHub `main` protection remains an external platform setting and is not claimed as enforced.
