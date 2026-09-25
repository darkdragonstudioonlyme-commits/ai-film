# NEXT WORK ITEM — Product v2 batch 017

STATUS: READY
MILESTONE: M2

BATCH:
1. T-053 — implement deterministic portable spec export/import bundle that materializes only package-approved spec files and verifies path/hash identity on import.
2. T-054 — implement project schema compatibility/version checks and explicit upgrade plans for scaffolded projects without mutating silently.
3. T-055 — implement a stage-readiness DAG that derives READY/BLOCKED stages from current project evidence, rights, media and paid-resource gates without executing stages.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- production specs can move between machines without path traversal, generated media, runtime receipts or secrets
- schema upgrades are explicit/dry-run and stale/unsupported versions fail closed
- readiness report identifies the next genuinely runnable stages and blocker dependencies instead of creating governance work
- no paid compute or media generation is launched

DO NOT:
- launch/rent GPU
- auto-execute imported source content
- silently migrate schemas
- copy runtime/generated/secrets into portable bundle
- publish content
