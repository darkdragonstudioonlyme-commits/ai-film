# HEALTH_REVIEW-DOCSYS-R9-CI-002

```yaml
HEALTH_REVIEW_ID: HEALTH_REVIEW-DOCSYS-R9-CI-002
TRIGGER: "Post-promotion Documentation Governance CI run 35089621367 failed in adversarial lifecycle regression after lifecycle checker itself passed with promotion evidence resolved."
WORKFLOW: DOCSYS-V2-R9
STATE_BEFORE: "State V33 / main 607eb01e... / R9 verdict pair present / product validation RUN-P00-VALIDATION-001 unchanged"
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: TOOLING
LEARNING_IDS:
  - LEARNING-ADVERSARIAL-FIXTURE-ISOLATION-003
LEARNING_ACTIVATION_STATUS: "Candidate correction requires reopened DOC-REVIEW/DOC-AUDIT before promotion"
LEARNING_EFFECTIVENESS_STATUS: "PENDING_MEASUREMENT"
RETURN_TO: "After corrected R9 review/audit/promotion, resume unchanged RUN-P00-VALIDATION-001/V02."
RESULT: "Adversarial fixture made ambient-state-independent; State V34 reopens exact documentation review/audit."
```

## Failure evidence

Promotion CI run `35089621367`, job `104772577496` showed:

- `Learning lifecycle` PASS with `promotion_evidence=resolved` and exact target `7eb160ee18c349ed7cb539250179c96df87137fa`;
- `Adversarial lifecycle regression` FAIL only in `partial_promotion_verdict`;
- the test expected `partial-promotion-verdict-set` but received `promotion-target-design-mismatch` because the copied promoted repository already contained the real audit record.

This was a regression-test fixture bug, not a lifecycle-checker or promotion-evidence bug.

## Recovery

The correction derives final review/audit IDs and paths from `PROJECT_STATE`, deletes any ambient verdict files inside each temporary fixture before constructing simulated partial/mismatched scenarios, and therefore has the same semantics before and after promotion.

Correction branch CI run `35089806760` PASSed after the fixture fix on the promoted R9 base.

Because checker/regression tooling is documentation governance, the correction is not patched directly into main as an unreviewed hotfix. State V34 reopens detailed review and holistic audit before corrected promotion.
