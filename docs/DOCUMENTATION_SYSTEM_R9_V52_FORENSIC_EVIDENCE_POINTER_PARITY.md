# DOCSYS-V2-R9 — V52 forensic evidence-pointer parity

DESIGN_ID: DOCSYS-R9-V52-FORENSIC-EVIDENCE-POINTER-PARITY
TARGET_RELEASE: DOCSYS-V2-R9
TARGET_STATE_VERSION: 52
REVISION: R25_V52_FORENSIC_EVIDENCE_POINTER_PARITY
BASE_MAIN_COMMIT: f297d9d6e4f33859b73da7c86c6966f77bf41fab
DESIGN_BRANCH: lane/docs-v2-r9-v52-forensic-evidence-pointer-parity-design
REVIEW_BRANCH: lane/docs-v2-r9-v52-forensic-evidence-pointer-parity-review
AUDIT_BRANCH: lane/docs-v2-r9-v52-forensic-evidence-pointer-parity-audit
REQUIRED_REVIEW_ID: DOC-V2-R9-REVIEW-026
REQUIRED_AUDIT_ID: DOC-V2-R9-AUDIT-026
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false

## Finding

V51 section-aware inventory found that duplicated forensic evidence pointers were not comprehensively machine-enforced. `AUTHORITY_REFERENCE_EVIDENCE` and `CI_CREDENTIAL_ISOLATION_EVIDENCE` matched machine state, but `FORENSIC_HARDENING.PROMOTION_FINALIZATION_EVIDENCE` differed: Markdown retained V42 while machine state retained the V49 health record introduced in the exact historical/prior-tree R23/A23-reviewed V49 tree.

This is distinct from `DOCUMENTATION_GOVERNANCE.PROMOTION_FINALIZATION_EVIDENCE`, which has its own owner and already matches machine documentation-governance state. Section-specific parsing is therefore required; global same-name lookup is insufficient.

## Negative-first proof

Test-only commit `7a70127065abb6e42bdfff1c233b7feac545fac9` expands active-doc adversarial coverage from 14 to 18 cases: parity mutations for the three forensic evidence pointers plus a matching-but-nonexistent promotion-finalization target. Run `35303654597` / job `105471313759` passed baseline lifecycle/governance/docs and failed at Adversarial active docs regression before the checker correction.

## Pre-review baseline authoring failure

First correction commit `9f912ce0fcd08bac60bb41430c270db69515e62c` produced run `35303823020` / job `105471804671`. Lifecycle and documentation-governance steps passed, but baseline Active documentation consistency failed before adversarial execution because remote source reconstruction had corrupted/duplicated the checker helper region. The correction rebuilds `tools/check_project_docs.py` from the exact canonical V51 checker and reapplies only the intended section helper plus forensic parity/existence block. No V52 predicate or adversarial expectation is weakened.

## Pre-review provenance-authority correction

Clean checker rebuild `33201f568064018ff6dbd6b5f53b13b4f8359d93` produced run `35303968562` / job `105472239414`. Lifecycle and documentation-governance steps passed, but baseline Active documentation consistency rejected three V49 provenance references because historical/prior-tree R23/A23 was not marked historical within the pair-local clause. The correction changes only those provenance phrases; the forensic pointer values, checker predicates and 18 adversarial expectations remain unchanged.

## Correction

V52 adds section-aware field parsing and enforces machine/Markdown equality plus target existence for:
- `FORENSIC_HARDENING.PROMOTION_FINALIZATION_EVIDENCE`;
- `FORENSIC_HARDENING.AUTHORITY_REFERENCE_EVIDENCE`;
- `FORENSIC_HARDENING.CI_CREDENTIAL_ISOLATION_EVIDENCE`.

The promotion-finalization pointer is reconciled to `workflow-health/HEALTH_REVIEW-DOCSYS-R9-V49-VALIDATION-P7-026.md`, the value already present in the exact V49 machine tree reviewed/audited by historical/prior-tree R23/A23. V52 does not self-reference its own health record as prior promotion-finalization proof.

## Scope and boundaries

No product source/package, validation head/tooling, V02 predicate, native procedure, learning lifecycle outcome or continuity receipt changes. Platform protection representation is intentionally outside raw pointer parity. No new standalone learning is created; this is further implementation of V51 memory rule on duplicated evidence pointers.

## Exact-tree rule

R26/A26 are the final verdict identities for one semantic tree. Review/audit may add verdict artifacts only; any semantic state/checker/test change afterward reopens review/audit.
