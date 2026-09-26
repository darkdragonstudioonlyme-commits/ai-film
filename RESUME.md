# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 voice quality scoring + M4 balanced motion owner scoring pending; Wan2.2 runtime admitted.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
OWNER_ACTION: score 12 VoxCPM2 samples and 2 balanced Wan motion clips when presented.
PAID_RESOURCE: source=projects/slice01/runtime/gpu_session.json | pod=0h1twwxqw6yx0k | state=RUNNING_IDLE | provider_billed=USD 9.272200/USD 60 | no GPU batch queued.
MEDIA_SYNC: source=projects/slice01/runtime/gpu_session.json | 25/25 tracked media synced (10 PNG + 12 WAV + 3 MP4) | unsynced=0.
WORLD_PROFILES: READY — reusable presets/validation for Tang Chang'an, Ming Jiangnan, Victorian London, Belle Époque Paris and contemporary Berlin; casting identity remains independent from world/period constraints.
WAN22_BALANCED_MOTION: PASS runtime 2/2 at 25f/8-step, 704x1280@24fps; total 536.179733s; peak 31249 MiB; execution USD 0.072980; both clips synced; owner quality scoring pending; both show pseudo-text on name badge.
WAN22_TI2V_SMOKE: PASS runtime admission; 17 frames/5 steps, peak 31,883 MiB, elapsed 266.384005s, H.264 960x928 @24fps, 0.708333s, execution cost USD 0.036258; quality NOT_EVALUATED.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4; required 20 GiB + 4 GiB reserve.
ZIMAGE_FORMAL_1024_SMOKE: PASS 4/4; required 26 GiB + 4 GiB reserve.
IMAGE_MODEL_COMPARISON: owner scores complete; FLUX2 and Z-Image tie at 8/32 each (mean 2/8); all four photoreal samples scored 4/8 and all four stylized_3d samples 0/8; no model winner selected.
VOXCPM2_FORMAL_BATCH: 12/12 PASS_RUNTIME; 10/12 cue-fit; peak 5829 MiB; runner elapsed 784.510539s; execution cost USD 0.106782; quality awaits owner scoring; no reference audio/no cloning.
COST_LEDGER: canonical measured-execution entries total USD 0.382528; provider billed snapshot USD 9.272200 including GPU + disk. Budget guard follows paid/provider spend.
NEXT: owner score the 2 Wan motion clips and 12 VoxCPM2 samples; then promote only scored media into the first multi-shot quality benchmark. Keep 14B/LTX gated.
STORAGE_NOTE: 10 image PNG + 12 VoxCPM2 WAV + 3 Wan MP4 are synced off the Pod and hash-verified; container disk has no separate network volume.
SAFETY: no image-model winner from the tied owner scores, no voice quality promotion before owner scoring, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
