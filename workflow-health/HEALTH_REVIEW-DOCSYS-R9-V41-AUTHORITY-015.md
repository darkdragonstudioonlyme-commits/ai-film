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

## Correction candidate

1. Allocate new R12/A12 verdict identities for the changed exact tree; never reuse R11/A11.
2. Add `DESIGN_RECORD` to canonical governance and enforce Markdown/JSON parity for governance identity fields.
3. Derive the expected live verdict pair from canonical final IDs and scan current state, current checkpoint and active design record for mismatched pairs.
4. Permit mismatched pairs only when the same line explicitly marks them as prior/old/historical/superseded/reused/earlier/previous/pre-promotion evidence.
5. Finalize learning 007 from `ACTIVE_ON_PROMOTION` to `ACTIVE` using its already-completed R11/A11 activation evidence, preventing the next promotion's final-verdict fields from becoming an accidental dependency.
6. After the detector passes server CI, route the reusable rule into a new reviewed learning candidate and measure the pending checker/schema-evolution learning against this real event.

## Non-claims

No product source, LAB execution, native procedure status, SITE evidence, qualification or HOST_READY state changed. GitHub `main` protection remains an external platform setting and is not claimed as enforced.
