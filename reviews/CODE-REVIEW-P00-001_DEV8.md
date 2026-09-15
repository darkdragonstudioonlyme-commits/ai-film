# CODE-REVIEW-P00-001 — dev8 early review

```yaml
MODE: CODE_REVIEW
PHASE: "00 — Host / WSL"
WORK_ITEM: CODE-REVIEW-P00-001
TARGET_DELIVERY: 0.1.0.dev8 / PARTIAL_SOURCE_DROP_DEV8
TARGET_PACKAGE_SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
REVIEW_KIND: EARLY_OWNER_REQUESTED_REVIEW
VERDICT: FAIL
CODE_REVIEW_PASS: false
FORMAL_GATE_TRANSITION: NOT_ACTIVATED
SOURCE_MODIFIED_DURING_REVIEW: false
```

## Review discipline

The review followed Blueprint V2 CODE_REVIEW discipline: re-read requirements and exact diff/artifact, searched failure scenarios and negative cases first, treated dev8 as another team's code, and made no code edits.

Independent review rerun from `/home/dragon/ai-film-dev/source-dev8` reproduced:

```text
683 workspace tests PASS
92 static checks PASS
source digest e793fc78d622c987343d1b5e5d3909cb4c19d7b0bcbafbc32909f137a1894c08
test digest   f91b422b6ce4ffeee9fc516bff0dc00c8e4a6216ae98e94b977ac2ef00949021
source Git clean after review run
```

Those results are author/workspace evidence only; they do not offset the findings below.

## Verdict summary

**FAIL.** The exact dev8 candidate is not author-complete and is not eligible for `CODE_REVIEW_PASS`. In addition to the declared incomplete scope, review found two reproducible lifecycle/recovery defects and one robustness gap in the dev8 wait-state implementation.

## Findings

### CR-P00-001 — BLOCKER — Formal review handoff is premature

**Areas:** ARCHITECTURE_COMPLIANCE, CORRECTNESS, TESTABILITY, DEPENDENCIES, NETWORK, ROLLBACK.

**Evidence:** canonical state V16 says `AUTHOR_COMPLETE=false`, `CODE_REVIEW_HANDOFF_READY=false`, `IMPL-REM-01…08` remain open, and the package's `docs/CODE_REVIEW_HANDOFF_DRAFT.md` explicitly says `NOT_READY`. `docs/REMAINING_IMPLEMENTATION.md` still records unfinished prior pre-C3/checkpoint/nested E00 semantics, incomplete/temp publication recovery, non-DIRECT transport, remaining dependency/bootstrap provenance, full causal 86-case controller coverage, and production-factory integration.

**Impact:** a PASS/PASS_WITH_FIXES verdict for the full Phase00 code gate would certify reviewed scope that does not yet exist. Author test count cannot compensate for missing required implementation.

**Required disposition:** return to IMPLEMENTATION for full remaining scope. Re-enter formal CODE_REVIEW only when the implementation exit condition is evidence-backed and `CODE_REVIEW_HANDOFF_READY=true`.

---

### CR-P00-002 — HIGH — Durable owner-wait relabel occurs after observation without renewed authority

**Areas:** SECURITY, ERROR_HANDLING, CONCURRENCY, IDEMPOTENCY.

**Location:** `src/aifilm_p00/recovery.py` around lines 139–150 in dev8.

**Logic:** `RecoveryRunner` calls `self.d.reconcile(...)`. If that observation path raises `20/AWAITING_OWNER_VERIFICATION`, the catch branch immediately calls `c.awaiting('AWAITING_OWNER_VERIFICATION', ...)` and returns. Unlike the successful reconciliation path and PAUSE/CANCEL paths, this branch does **not** call `_reauthorize(...)` before changing the durable fence.

**Executable review evidence:** an ad-hoc review scenario changed the synthetic authority time past approval expiry inside `d.reconcile` and then raised `20/AWAITING_OWNER_VERIFICATION`. Dev8 accepted the durable relabel anyway:

```text
accepted_after_expiry: true
report state: AWAITING_OWNER_VERIFICATION
fence state:  AWAITING_OWNER_VERIFICATION
```

**Impact:** a long-running observation can outlive/revoke the authority that admitted it, yet still mutate persistent coordination state. This contradicts the implementation's own reauthorization discipline and the reviewed resume rule requiring renewed/bound authority after lifecycle waits.

**Required fix:** re-authorize and re-check fence/request identity immediately before durable owner-wait relabel, analogous to the other recovery branches. Add negative tests for approval expiry, authority generation rollback, actor drift and request drift occurring after postcondition observation but before relabel.

---

### CR-P00-003 — HIGH — Actual pending-reboot observation is discarded when the durable wait fence is written

**Areas:** CORRECTNESS, OBSERVABILITY, ERROR_HANDLING, RECOVERY.

**Locations:**

- `src/aifilm_p00/native/lifecycle.py` lines 13–28 creates `wait_reason` and `pending_reboot` from observed facts.
- `src/aifilm_p00/session.py` lines 137–140 detects the waiting state but calls only `c.awaiting(result['state'])`.

**Executable review evidence:** a SessionRunner review scenario returned:

```python
{
  'state': 'AWAITING_REBOOT',
  'exit': 20,
  'wait_reason': 'PENDING_REBOOT_OBSERVED',
  'pending_reboot': {'cbs': True, 'wu': False}
}
```

The resulting durable fence contained `state=AWAITING_REBOOT` but **no `wait_observation` and no persisted pending-reboot facts**.

**Impact:** the controller computes the actual reason for the reboot wait but discards it at the persistence boundary. After controller/host restart, reconciliation sees a derived state without the bounded observation that caused it. That weakens auditability and the reviewed durable intent/result requirement; it also makes later reasoning about reboot-origin waits rely on controller state rather than a persisted actual observation.

**Required fix:** persist a bounded, typed wait observation when entering `AWAITING_REBOOT` / `AWAITING_USER_INIT` / `AWAITING_OWNER_VERIFICATION`, including only safe fields required for recovery (for reboot: reason + normalized pending indicators + relevant result/witness digest). Add positive and tamper/absence tests.

---

### CR-P00-004 — MEDIUM — `Coordinator.awaiting` claims bounded context but accepts arbitrary unbounded dictionaries

**Areas:** RESOURCE_MANAGEMENT, SECURITY, OBSERVABILITY.

**Location:** `src/aifilm_p00/admission.py` around lines 129–135.

**Logic:** when an observation is supplied, the only validation is `type(observation) is dict and bool(observation)`, after which the whole object is deep-copied into the durable fence.

**Impact:** the API can persist arbitrary keys/large raw values into the fixed journal, defeating the intended bounded/sanitized wait-context model and creating avoidable journal-capacity or sensitive-data exposure risk. The journal cap eventually blocks oversized writes, but that is not a schema/privacy boundary.

**Required fix:** define exact wait-observation schemas per wait kind, reject unknown fields, cap serialized size, and store digests/references rather than raw evidence where possible. Add oversized/unknown-key/sensitive-shape negative tests.

## Non-findings / reviewed decisions

- The explicit final `AWAIT_OWNER_RESTART` in ENGINE was **not** flagged as a duplicate-restart defect. Design V2/T00-05 separately requires an owner-planned host restart lifecycle; an engine-required reboot does not silently substitute for that reviewed lifecycle boundary.
- Independent workspace rerun reproduced all 683 author tests and 92 static checks. No source mutation occurred during review.
- No claim is made about native Windows/WSL behavior because those tests remain NOT_RUN.

## Category disposition

| Category | Review result |
|---|---|
| CORRECTNESS | FAIL — CR-P00-001, CR-P00-003 |
| ARCHITECTURE_COMPLIANCE | FAIL — CR-P00-001 |
| SECURITY | FAIL — CR-P00-002; CR-P00-004 |
| ERROR_HANDLING | FAIL — CR-P00-002; CR-P00-003 |
| CONCURRENCY | FAIL/needs fix — authority recheck at durable transition (CR-P00-002) |
| RESOURCE_MANAGEMENT | FAIL/needs fix — unbounded wait context (CR-P00-004) |
| GPU/VRAM | N/A to Phase00 Host/WSL code-review target |
| OOM | No independent blocking finding beyond resource-cap issue CR-P00-004 |
| NETWORK | FAIL completeness — supported non-DIRECT path remains open under CR-P00-001 |
| FILESYSTEM | No new dev8-specific blocker found in this review |
| CONFIG | No new dev8-specific blocker found; terminal/effective semantics still incomplete under CR-P00-001 |
| DEPENDENCIES | FAIL completeness — remaining guest/bootstrap provenance under CR-P00-001 |
| OBSERVABILITY | FAIL — CR-P00-003; CR-P00-004 |
| TESTABILITY | FAIL completeness; missing negative tests for CR-P00-002/003/004 |
| IDEMPOTENCY | Needs fix — durable relabel authority window CR-P00-002 |
| ROLLBACK/RECOVERY | FAIL completeness + CR-P00-003 |

## Required next action

This review was intentionally requested before the implementation handoff gate was ready. The safe project action is therefore:

```text
CODE_REVIEW dev8 → FAIL
→ return to IMPLEMENTATION
→ fix CR-P00-002/003/004 as part of the lifecycle/recovery source
→ finish IMPL-REM-01…08 / IMPL-BLOCK-01…03
→ produce author-complete exact candidate
→ CODE-REVIEW-P00-001 again
```

Do not issue `CODE_REVIEW_PASS`, qualification, validation PASS or HOST_READY from this review.
