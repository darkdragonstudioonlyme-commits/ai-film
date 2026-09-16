# DOCSYS-V2-R9 — Correction R1: Promotion-state-independent adversarial fixtures

## Trigger

The first R9 promotion commit correctly added both immutable verdict records and the lifecycle checker correctly resolved promotion evidence. Post-promotion CI run `35089621367` then failed in the adversarial regression suite because the `partial_promotion_verdict` test copied the **already promoted** repository, including both real verdict files, before trying to simulate a partial-verdict state.

The checker was correct. The negative-test fixture was not isolated from ambient repository lifecycle state.

## Root cause

The test encoded a hidden precondition: “final review/audit files are absent before the mutation”. That was true on the design branch and false after promotion. Because the test did not normalize that precondition itself, its expected failure reason depended on when in the documentation lifecycle the same test ran.

## Correction

`tools/test_learning_lifecycle_checker.py` now:

1. derives current documentation release, final review/audit IDs, and final verdict paths from `PROJECT_STATE.md`;
2. removes any ambient current final-verdict files **inside the temporary copied fixture only** before simulating partial or mismatched promotion states;
3. creates the exact simulated review/audit documents using the current state contract;
4. therefore executes identical negative semantics on promotion-ready and promoted repositories.

The correction changes test/control-plane evidence only; lifecycle checker semantics are unchanged.

## Self-learning update

The incident creates `LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003`:

> Adversarial/negative tests must establish every fixture precondition they rely on; they must not infer lifecycle phase from ambient repository contents.

State V34 records this learning as `ACTIVE_ON_PROMOTION` subject to corrected review/audit R2. Existing `LEARNING-LIFECYCLE-CONSISTENCY-002` is now evidence-backed ACTIVE from R1/A1 and remains pending effectiveness measurement.

## Governance recovery

Because regression tooling is part of documentation governance, the fix is **not** patched into main outside governance. Correction branches are:

- design: `lane/docs-v2-r9-r1-design`
- review: `lane/docs-v2-r9-r1-review`
- audit: `lane/docs-v2-r9-r1-audit`

Final correction verdicts are predeclared:

- `DOC-V2-R9-REVIEW-002` → `reviews/DOCUMENTATION_SYSTEM_R9_REVIEW_R2_PASS.md`
- `DOC-V2-R9-AUDIT-002` → `reviews/DOCUMENTATION_SYSTEM_R9_AUDIT_R2_PASS.md`

After corrected audit, only those two verdict records may be added to the exact correction tree before promotion.

## Acceptance

Correction is acceptable only if:

- the adversarial suite passes on the already-promoted R9 base;
- exact correction design CI passes all portable R9 guardrails;
- review confirms no lifecycle checker semantic weakening;
- audit confirms R1/A1 remain immutable historical evidence and R2/A2 bind one exact correction target;
- post-correction promotion CI passes on main with real R2/A2 verdicts present;
- product validation state remains `RUN-P00-VALIDATION-001/V02` with no native authority change.
