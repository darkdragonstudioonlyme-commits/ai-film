# LEARNING-EVIDENCE-SEMANTICS-007 — Semantic evidence and stage-aware governance

```yaml
LEARNING_ID: LEARNING-EVIDENCE-SEMANTICS-007
DISCOVERED_IN: DOCSYS-R9-V41-FORENSIC-012
CLASS: PROCESS
OBSERVATION: "Structural lifecycle checks could accept unrelated existing evidence paths as effectiveness proof, mutable register wording could drift from immutable success metrics, and verdict-bearing REVIEW/AUDIT branches could report PASS while stage-insensitive CI failed on an expected partial verdict set."
ROOT_CAUSE: "The control plane enforced artifact existence and promoted-tree invariants more strongly than semantic metric binding and workflow-stage semantics."
REUSABLE_RULE: "Bind effectiveness to the immutable metric through a reviewed measurement receipt; fail closed on metric drift; distinguish DESIGN, REVIEW, AUDIT and PROMOTED invariant sets; do not interpret a structural checker beyond predicates it actually verifies."
SCORE: 10
CURRENT_ACTION: "Harden lifecycle checker/adversarial tests, add stage-aware verdict validation, expand CI lifecycle-domain triggers, and measure recurrence at the next documentation promotion."
POLICY_OR_TOOL_PROMOTION: "SELF_LEARNING.md; WORKFLOW_HEALTH.md; GIT_WORKFLOW.md; tools/check_learning_lifecycle.py; tools/test_learning_lifecycle_checker.py; .github/workflows/documentation-governance.yml"
SUCCESS_METRIC: "Future EFFECTIVE transitions bind the immutable success metric to explicit scope/sample/predicate evidence, unrelated existing files cannot satisfy effectiveness, metric-definition drift fails closed, and legitimate DESIGN/REVIEW/AUDIT verdict stages do not generate false promotion-state CI failures."
STATUS: CANDIDATE_PENDING_R11_A11
```

The current candidate predeclares activation through R10/A10. Effectiveness is not claimed by this record; it must be measured after a later qualifying lifecycle/promotion transition.
