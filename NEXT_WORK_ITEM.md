# NEXT WORK ITEM — Product v2 batch 013

STATUS: READY
MILESTONE: M2

BATCH:
1. T-041 — implement per-language lip-sync request planning that only includes dialogue shots explicitly marked mouth-visible and binds exact video/audio identities when available.
2. T-042 — implement structured ambience/SFX/music cue sheet with timeline bounds and rights/provenance placeholders; no music generation.
3. T-043 — implement deterministic audio-mix plan for dialogue + ambience + SFX + music with cue timing and target output identity; no ffmpeg execution.

DEFERRED:
- T-019 paid rental GPU benchmark remains BLOCKED pending explicit bounded approval.

SUCCESS:
- lip-sync is selective rather than applied to every shot
- audio cues cannot exceed the 75s timeline or masquerade as rights-cleared assets
- mix plan exposes missing assets/rights as blockers and does not execute tools
- no paid compute is launched

DO NOT:
- launch/rent GPU
- generate or clone voices/music
- assume music/SFX rights
- publish content
