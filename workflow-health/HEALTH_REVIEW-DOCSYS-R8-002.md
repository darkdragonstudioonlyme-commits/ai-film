# HEALTH_REVIEW-DOCSYS-R8-002

```yaml
HEALTH_REVIEW_ID: HEALTH_REVIEW-DOCSYS-R8-002
TRIGGER: "User-requested design/self-learning/smoothness review after R8 detailed PASS but holistic audit FAIL, plus observed dev20 source-visibility friction."
WORKFLOW: DOCSYS-V2-R8
STATE_BEFORE: "R8 detailed review PASS on 908a96d7..., holistic audit FAIL with DOCV2-R8-A01/A02; main still DOCSYS-V2-R6; dev20 advanced locally/ledger to verified package and S07."
HEALTH_STATE: META_REVIEW_REQUIRED
ROOT_CAUSE_CLASS: PROCESS_AND_GOVERNANCE
RETURN_TO: "Promote exact R8 tree after final DOC-REVIEW + DOC-AUDIT PASS, then resume RUN-P00-CR001-001/S07."
RESULT: SYSTEMIC_CORRECTION_AUTHORED_PENDING_INDEPENDENT_REVIEW
LEARNING_ACTIVATION_STATUS: PENDING_ACTIVATION
```

## Symptoms and wasted-work risk

- Standing docs named generic documentation branches/worktrees that no longer matched the governed release-scoped lanes.
- Promotion metadata was not fully predeclared inside the exact audited tree, risking another post-audit edit/review loop.
- R8's continuity learning was correct and detailed-review PASSed but still not active because holistic audit failed; the learning loop did not explicitly surface activation lag.
- Dev20 source/package identity was durable, yet GitHub readers still lacked ordinary source visibility until a partial snapshot was created.

## Systemic correction

- derive documentation governance lane/worktree identity from canonical state;
- predeclare exact final review/audit IDs and paths in promotion-ready state/checkpoint;
- add `tools/check_documentation_governance.py` for stale fixed lane identities and required promotion/activation/source-visibility fields;
- add explicit learning activation lifecycle/backlog/lag metrics;
- separate exact artifact durability from remote source visibility and require handoff visibility declarations;
- sync promotion-ready state to the actual dev20 S07 cursor so activating R8 cannot regress implementation state.

No Phase00 product/source behavior, native validation result or code-review gate is changed by this health correction.
