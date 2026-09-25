# NEXT WORK ITEM — Product v2 batch 006

STATUS: READY
MILESTONE: M2

BATCH:
1. T-020 — compile deterministic casting-reference generation jobs from the 16-slot An/Linh contract for active image candidates; no image generation.
2. T-021 — implement blind-score ingestion/ranking for casting/model evaluation; keep model/character private mapping sealed until scoring completeness checks pass.
3. T-022 — implement VoxCPM2 Voice Design runner request/output manifest contract plus score ingestion; no synthesis/model execution.

BLOCKED:
- T-005/T-006 require generated visual assets.
- T-019 paid rental GPU execution requires explicit bounded approval and live provider-rate recheck.

SUCCESS:
- casting jobs bind exact character/style/slot/model/prompt/seed provenance
- incomplete/tampered blind score sets fail closed before unblinding/ranking
- VoxCPM2 requests bind exact model revision/package, voice group, text, seed and no-reference-audio policy
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- execute model inference
- enable Qwen-Image-2.1 for commercial production without separate license
- treat LatentSync OpenRAIL++ as automatically commercially cleared
- clone a real person's voice without rights
- publish content
