# LEARNING-PROMOTED-SEMANTIC-SURFACE-011 — Promoted authority surfaces must be stage-resolved

```yaml
LEARNING_ID: LEARNING-PROMOTED-SEMANTIC-SURFACE-011
DISCOVERED_IN: HEALTH-DOCSYS-R9-V42-PROMOTED-STATE-018
CLASS: PROCESS
OBSERVATION: "A promoted tree can carry the correct verdict ordinals and promotion-state field while current authority prose still describes the current verdict pair/tree as prospective or awaiting promotion."
ROOT_CAUSE: "Authority checks validated pair identity but not same-pair stage semantics under the PROMOTED role."
REUSABLE_RULE: "Current authority surfaces must be role-aware: promoted main rejects candidate/pending promotion state and prospective/pending/awaiting language for the current verdict pair; explicit historical prior-pair context remains readable."
SCORE: 10
CURRENT_ACTION: "Add role-aware promoted semantic checks and adversarial fixtures; keep the exact design prose valid through DESIGN/REVIEW/AUDIT/PROMOTED without post-merge semantic rewrite."
POLICY_OR_TOOL_PROMOTION: "tools/check_project_docs.py; tools/test_project_docs_checker.py; documentation governance CI"
SUCCESS_METRIC: "The next documentation promotion passes DESIGN, REVIEW, AUDIT and PROMOTED checks on one exact semantic tree; main contains no candidate/pending promotion state and no current-pair prospective/pending/awaiting-review wording, while explicitly historical prior verdict references remain readable."
STATUS: CANDIDATE_PENDING_R15_A15
```

Effectiveness is not claimed by this record. It is measured on the next documentation promotion after activation.
