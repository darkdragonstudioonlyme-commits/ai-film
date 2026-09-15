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

## Dev8 lifecycle lessons

### MEM-20260915-016 — Process terminal is not lifecycle terminal

```yaml
TYPE: LIFECYCLE
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "A successful C3 child process can leave Windows in a pending-reboot state."
EVIDENCE: "Dev8 added post-process pending-reboot classification; 10 targeted lifecycle tests and full 683-test regression passed."
REUSABLE_RULE: "After C3 process completion, read current pending-reboot indicators. If any are true, keep the original durable fence at AWAITING_REBOOT/20; do not advance from exit code alone."
ACTION_TAKEN: "Added native.lifecycle.classify_c3_process_result and wired it into ENABLE_PREREQUISITES/INSTALL_RUNTIME."
```

### MEM-20260915-017 — Reboot resume is a witnessed lifecycle boundary

```yaml
TYPE: RECOVERY
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Reconciliation after a reboot wait must prove the host actually crossed a boot boundary and is no longer pending reboot."
EVIDENCE: "Dev8 requires current host boot witness != the fence witness and requires all observed pending-reboot indicators false before postconditions/affected-resource checks may commit the original step."
REUSABLE_RULE: "A renewed approval, elapsed time or process exit cannot substitute for a changed host boot witness plus cleared pending-reboot state."
ACTION_TAKEN: "Added reboot_resume_boundary and reused it for reboot-origin owner-verification waits."
```

### MEM-20260915-018 — Owner verification wait is not a generic error relabel

```yaml
TYPE: RECOVERY
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "Missing post-C3/OOBE owner evidence is an operator wait, but only when reconciliation already owns an operator-wait fence."
EVIDENCE: "Dev8 RecoveryRunner catches only exit20/AWAITING_OWNER_VERIFICATION from AWAITING_REBOOT, AWAITING_USER_INIT or AWAITING_OWNER_VERIFICATION fences; other errors propagate unchanged."
REUSABLE_RULE: "Never convert an arbitrary UNCERTAIN/failure into owner wait. Retain/relabel only an existing operator-wait fence and never replay the mutation."
ACTION_TAKEN: "Added bounded wait context and owner_wait_can_relabel guard."
```

### MEM-20260915-019 — Engine reboot and planned host-restart test are distinct

```yaml
TYPE: DESIGN
STATUS: ACTIVE
DISCOVERED_IN: {MODE: IMPLEMENTATION, PHASE: "00 — Host / WSL", WORK_ITEM: IMPL-P00-001}
SUMMARY: "The explicit final AWAIT_OWNER_RESTART must not be removed merely because ENABLE_PREREQUISITES/INSTALL_RUNTIME required an earlier reboot."
EVIDENCE: "Design V2/T00-05 requires one owner-planned host restart with sentinel/content and affected-resource checks; ENGINE/reboot is separately required to establish engine/runtime post-state before fresh inventory/next planning."
REUSABLE_RULE: "Do not deduplicate lifecycle operations solely by action name. Preserve reviewed semantic boundaries unless a formal design change is approved."
ACTION_TAKEN: "Dev8 keeps plan operations unchanged and only hardens wait/resume semantics."
```

## Future-chat usage

1. Read `PROJECT_STATE.md` and `NEXT_WORK_ITEM.md` first.
2. Scan this index for lessons relevant to the active increment.
3. Read `WORKSPACE_WSL.md` for Desktop Commander/WSL operation.
4. Use Git history/archive pointers for older entry detail when needed.
5. Add/supersede entries automatically at every meaningful increment.
