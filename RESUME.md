# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 live model-eval/casting execution on RunPod A40.
CANONICAL_BASE_BEFORE_FLUX2_512_EVIDENCE: origin/main @ 7443351e6cd4416cb67efffa4fb324bcf9577fe5.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h, 250 GB container/root disk, Torch 2.8.0+cu128.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
FLUX2_512_QUALIFICATION: PASS — exact job castjob_d3ec86da4ca6b1fc, 512×512, 4 steps, BF16 full GPU, 16,577 MiB peak, 1.285966s inference, 10.139162s total, USD 0.00138 estimated compute.
PROFILE_BOUNDARY: this is a single 512 qualification only. FLUX2 admission_ready remains false and required_vram_gb remains unset until the fixed 1024×1024 four-job smoke passes.
NEXT: run the canonical formal smoke via tools/run_flux2_casting_batch.py, ingest four-job evidence/cost, then qualify Z-Image on the same population.
STORAGE_NOTE: qualification artifact remains Pod-local; canonical repo stores its SHA/evidence identity, not the PNG binary. Sync all smoke assets before Pod termination.
SAFETY: no winner selection, no production acceptance, no publish, no extra resource creation, hard project cap USD 60.
