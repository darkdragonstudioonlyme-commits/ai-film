# Batch 012 — F05 admission, queue/backpressure and cost controls

T-038:
- admission requires a profile explicitly marked admission_ready with measured VRAM requirement;
- a 32/96 GB GPU does not prove model fit by itself;
- capabilities and exact runtime identity must match;
- quarantined workers are rejected;
- admission reports no throughput unless measured separately.

T-039:
- queue depth and per-project concurrency are bounded;
- enqueue beyond max depth fails with visible backpressure;
- scheduler scans past an incompatible/concurrency-blocked head job, exposing the reason, so a compatible later job can dispatch;
- queued cancellation is explicit and cancelled jobs are not dispatched.

T-040:
- immutable cost receipts include accepted compute, failed compute, rejected takes, storage, transfer, API and other costs;
- duplicate cost ids are rejected;
- budget decision uses total historical spend plus proposed charge;
- current project paid budget remains USD 0 because T-019 is not authorized.
