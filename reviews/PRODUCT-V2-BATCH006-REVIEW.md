# PRODUCT V2 BATCH 006 REVIEW — casting jobs + blind scoring + VoxCPM2 adapter

VERDICT: PASS
REVIEWER: ChatGPT self-review; GitHub Actions still required before merge.

## Scope
- T-020 deterministic casting-reference generation jobs.
- T-021 fail-closed blind score ingestion and deterministic model/style ranking.
- T-022 VoxCPM2 Voice Design request/output/score contracts.

## Review findings closed
1. Casting scoring initially could conceptually be completed before generated assets were bound. The ingestion CLI now requires complete scores and public asset_id/asset_sha256 before loading the private map.
2. Private blind mapping is deliberately read only after public score completeness passes. This is a process seal, not cryptographic secrecy from repository administrators.
3. VoxCPM2 coverage was extended beyond request compilation: tests now exercise all 12 bound output manifests plus a complete score set through unblinding/ranking.
4. Model execution remains false for all generated casting and VoxCPM2 requests; no paid or local model inference is performed by this batch.

## Verification
- product-v2 checker PASS.
- 54/54 film/product tests PASS.
- Python syntax PASS.
- casting compiler dry-run: 32 jobs = 16 slots × 2 active image models.
- VoxCPM2 compiler dry-run: 12 Voice Design requests, reference_audio count 0.
- git diff --check PASS.

## Remaining block
Generated visual references and VoxCPM2 audio still require actual model execution; paid GPU launch remains T-019 BLOCKED pending explicit bounded approval.
