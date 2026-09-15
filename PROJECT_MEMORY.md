# AI-FILM-SERVER — PROJECT MEMORY

> Living reusable knowledge. Current truth lives in `PROJECT_STATE.md`; executable next work lives in `NEXT_WORK_ITEM.md`.

## No-silent-knowledge rule

Reusable discoveries, optimizations, tooling limitations, failure patterns, security/test lessons and clarifications must be persisted before the related increment is considered durable. Memory does not approve architecture or pass gates.

Historical detail through checkpoint V15 is preserved in Git history. The V15 living-memory blob is `80db3862014db65d2d5926deb5442de68401b3bd`; the repository also contains `memory/archive/PROJECT_MEMORY_V15.md` as its archive pointer.

## Active Memory Index

| ID | Type | Reusable rule |
|---|---|---|
| MEM-20260915-001 | PROCESS | Separate current state, next work, reusable knowledge and immutable history. |
| MEM-20260915-002 | TOOLING | Exact baselines require byte-preserving transport plus independent identity verification. |
| MEM-20260915-003 | TESTING | Author regression/static checks are not Windows/WSL/LAB/SITE proof. |
| MEM-20260915-004 | PROCESS | An increment is durable only after remote artifact/state verification. |
| MEM-20260915-005 | SECURITY | Secret-scan every public-repo delivery; never persist real credentials/private assets. |
| MEM-20260915-006 | TOOLING | Prefer file-reference/raw-file actions for binary delivery artifacts. |
| MEM-20260915-007 | PROCESS | Hybrid persistence is valid when Git state and exact binary artifact roles are explicit. |
| MEM-20260915-008 | LESSON | Explicit missing state is safer than accepting non-identical bytes. |
| MEM-20260915-009 | TOOLING | If chunking is unavoidable, verify every Git blob SHA individually; prefer file-native transfer. |
| MEM-20260915-010 | TESTING | Respect the package src-layout/official runner; missing `PYTHONPATH=src` is not a source regression. |
| MEM-20260915-011 | SECURITY | Executable trust binds path + exact bytes + policy + pinned handle + witness before resume. |
| MEM-20260915-012 | TOOLING | Use `/home/dragon/ai-film-dev`; verify delivery hash before extraction. |
| MEM-20260915-013 | TOOLING | No-pip venv + `.pth` is acceptable only while project dependencies remain empty. |
| MEM-20260915-014 | PROCESS | Local Git fetch/commit and remote write authentication are separate; avoid hanging interactive helpers. |
| MEM-20260915-015 | TESTING | Save run evidence outside source and restore tracked generated evidence so verification keeps baseline clean. |
| MEM-20260915-016 | LIFECYCLE | Native process completion is not lifecycle completion; observed pending reboot must retain a durable wait. |
| MEM-20260915-017 | RECOVERY | Resume from reboot wait needs a changed boot witness + cleared pending state before the original step can commit. |
| MEM-20260915-018 | PROCESS | Missing owner postcheck is an owner wait only from an existing operator-wait fence; never relabel arbitrary `UNCERTAIN`. |
| MEM-20260915-019 | DESIGN | Keep the reviewed final owner-planned restart; an earlier engine-required reboot does not satisfy T00-05 by itself. |
| MEM-20260915-020 | REVIEW | An early review of an explicitly partial candidate must FAIL; passing tests do not make missing reviewed scope reviewable. |
| MEM-20260915-021 | SECURITY | Any durable recovery-state change after observation needs renewed authority immediately before persistence. |
| MEM-20260915-022 | OBSERVABILITY | If lifecycle classification uses an actual observation, persist a bounded typed representation/digest of that observation; do not retain only the derived state. |
| MEM-20260915-023 | RESOURCE | Durable wait context needs exact schemas and size/privacy bounds; never deep-copy arbitrary observation dictionaries into the journal. |

## Dev8 lifecycle lessons

### MEM-20260915-016 — Process terminal is not lifecycle terminal

A successful C3 child process can leave Windows pending reboot. After C3 process completion, read current pending-reboot indicators and retain `AWAITING_REBOOT/20` when any are true; process exit alone is not lifecycle completion.

### MEM-20260915-017 — Reboot resume is a witnessed lifecycle boundary

Reconciliation after a reboot wait requires current host boot witness != the original fence boot witness and all observed pending-reboot indicators clear before postconditions may commit the step.

### MEM-20260915-018 — Owner verification wait is not a generic error relabel

Missing post-C3/OOBE owner evidence may remain an operator wait only when reconciliation already owns an operator-wait fence. Never convert arbitrary `UNCERTAIN` or assertion failure into owner wait.

### MEM-20260915-019 — Engine reboot and planned host-restart test are distinct

The explicit final `AWAIT_OWNER_RESTART` must not be removed merely because an earlier engine C3 step required reboot. Design V2/T00-05 defines a distinct owner-planned host restart lifecycle boundary.

## CODE_REVIEW dev8 lessons

### MEM-20260915-020 — Passing author tests do not make a partial candidate review-ready

```yaml
TYPE: REVIEW
STATUS: ACTIVE
DISCOVERED_IN: {MODE: CODE_REVIEW, PHASE: "00 — Host / WSL", WORK_ITEM: CODE-REVIEW-P00-001}
SUMMARY: "Dev8 independently reproduced 683 PASS + 92 static, but the full candidate still declared AUTHOR_COMPLETE=false and REM-01…08 open."
EVIDENCE: "CODE-REVIEW-P00-001 dev8 verdict FAIL; CR-P00-001 BLOCKER."
REUSABLE_RULE: "Do not issue PASS/PASS_WITH_FIXES for a full-scope code gate when required reviewed implementation is absent. Test success only evaluates existing code."
ACTION_TAKEN: "Formal CODE_REVIEW_PASS transition was not activated; project returned to IMPLEMENTATION."
```

### MEM-20260915-021 — Re-authorize immediately before persistent recovery-state changes

```yaml
TYPE: SECURITY
STATUS: ACTIVE
DISCOVERED_IN: {MODE: CODE_REVIEW, PHASE: "00 — Host / WSL", WORK_ITEM: CODE-REVIEW-P00-001}
SUMMARY: "A recovery observation can outlive the authority that admitted it; persistent wait-state mutation therefore needs a final authority check."
EVIDENCE: "Review scenario expired synthetic authority inside d.reconcile and raised AWAITING_OWNER_VERIFICATION; dev8 still persisted the relabel because that catch branch skipped _reauthorize. CR-P00-002."
REUSABLE_RULE: "After any potentially long observation/proof read and before changing durable recovery/fence state, revalidate current authority, actor/request identity, generation and fence identity."
ACTION_TAKEN: "Finding recorded; implementation fix required before next formal review."
```

### MEM-20260915-022 — Persist the actual cause of derived lifecycle waits

```yaml
TYPE: OBSERVABILITY
STATUS: ACTIVE
DISCOVERED_IN: {MODE: CODE_REVIEW, PHASE: "00 — Host / WSL", WORK_ITEM: CODE-REVIEW-P00-001}
SUMMARY: "Dev8 computes pending-reboot facts and wait_reason but SessionRunner persists only AWAITING_REBOOT state."
EVIDENCE: "Review scenario returned pending_reboot={cbs:true,wu:false}; the resulting fence had no wait_observation. CR-P00-003."
REUSABLE_RULE: "A durable state derived from an actual observation should retain a safe typed observation/digest sufficient to audit/reconcile the derivation. Do not persist only the conclusion."
ACTION_TAKEN: "Finding recorded; implementation fix required."
```

### MEM-20260915-023 — Durable wait context must be typed and bounded

```yaml
TYPE: RESOURCE
STATUS: ACTIVE
DISCOVERED_IN: {MODE: CODE_REVIEW, PHASE: "00 — Host / WSL", WORK_ITEM: CODE-REVIEW-P00-001}
SUMMARY: "Coordinator.awaiting currently accepts any non-empty dict and deep-copies it into the durable fence."
EVIDENCE: "Static review of admission.py lines 129–135; CR-P00-004."
REUSABLE_RULE: "For journaled wait metadata, define exact allowed keys/types and canonical serialized size limits; keep raw/sensitive evidence behind protected references/digests."
ACTION_TAKEN: "Finding recorded; add schema/size/privacy negative tests during implementation."
```

## Future-chat usage

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Scan this index for lessons relevant to the active increment.
3. Read `reviews/CODE-REVIEW-P00-001_DEV8.md` while CR-P00-001…004 remain open.
4. Read `WORKSPACE_WSL.md` for Desktop Commander/WSL operation.
5. Use Git history/archive pointers for older entry detail when needed.
6. Add/supersede entries automatically at every meaningful increment.
