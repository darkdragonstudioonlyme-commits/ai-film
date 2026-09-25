# NEXT WORK ITEM — Product v2 batch 012

STATUS: READY
MILESTONE: M2

BATCH:
1. T-038 — implement capability-based worker admission from exact model/runtime profile and measured/declared VRAM, without claiming throughput.
2. T-039 — implement bounded queue depth, per-project concurrency, visible backpressure and cancellation semantics.
3. T-040 — implement project/job cost ledger and budget enforcement that includes successful, failed, rejected, storage and transfer costs.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- incompatible/insufficient workers are rejected before dispatch
- queue/concurrency limits are deterministic and starvation/backpressure state is visible
- budget guard counts failed/rejected work and non-compute costs, not only accepted GPU seconds
- no GPU throughput claims or paid execution are made

DO NOT:
- launch/rent GPU
- fabricate measured VRAM/throughput
- hide rejected/failed cost
- publish content
