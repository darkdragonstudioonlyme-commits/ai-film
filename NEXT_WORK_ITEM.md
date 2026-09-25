# NEXT WORK ITEM — Product v2 batch 007

STATUS: READY
MILESTONE: M2

BATCH:
1. T-023 — implement the image-model GPU runner contract for casting jobs, including dry-run environment/model/reference validation and immutable output manifests; do not create a provider resource.
2. T-024 — implement generated casting-asset ingestion that verifies job/output/provenance identities before updating reference slots/reference index.
3. T-025 — implement benchmark result + cost ledger aggregation and a deterministic decision report for later GPU runs.

BLOCKED:
- T-005/T-006 still require actual generated visual assets.
- T-019 paid rental GPU execution requires explicit bounded approval and live provider-rate recheck.

SUCCESS:
- a casting job can be translated into an executable worker request but remains non-executing without a local authorized GPU runtime
- only hash-bound generated assets can populate casting reference slots
- benchmark timing/VRAM/failure/cost data can produce a reproducible comparison report without inventing a winner when evidence is incomplete
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- execute model inference on paid infrastructure
- bypass model/license/runtime gates
- unblind incomplete evaluations
- clone a real person's voice without rights
- publish content
