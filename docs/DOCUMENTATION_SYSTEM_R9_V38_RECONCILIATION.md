# Documentation System R9 — V38 lifecycle measurement reconciliation

## Purpose

V38 reconciles two real post-V37 facts without changing product/native execution: validation evidence head advanced when Phase F was closed, and learning 004 reached its scheduled effectiveness gate. V38 also finalizes learning 005 from transition-only promotion state after completed V37 promotion while preserving its V39 measurement gate.

## Canonical changes

1. State version advances from 37 to 38.
2. Validation evidence head advances from `f98185bab6ad140b930eaaaf1ab3ac35ea1aae7b` to `179c475007802bf61414f043a0cf189b0fdc371a`.
3. Learning 004 candidate effectiveness moves from `PENDING_MEASUREMENT` to `EFFECTIVE` only if the unchanged adversarial suite passes on the exact V38 target.
4. Learning 005 moves from `PASS_ON_FINAL_REVIEW / ACTIVE_ON_PROMOTION` to durable `PASS / ACTIVE` after the completed V37 R5/A5 promotion, but remains `PENDING_MEASUREMENT` until V39.
5. Learning aggregates become pending=1, overdue=0, historical ineffective=3.
6. Product/native state, V02 authority, 86-case inventory and production-like controls remain unchanged.

## Measurement contract for learning 004

The exact V38 target must execute the unchanged 9-case adversarial lifecycle regression after the ambient lifecycle register changes. Each negative fixture must still trigger its intended checker failure class. No checker predicate or adversarial case may be removed or weakened to obtain PASS.

If the exact V38 target or CI fails, learning 004 remains pending or becomes ineffective based on the failure evidence; it must not be marked effective by documentation assertion alone.

## Promotion-state finalization for learning 005

V37 R5/A5 verdicts and post-promotion CI completed successfully. Before V38 predeclares new final-review/final-audit IDs, the prior transition-only state for learning 005 is normalized to durable PASS/ACTIVE while retaining immutable V37 activation evidence. This is lifecycle-state finalization, not an effectiveness measurement. The V39 gate remains intact.

## Native boundary

`RUN-P00-VALIDATION-001` remains BLOCKED at `V02_LAB_EXECUTION_AUTHORITY`; LAB remains unexecuted, all 86 cases remain NOT_RUN, qualification is absent, SITE is unexecuted and HOST_READY is not evaluated. Production-like readiness cannot satisfy V02 `DONE_WHEN`.

## Promotion contract

V38 predeclares R6 detailed review and A6 holistic audit. Both must bind one exact design SHA. Promotion is verdict-only and post-promotion CI is mandatory.
