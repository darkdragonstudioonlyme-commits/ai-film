# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 blind image-model comparison + multilingual voice qualification on RunPod A40.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4; required 20 GiB + 4 GiB reserve.
ZIMAGE_FORMAL_1024_SMOKE: PASS 4/4; required 26 GiB + 4 GiB reserve.
IMAGE_MODEL_COMPARISON: 8 neutral Pod-local blind-ID PNG copies verified byte/hash against canonical public packet; scores remain blank; selection_authorized=false.
VOXCPM2_QUALIFICATION: PASS one EN Voice Design sample; 5827 MiB peak, 3.04s audio within 3.5s cue, 31.527109s runner elapsed, USD 0.004291; no reference audio/no cloning; formal packet has 11 remaining samples.
COST_LEDGER: canonical measured-execution estimate USD 0.170799 / USD 60. Provider full accrued bill remains unavailable through MCP; wall-clock Pod compute must still be watched separately.
NEXT: run the remaining 11 fixed VoxCPM2 EN/ZH/VI Voice Design requests without changing seeds/descriptions, aggregate 12 output manifests/cue-fit/VRAM/time/cost, then expose audio for blind scoring. In parallel keep image blind scores sealed until all 8 rows are completed.
STORAGE_NOTE: image PNGs and VoxCPM2 WAV remain Pod-local; canonical repo stores hashes/evidence, not binary media. Sync assets before Pod termination.
SAFETY: no image-model winner before complete blind scores, no voice quality promotion before full packet, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
