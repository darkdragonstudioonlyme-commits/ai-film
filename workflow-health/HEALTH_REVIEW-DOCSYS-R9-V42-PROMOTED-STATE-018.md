# HEALTH_REVIEW-DOCSYS-R9-V42-PROMOTED-STATE-018

```yaml
HEALTH_REVIEW_ID: HEALTH-DOCSYS-R9-V42-PROMOTED-STATE-018
TRIGGER: "Post-R14/A14 promoted-tree semantic reread"
BASE_MAIN_COMMIT: 176aa7452e1c14c67b0768dd75181331f561d95e
STATE_VERSION: 42
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: PROMOTED_SEMANTIC_SURFACE_GAP
PRODUCT_SOURCE_CHANGED: false
NATIVE_EXECUTION_ADVANCED: false
```

## Recurrence

Historical/prior-tree R14/A14 and post-promotion CI succeeded, and `PROMOTION_STATE` was already `ACTIVE_ON_PROMOTION`. However `PROJECT_STATE.md` still described current R14/A14 as prospective and the current tree as a candidate awaiting replacement. The checker enforced current verdict ordinal consistency but did not enforce role-aware stage semantics for the same current pair.

This is direct negative evidence against learning 010's success metric: main still required a semantic wording correction after promotion. Learning 010 is therefore INEFFECTIVE rather than left pending, and successor learning 011 is introduced.

## Guardrail

The checker now derives documentation role from canonical branch fields or `AIFILM_DOCSYS_ROLE`. On PROMOTED/GENERIC trees it rejects candidate/pending promotion state and current-pair prospective/pending/awaiting-review wording. Adversarial fixtures prove the same wording remains legal on DESIGN role.

V02 remains blocked at external authenticity/authority; LAB remains stopped and native execution is not advanced by this documentation correction.
