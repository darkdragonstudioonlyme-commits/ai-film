# NEXT WORK ITEM — Product v2 batch 005

STATUS: READY
MILESTONE: M2

BATCH:
1. T-016 — build stage-specific GPU runner/prelaunch bundle from the pinned runtime/model matrix; validate locally without creating a provider resource.
2. T-017 — define casting reference manifest + blind identity/style acceptance contract for An and Linh; create reference-index schema but no generated images.
3. T-018 — prepare VoxCPM2 EN/ZH/VI fixed voice-eval inputs/scoring contract using synthetic/built-in or non-cloned voices only.

BLOCKED:
- T-019 paid rental GPU execution requires explicit bounded approval and live provider-rate recheck.

SUCCESS:
- each enabled visual model has a deterministic stage-specific runner/install/input contract
- casting reference identities/roles and acceptance measurements are machine-readable before keyframe generation
- multilingual voice packet binds dialogue IDs, languages, target character identity, scoring and rights constraints
- no paid compute is launched

DO_NOT:
- launch/rent GPU
- enable Qwen-Image-2.1 for commercial production without separate license
- treat LatentSync OpenRAIL++ as automatically cleared for commercial use
- clone a real person's voice without rights
- publish content
- resume P00 dev23/prodlike
