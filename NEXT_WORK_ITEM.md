# NEXT WORK ITEM — Product v2 batch 004

STATUS: READY
MILESTONE: M2

BATCH:
1. T-013 — create a reproducible pinned GPU-worker runtime/setup manifest and validate setup logic without creating a GPU instance.
2. T-014 — implement backend adapter contracts for the pinned image/video candidates so benchmark jobs can be translated into exact runner inputs; no model inference yet.
3. T-015 — generate all slice01 EN/VI preset-voice previsualization dialogue clips on CPU and integrate them into the 75s animatic; keep ZH as subtitle-only until VoxCPM2 MODEL-EVAL.

CURRENT_BLOCK:
- no discrete NVIDIA GPU
- paid rental is proposed but not authorized
- keyframe references do not exist yet

SUCCESS:
- GPU worker setup/runtime identity is deterministic and dry-run testable
- adapters preserve job/model/prompt/reference/seed identity and reject missing requirements
- 75s previsualization animatic contains timed EN/VI dialogue tracks with manifests and no voice cloning

DO_NOT:
- launch or rent GPU
- enable Qwen-Image-2.1 for commercial production without a separate commercial license
- clone a real person's voice without rights
- resume P00 dev23/prodlike
- publish content
