# LEARNING-DOCSYS-ACTIVATION-001

```yaml
LEARNING_ID: LEARNING-DOCSYS-ACTIVATION-001
DISCOVERED_IN: DOCSYS-V2-R8 governance review
CLASS: PROCESS
OBSERVATION: "R8 continuity learning was persisted and detailed-review PASSed, but holistic audit failure left the correction unpromoted while affected implementation work still needed the behavior."
ROOT_CAUSE: "The learning loop measured persistence/review but did not explicitly distinguish reviewed correction from canonically active correction."
EVIDENCE:
  - reviews/DOCUMENTATION_SYSTEM_R8_REVIEW_R4_PASS.md
  - reviews/DOCUMENTATION_SYSTEM_R8_AUDIT_R1_FAIL.md
  - lane/implement-p00:workflow-runs/RUN-P00-CR001-001.md
REUSABLE_RULE: "A reusable learning is applied only after its reviewed policy/tool/checker change is canonically active, or activation is explicitly blocked with owner/return path."
SCORE: 9
CURRENT_ACTION: "Add activation lifecycle fields, backlog/lag metrics and promotion-ready record predeclaration."
POLICY_OR_TOOL_PROMOTION: "SELF_LEARNING.md; WORKFLOW_HEALTH.md; tools/check_documentation_governance.py"
ACTIVATION_TARGET: DOCSYS-V2-R8
ACTIVATION_STATUS: PENDING_ACTIVATION
ACTIVATION_BLOCKER: "Requires final DOC-REVIEW and holistic DOC-AUDIT PASS on exact corrected R8 tree."
ACTIVATED_IN: null
SUCCESS_METRIC: "Zero reviewed systemic corrections silently treated as active before canonical promotion; learning activation lag/backlog visible in health review."
REVIEW_STATUS: PENDING_R8_FINAL_REVIEW
STATUS: ACTIVE
```
