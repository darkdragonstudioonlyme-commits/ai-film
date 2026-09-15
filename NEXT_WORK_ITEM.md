# NEXT WORK ITEM — IMPL-P00-001 after dev8 CODE_REVIEW FAIL

```yaml
WORK_ITEM_ID: IMPL-P00-001
MODE: IMPLEMENTATION
PHASE: "00 — Host / WSL"
STATUS: IN_PROGRESS
CURRENT_DELIVERY: PARTIAL_SOURCE_DROP_DEV8
LAST_CODE_REVIEW: CODE-REVIEW-P00-001 / FAIL
TARGET_GATE: CODE_REVIEW_PASS
MODE_TRANSITION_NOW: NONE
OPEN_REVIEW_FINDINGS: CR-P00-001…004
ACTIVE_SOURCE: /home/dragon/ai-film-dev/source-dev8
```

## Exact recovery anchor

```yaml
PACKAGE: IMPL-P00-001_IMPLEMENTATION_PACKAGE_V8.zip
SIZE_BYTES: 1091121
SHA256: d4e6b67eebd40fbc173f85205792499021cf6eea9b82309e54c2a76a9a9e3cb5
DRIVE_FILE_ID: 125T2wVf0CVkcmQND0PSmF3HHvXh8AgxD
LOCAL_BASELINE_COMMIT: c44c2f87084f8082ce29af5935c6b47d03f7b96c
```

Author baseline remains **683 PASS / 92 static PASS**. Native Windows/WSL/LAB/SITE remain NOT_RUN.

## First integration — close review findings before new evidence scope

1. **CR-P00-002 / HIGH — renewed authority before durable owner-wait relabel**
   - In `RecoveryRunner`, re-authorize immediately before persisting `AWAITING_OWNER_VERIFICATION` after postcondition observation.
   - Re-check exact opening fence/request identity and authority generation.
   - Add negative tests for approval expiry, authority rollback, actor drift and recovery-request drift after observation but before relabel.

2. **CR-P00-003 / HIGH — persist actual wait cause**
   - When SessionRunner receives an operator-wait result, persist a bounded wait observation instead of dropping `wait_reason`/normalized lifecycle facts.
   - For reboot waits, retain only safe normalized pending-reboot indicators and required witness/result identity; do not persist raw process output.
   - Add tamper/absence/replay tests showing recovery can distinguish persisted reboot-origin context.

3. **CR-P00-004 / MEDIUM — typed/bounded wait context**
   - Define exact schemas/allowed keys per `AWAITING_REBOOT`, `AWAITING_USER_INIT`, `AWAITING_OWNER_VERIFICATION`.
   - Reject unknown keys and cap canonical serialized size.
   - Prefer digests/references for evidence larger than the minimal wait state.
   - Add oversized/unknown-key/sensitive-shape negative tests.

4. Run targeted review-finding tests, then full `/home/dragon/ai-film-dev/test.sh` regression/static checks.
5. Documentation Sync Gate; update review finding dispositions but do **not** mark `CR-P00-001` closed yet.
6. Package/persist exact next delivery and verify remote state.

## Then — resume remaining implementation

After CR-P00-002…004 are fixed and persisted:

1. prior pre-C3/checkpoint provenance selection + nested cross-stage E00 semantics;
2. incomplete/temp support-bundle publication recovery + remaining E17 recovery integration/applicability;
3. reviewed non-DIRECT transport;
4. causal supported-route/failure controller procedures for all 86 normative T/F/subcases;
5. production-factory integration author tests;
6. full source/harness/docs/test closure.

`CR-P00-001` closes only when `AUTHOR_COMPLETE=true`, full REM scope is closed/managed and `CODE_REVIEW_HANDOFF_READY=true` is justified.

## Review record

Read before touching the findings:

- `reviews/CODE-REVIEW-P00-001_DEV8.md`
- `reviews/CODE-REVIEW-P00-001_DEV8.json`
- `PROJECT_MEMORY.md` entries `MEM-20260915-020…023`

## WSL workflow

```bash
source /home/dragon/ai-film-dev/env.sh
/home/dragon/ai-film-dev/test.sh
```

Use local Git for diff/rollback. Direct WSL push remains unauthenticated; remote state writes use the GitHub connector.

## Forbidden

- Change FD/D00/public/reviewed contracts or lower acceptance.
- Execute Phase00 native Windows/WSL/LAB/SITE/guest/live-network provisioning/validation during authoring.
- Treat process exit, fixture flags, author-test count, envelope labels or timestamps as actual native proof.
- Fix CR-P00-001 by merely changing documentation flags; full source closure is required.
- Store raw/sensitive observations in the new wait context just to satisfy CR-P00-003.
- Delete unresolved journal/fence/read state.
- Self-approve CODE_REVIEW_PASS, qualification or HOST_READY.

## Exit condition

After all remaining source scope is genuinely author-complete and the exact candidate is persisted/reviewable, set `CODE_REVIEW_HANDOFF_READY=true` with evidence and run `CODE-REVIEW-P00-001` again. Until then remain in IMPLEMENTATION.
