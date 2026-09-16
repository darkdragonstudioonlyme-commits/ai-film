# DOCSYS-V2-R9 — Reconciliation R2: close self-learning effectiveness and resume routing

## Purpose

V35 is a post-promotion reconciliation, not a new learning-policy design. It closes evidence from the R9 checker-regression recovery and removes the last stale governance routing residue before returning control to Phase00 validation.

## Inputs

- initial R9 promotion CI failure: run `35089621367`;
- fixture-isolation correction verification: run `35089806760`;
- exact V34 correction design CI: run `35090191030`;
- successful post-correction promotion CI: run `35090425340`, job `104775167330`;
- immutable correction learning: `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003`;
- immutable effectiveness health record: `HEALTH_REVIEW-DOCSYS-R9-CI-003`.

## Reconciliation

1. Transition `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003` from promotion-conditional/pending measurement to evidence-backed `ACTIVE` + `EFFECTIVE`.
2. Reduce `PENDING_EFFECTIVENESS_MEASUREMENT` from 2 to 1; `LEARNING-LIFECYCLE-CONSISTENCY-002` remains pending at V36.
3. Keep `OVERDUE_EFFECTIVENESS_MEASUREMENT=0`.
4. Generalize the adversarial `stale_activation` fixture so it does not assume an `ACTIVE_ON_PROMOTION` entry still exists after promotion.
5. Replace stale documentation-governance `NEXT_ACTION` wording with the actual product route `RUN-P00-VALIDATION-001/V02_LAB_EXECUTION_AUTHORITY`.

## Authority boundaries

This reconciliation does not change:

- lifecycle checker semantic rules;
- product source or product tests;
- exact dev21 code/package identity;
- native LAB/SITE authority;
- qualification or HOST_READY;
- the current product workflow/run identity.

## Review rule

Because V35 changes canonical state and lifecycle evidence after an audited promotion, it is reviewed/audited as a separate correction rather than edited directly on main.

Final verdicts are predeclared:

- `DOC-V2-R9-REVIEW-003` / `reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R3_PASS.md`
- `DOC-V2-R9-AUDIT-003` / `reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R3_PASS.md`

Post-audit promotion must add only these two immutable records to the exact V35 reconciliation target. Post-promotion CI must pass before the documentation self-learning review is considered fully closed.