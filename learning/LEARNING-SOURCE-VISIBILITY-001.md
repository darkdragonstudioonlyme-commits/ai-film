# LEARNING-SOURCE-VISIBILITY-001

```yaml
LEARNING_ID: LEARNING-SOURCE-VISIBILITY-001
DISCOVERED_IN: dev20 continuation / GitHub source visibility review
CLASS: TOOLING
OBSERVATION: "Exact local source commit and verified package existed, but a GitHub reader could not inspect ordinary source files until a partial snapshot branch was created."
ROOT_CAUSE: "Persistence policy optimized byte durability and exact identity but did not model remote source visibility/addressability as a separate handoff property."
EVIDENCE:
  - SOURCE_IMPORT_STATUS.md
  - lane/implement-p00:LANE_STATE.md
  - snapshot/dev20-source:SOURCE_SNAPSHOT_DEV20.md
REUSABLE_RULE: "Every formal source handoff declares remote source addressability and full-mirror status; partial snapshots are useful but explicitly non-authoritative."
SCORE: 8
CURRENT_ACTION: "Add source-visibility fields/checkpoint to GIT_WORKFLOW, PROJECT_STATE and handoff reasoning."
POLICY_OR_TOOL_PROMOTION: "GIT_WORKFLOW.md; POLICY_REGISTRY.md; tools/check_documentation_governance.py"
ACTIVATION_TARGET: DOCSYS-V2-R8
ACTIVATION_STATUS: PENDING_ACTIVATION
ACTIVATION_BLOCKER: "Requires final DOC-REVIEW and holistic DOC-AUDIT PASS on exact corrected R8 tree."
ACTIVATED_IN: null
SUCCESS_METRIC: "Formal CODE_REVIEW handoffs always state exact source/package identity plus remote source visibility; no reader mistakes partial snapshot for full candidate."
REVIEW_STATUS: PENDING_R8_FINAL_REVIEW
STATUS: ACTIVE
```
