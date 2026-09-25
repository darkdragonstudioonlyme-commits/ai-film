# NEXT WORK ITEM — Product v2 batch 008

STATUS: READY
MILESTONE: M2

BATCH:
1. T-026 — build the authorization receipt schema + live provider-rate recheck gate required before T-019; do not launch any resource.
2. T-027 — build a synthetic casting-output fixture pack that exercises worker output → provenance ingestion → blind asset binding → score gate without model inference.
3. T-028 — build stage-specific benchmark/cost decision-report templates and import paths for later real GPU runs.

BLOCKED:
- T-019 paid rental GPU execution remains blocked until explicit bounded approval.
- T-005/T-006 still require actual generated visual assets.

SUCCESS:
- paid launch cannot proceed without a hash-bound explicit authorization receipt and current rate check
- casting ingestion/scoring path is proven end-to-end on synthetic assets without fake production acceptance
- decision reports can ingest later image/video/voice run data without inventing winners when evidence is incomplete
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- execute model inference
- treat synthetic fixtures as real casting assets
- bypass licensing/runtime/reference gates
- publish content
