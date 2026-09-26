# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 voice quality scoring remains; M4 Wan2.2 TI2V-5B runtime admission smoke passed.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
OWNER_ACTION: score the 12 VoxCPM2 samples when presented; image owner score set is complete 8/8.
PAID_RESOURCE: source=projects/slice01/runtime/gpu_session.json | pod=0h1twwxqw6yx0k | state=RUNNING | provider_billed=USD 8.748000/USD 60 | batch=idle after synced Wan smoke.
MEDIA_SYNC: source=projects/slice01/runtime/gpu_session.json | 21/21 current-round media synced (8 PNG + 12 WAV + 1 MP4) | unsynced=0.
WORLD_PROFILES: READY — reusable presets/validation for Tang Chang'an, Ming Jiangnan, Victorian London, Belle Époque Paris and contemporary Berlin; casting identity remains independent from world/period constraints.
WAN22_TI2V_SMOKE: PASS runtime admission; 17 frames/5 steps, peak 31,883 MiB, elapsed 266.384005s, H.264 960x928 @24fps, 0.708333s, execution cost USD 0.036258; quality NOT_EVALUATED.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4; required 20 GiB + 4 GiB reserve.
ZIMAGE_FORMAL_1024_SMOKE: PASS 4/4; required 26 GiB + 4 GiB reserve.
IMAGE_MODEL_COMPARISON: owner scores complete; FLUX2 and Z-Image tie at 8/32 each (mean 2/8); all four photoreal samples scored 4/8 and all four stylized_3d samples 0/8; no model winner selected.
VOXCPM2_FORMAL_BATCH: 12/12 PASS_RUNTIME; 10/12 cue-fit; peak 5829 MiB; runner elapsed 784.510539s; execution cost USD 0.106782; quality awaits owner scoring; no reference audio/no cloning.
COST_LEDGER: canonical measured-execution entries total USD 0.309548; provider billed snapshot USD 8.748000 including GPU + disk. Budget guard follows paid/provider spend, not execution time.
NEXT: present VoxCPM2 audio for owner scoring; then build the first quality video benchmark batch on the admitted Wan2.2 TI2V-5B path. Keep 14B/LTX gated until measured admission/runtime evidence exists.
STORAGE_NOTE: current 8 image PNG + 12 VoxCPM2 WAV + Wan smoke MP4 are synced off the Pod and hash-verified. Pod container disk still has no separate network volume.
SAFETY: no image-model winner from the tied owner scores, no voice quality promotion before owner scoring, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
