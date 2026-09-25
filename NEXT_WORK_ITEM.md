# NEXT WORK ITEM — Product v2 batch 014

STATUS: READY
MILESTONE: M2

BATCH:
1. T-044 — implement an executable screenplay/scene schema for slice01 with stable scene/beat/dialogue IDs, runtime estimates and rights/source identity validation.
2. T-045 — implement EN-master localization bundle validation for ZH/VI with stable dialogue IDs, complete language coverage and cue-budget timing-fit checks.
3. T-046 — implement deterministic framing/reframe planning from 9:16 master to 16:9 using per-shot camera/framing intent and safe-area constraints; no rendering.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- story/script data is machine-validatable rather than Markdown-only
- localization cannot silently drop/relabel dialogue or exceed cue timing without a blocker
- 16:9 path preserves shot identity/camera intent and exposes shots requiring rerender rather than pretending crop is always safe
- no paid compute or media generation is launched

DO NOT:
- launch/rent GPU
- fabricate translated timing measurements
- publish content
- treat crop/reframe planning as rendered media
