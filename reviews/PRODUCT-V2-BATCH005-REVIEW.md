# PRODUCT V2 BATCH 005 REVIEW — 2026-09-25

STATUS: PASS after local contract/unit/integration verification.

Scope:
- T-016 deterministic visual-model prelaunch bundle, no provider action.
- T-017 casting reference manifest + blind acceptance packet, no generated assets.
- T-018 VoxCPM2 EN/ZH/VI Voice Design packet, no synthesis and no reference audio.

Findings/decisions:
- VoxCPM2 package pinned to voxcpm==2.0.3; upstream supports Voice Design without reference audio and native 48 kHz.
- Prelaunch bundle covers exactly the five enabled visual/video candidates and preserves exact model/prompt/seed/reference identity; execution_ready/provider_resource_created remain false.
- Casting embedding absolute threshold intentionally remains uncalibrated until an embedding model and accepted reference population exist; human provisional rubric is 4/5 with zero severe tags.
- VoxCPM2 uses stable per-character seed/description across EN/ZH/VI for cross-language comparison and explicitly forbids cloning in this packet.
- No paid resource, image model or VoxCPM2 inference was executed.
