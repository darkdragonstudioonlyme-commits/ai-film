# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 owner image scoring complete; multilingual voice quality scoring pending; staged video runtime smoke next.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
OWNER_ACTION: voice scoring pending; image owner score set is complete 8/8 on the owner-specified 0–8 scale.
PAID_RESOURCE: source=projects/slice01/runtime/gpu_session.json | pod=0h1twwxqw6yx0k | state=RUNNING | provider_billed=USD 8.223297/USD 60 | next=batch-orchestrator validation → staged video smoke.
MEDIA_SYNC: source=projects/slice01/runtime/gpu_session.json | 20/20 current-round media synced (8 PNG + 12 WAV) | unsynced=0.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4; required 20 GiB + 4 GiB reserve.
ZIMAGE_FORMAL_1024_SMOKE: PASS 4/4; required 26 GiB + 4 GiB reserve.
IMAGE_MODEL_COMPARISON: owner scores complete; FLUX2 and Z-Image tie at 8/32 each (mean 2/8); all four photoreal samples scored 4/8 and all four stylized_3d samples 0/8; no model winner selected.
VOXCPM2_FORMAL_BATCH: 12/12 PASS_RUNTIME; 10/12 cue-fit; peak 5829 MiB; runner elapsed 784.510539s; execution cost USD 0.106782; quality awaits owner scoring; no reference audio/no cloning.
COST_LEDGER: canonical measured-execution entries total USD 0.273290; provider billed snapshot USD 8.223297 including GPU + disk. Budget guard follows paid/provider spend, not execution time.
NEXT: validate the batch orchestrator idempotently against the 12 existing VoxCPM receipts, then run staged video smoke beginning with the A40-fit-hypothesis Wan 2.2 TI2V-5B path. Keep 14B/LTX gated until measured admission/runtime evidence exists.
STORAGE_NOTE: current 8 image PNG + 12 VoxCPM2 WAV are synced off the Pod and hash-verified. Pod container disk still has no separate network volume, so future generated media must also be synced before termination.
SAFETY: no image-model winner from the tied owner scores, no voice quality promotion before owner scoring, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
