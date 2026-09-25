# NEXT WORK ITEM — Product v2 batch 011

STATUS: READY
MILESTONE: M2

BATCH:
1. T-035 — compile deterministic ffmpeg render commands from a READY edit plan; blocked plans must not yield executable render commands.
2. T-036 — implement technical media probe/QC for duration, dimensions/aspect, video/audio/subtitle streams and immutable file hash.
3. T-037 — implement delivery package manifests for 9:16/16:9 × EN/ZH/VI outputs with provenance/rights/QC references; package creation must not imply publication.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- edit execution is a deterministic derivative of an accepted edit plan and never bypasses blockers
- rendered media can be technically accepted/rejected from measured metadata
- delivery artifacts are hash-bound and publication remains a separate owner-authorized transition
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- fabricate generated film assets
- publish content
- weaken rights/QC/provenance gates
