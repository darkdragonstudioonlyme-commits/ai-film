# LEARNING-CURRENT-EVALUATION-EVIDENCE-009 — Current-evaluation evidence integrity

```yaml
LEARNING_ID: LEARNING-CURRENT-EVALUATION-EVIDENCE-009
DISCOVERED_IN: HEALTH-WF-P00-V02-POSTDEPLOY-005
CLASS: PROCESS
OBSERVATION: "A derived native-policy candidate could outlive a later failed authority reevaluation, a read-only preflight bound metadata but not file bytes, and initial CI attempts tried to treat non-authoritative repository source as exact source."
ROOT_CAUSE: "Control-plane evidence validity was modeled too durably across reevaluations, unchanged-tree evidence was weaker than its prose claim, and CI portability was not separated from exact-source authority."
REUSABLE_RULE: "Invalidate READY-derived artifacts before reevaluation and on every unsuccessful exit; cryptographically bind bytes/link identity for unchanged-tree claims; never substitute a non-authoritative source tree when exact source is unavailable."
SCORE: 10
CURRENT_ACTION: "Activate only after R13/A13 promotion; measure at the next authority reevaluation or evidence-integrity/source-addressability regression."
POLICY_OR_TOOL_PROMOTION: "validation/tooling/pre-v03-authority-stage.sh; validation/tooling/v02-authority-preflight.py; .github/workflows/validation-v02-tooling.yml; SELF_LEARNING.md"
SUCCESS_METRIC: "Future authority/control-plane reevaluations invalidate prior derived READY artifacts before evaluation and on every unsuccessful exit; read-only unchanged-state claims bind file bytes and link identity; and CI never substitutes a non-authoritative source tree for an unavailable exact source."
STATUS: CANDIDATE_PENDING_R13_A13
```

The validation-lane event is immutable discovery evidence. Canonical activation is conditional on exact V42 review/audit/promotion; effectiveness remains pending a future qualifying event after activation.
