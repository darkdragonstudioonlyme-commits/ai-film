# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 live image-model evaluation on RunPod A40.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h.
AUTHORITY: maximum USD 60; existing A40 Pod only; no new resource or publication authority.
FLUX2_512_QUALIFICATION: PASS — peak 16,577 MiB, 1.285966s inference, USD 0.00138.
FLUX2_FORMAL_1024_SMOKE: PASS 4/4 — max nvidia-smi 20,415 MiB, max torch reserved 20,080 MiB, mean 2.366221s/job, 15.430117s total, USD 0.0021.
FLUX2_ADMISSION: READY for measured 1024 smoke scope with required_vram_gb=20.0 and vram_reserve_gb=4.0; model_matrix execution_ready remains false and no winner is selected.
COST_LEDGER: estimated total USD 0.11375; provider accrued billing total is not exposed by MCP.
VALIDATOR_FINDING: pre-run model-dir validator undercounted the text encoder/tokenizer set; validator now binds all 18 required diffusers files / 15,980,131,745 bytes / 14.882657 GiB. No rerun was needed because inference already loaded those files successfully; post-run directory revalidation passed.
NEXT: qualify exact pinned Z-Image on the same A40 and fixed face_front population before blind scoring.
STORAGE_NOTE: smoke PNGs remain Pod-local; canonical repo stores hashes/evidence, not binary media. Sync assets before Pod termination.
SAFETY: no winner selection, no production acceptance, no publish, no extra resource creation, hard cap USD 60.
