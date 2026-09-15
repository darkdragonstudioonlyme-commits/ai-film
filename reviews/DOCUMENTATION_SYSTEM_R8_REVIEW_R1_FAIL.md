# Documentation System V2 R8 — Detailed Review R1

```yaml
REVIEW_ID: DOC-V2-R8-REVIEW-001-R1
REVIEW_LANE: lane/docs-v2-r8-review
TARGET_BRANCH: lane/docs-v2-r8-design
TARGET_COMMIT: fc8e20061c65320ac21adf363024921eede570f1
SOURCE_IMPLEMENTATION_MODIFIED: false
VERDICT: FAIL
```

## What passed

The exact remote R8 target passed the portable documentation audit, runtime-state reconciliation and workflow-continuity check. Cold start routes to the active run and S06 packaging. Negative simulations correctly rejected an unknown run, wrong expected IMPLEMENT head, missing `NEXT_WORK_ITEM` workflow field and broken router priority numbering. IMPLEMENT remained clean at dev20 commit `51c9d3f7373a2922c1ea6a3e973d817bb4e16523`; REVIEW remained detached at dev19 `2ac37acdd3f81d3b86d4ffb019689655110a80c2`.

## Finding DOCV2-R8-01 — HIGH — continuity checker is incident-specific

`tools/check_workflow_continuity.py` contains a hard-coded `RUN-P00-CR001-001` condition. A standing continuity checker must validate any future `RUN_ID` from canonical state/lane records; it must not encode the incident that motivated the policy. The holistic audit checker also does not currently include `check_workflow_continuity.py` in its anti-hardcoding scan.

Required correction:
- remove the specific RUN ID from generic checker logic;
- derive and validate `RUN_ID`, owner lane, run-record path, step/current-output identity from current state;
- validate live run-record schema enough to reject duplicate/mismatched workflow/base/current-step identity;
- include the continuity checker in checker-hardcoding audit coverage;
- add negative tests/simulations proving a different syntactically valid future run can be checked from state without source edits.

## Verdict

FAIL. R8 architecture direction is correct and addresses the timeout/duplicate-work failure, but it is not yet sufficiently general to promote. Return to DOC-DESIGN; DOC-AUDIT must not run until a revised exact candidate passes detailed review.
