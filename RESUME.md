# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 live image-model comparison on RunPod A40.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4 — admission-ready resource profile only; no winner/production acceptance.
ZIMAGE_512_QUALIFICATION: PASS — exact job castjob_8e02916e0db64eb6, peak 21,913 MiB, 21.623722s inference, 34.140679s total, USD 0.004647.
ZIMAGE_PROFILE_BOUNDARY: qualification is 512 only; required_vram_gb remains unset and admission_ready=false until the fixed 1024×1024 four-job smoke passes.
COST_LEDGER: estimated canonical execution entries total USD 0.118397; provider accrued billing total is not exposed by MCP.
NEXT: implement/run Z-Image formal 1024 four-job face_front smoke, ingest evidence, then blind-score FLUX2 vs Z-Image without premature winner selection.
STORAGE_NOTE: FLUX2/Z-Image smoke PNGs remain Pod-local; canonical repo stores hashes/evidence, not binary media. Sync assets before Pod termination.
SAFETY: no winner selection, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
