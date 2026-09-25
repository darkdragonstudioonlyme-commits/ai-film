# NEXT WORK ITEM — Product v2 batch 010

STATUS: READY
MILESTONE: M2

BATCH:
1. T-032 — implement production project/scene/shot/take state transitions and immutable selected-take revisions with stale-revision fencing.
2. T-033 — implement normalized logical generation key, attempt lifecycle, retry/cancel and UNKNOWN_OUTCOME reconciliation guards.
3. T-034 — implement deterministic edit timeline compiler that binds selected takes, timing, dialogue/audio and subtitle tracks without requiring final GPU media.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- stale workers/selections cannot overwrite newer shot revision
- retry cannot silently resubmit UNKNOWN_OUTCOME or exceed attempt/cost ceilings
- selected takes compile into a deterministic 75s edit plan with explicit missing-media blockers
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- publish content
- weaken rights/QC/provenance gates
- create fake generated media
