# NEXT WORK ITEM — Product v2 batch 015

STATUS: READY
MILESTONE: M2

BATCH:
1. T-047 — implement story beat→shot coverage and runtime reconciliation so every screenplay beat is represented and every shot maps to story intent.
2. T-048 — implement per-shot continuity expectation manifests from the ledger and a diff checker for observed/generated metadata.
3. T-049 — implement EN/ZH/VI subtitle layout and safe-area planning for both 9:16 and 16:9, including line-length/reading-density blockers without rendering.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- story beats and shots cannot drift independently or leave orphan coverage
- continuity expectations are explicit machine data and intentional changes are not mistaken for drift
- subtitle plans expose unsafe/overdense text and aspect-specific layout without claiming visual render validation
- no paid compute or media generation is launched

DO NOT:
- launch/rent GPU
- fabricate observed visual continuity
- claim subtitle visual QC without rendered frames
- publish content
