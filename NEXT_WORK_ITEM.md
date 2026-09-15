# NEXT WORK ITEM — Resume IMPL-P00-001

```yaml
WORKFLOW_ID: WF-P00-IMPL-DEV18
LANE: IMPLEMENT
STATUS: WIP
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
WORK_ITEM: IMPL-P00-001
TARGET_GATE: CODE_REVIEW_PASS
INPUT_IDENTITY:
  DURABLE_BASE_COMMIT: 64ea95bf10e05e856a009be9204983182f520b45
  DURABLE_BASE_VERSION: 0.1.0.dev17
  WORKTREE: /home/dragon/ai-film-dev/implement
  LOCAL_BRANCH: impl/p00
  WIP_DIRTY: true
GOAL: "Finalize the existing dev18 remediation for CR-P00-012/013 and hand an immutable candidate to independent REVIEW."
SUCCESS_OUTPUT: "Committed + packaged dev18 candidate with exact SHA/digests and REVIEW handoff."
ON_SUCCESS: WF-P00-REVIEW-DEV18
ON_FAIL: WF-P00-IMPL-DEV18
ON_BLOCK: WORKFLOW_ROUTER_BLOCK_PROTOCOL
EXIT_CONDITION: "REVIEW receives exact immutable dev18 candidate; no uncommitted handoff."
```

## Resume, do not restart

Current WIP already changes four files and last full author run reports **756 PASS / 100 static PASS**. A fresh chat must first inspect this WIP and preserve it. Do not reset to dev17 unless evidence proves the WIP is corrupt and the rollback is explicitly documented.

## Exact next steps

1. Fetch canonical `main` and fresh lane refs; read current IMPLEMENT lane state.
2. Verify `/home/dragon/ai-film-dev/implement` is branch `impl/p00`, base ancestry contains `64ea95b...`, and only the documented dev18 WIP changes are present.
3. Review the WIP diff specifically for CR-P00-012 collector build/contract binding and CR-P00-013 stage-window continuity/controller coverage.
4. Bump/finalize dev18 version + implementation/changelog/remaining/traceability docs as needed.
5. Run targeted harness tests, then full `lane-test.sh implement`.
6. Write tracked final evidence; secret scan; change inventory/diff audit.
7. Commit exact source candidate. Package **from that commit**, not from a mutable working tree.
8. Verify package manifest/hash; persist exact artifact identity.
9. Create immutable IMPLEMENT→REVIEW handoff with commit/package/source/test identities.
10. REVIEW lane checks out detached exact commit, independently reruns tests and former CR-P00-012/013 scenarios, then searches new failures.
11. If REVIEW FAIL: findings route back to IMPLEMENT through `WORKFLOW_ROUTER.md`; do not patch in REVIEW.
12. If delta PASS but `CR-P00-001` remains: continue next roadmap closure node rather than claiming CODE_REVIEW_PASS.

## Forbidden

- discard the current dev18 WIP merely because dev17 is the last durable package;
- review uncommitted dev18 as formal candidate;
- let IMPLEMENT self-close findings;
- let REVIEW patch source;
- change FD/D00/public contracts or lower acceptance;
- treat author/review tests or harness inventory as native validation;
- run native Windows/WSL/LAB/SITE/guest/live-network validation during current authoring.

## If user only says “continue”

Follow this file and `WORKFLOW_ROUTER.md` automatically. Do not ask what task is next unless a persisted blocker explicitly requires user action.
