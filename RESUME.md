# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 blind image-model comparison + multilingual voice qualification on RunPod A40.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4; required 20 GiB + 4 GiB reserve; admission-ready resource profile only.
ZIMAGE_FORMAL_1024_SMOKE: PASS 4/4; peak 26,227 MiB; required 26 GiB + 4 GiB reserve; 353.466833s total; USD 0.048111.
IMAGE_MODEL_COMPARISON: 8-sample blind packet READY, scores blank, selection_authorized=false.
COST_LEDGER: estimated canonical execution entries total USD 0.166508; provider accrued billing total is not exposed by MCP.
NEXT: materialize neutral-name blind assets on the Pod for scoring and keep scores blinded until all 8 are complete; in parallel qualify the fixed VoxCPM2 multilingual voice packet if budget/runtime checks pass.
STORAGE_NOTE: FLUX2/Z-Image PNGs remain Pod-local; canonical repo stores hashes/evidence, not binary media. Sync assets before Pod termination.
SAFETY: no image-model winner before complete blind scores, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
