# PRODUCT V2 — FLUX.2 klein formal 1024 casting smoke review

VERDICT: PASS FOR MEASURED WORKER ADMISSION; NOT MODEL SELECTION OR PRODUCTION ACCEPTANCE

Formal population:
- four deterministic face_front jobs: An/Linh × photoreal/stylized_3d
- exact revision e7b7dc27f91deacad38e78976d1f2b499d76a294
- 1024×1024, four distilled steps, guidance 1.0, BF16 FULL_GPU
- 4/4 PASS

Measurements:
- total elapsed 15.430117s
- per-job elapsed 2.751941, 2.233951, 2.243730, 2.235263s
- mean 2.366221s; median 2.239497s
- max torch reserved 20,080 MiB
- max nvidia-smi 20,415 MiB
- estimated compute cost USD 0.0021
- project ledger total after run USD 0.11375

Admission policy:
- measured peak = 20,415 MiB = 19.936523 GiB
- required_vram_gb = ceil(measured peak GiB) = 20.0
- vram_reserve_gb = 4.0 fixed operational reserve
- admission threshold = 24.0 GiB
- A40 measured available = 44.988281 GiB, so FLUX2 resource profile can become admission_ready=true for the measured 1024 smoke scope.

Validator finding closed:
- the pre-run validate_model_dir contract listed only 9 files and undercounted the snapshot as 7.386031 GiB.
- the actual exact-revision diffusers subset used by inference contains 18 required files / 15,980,131,745 bytes / 14.882657 GiB.
- validator is corrected to bind all 18 files; post-run model directory revalidation passed.
- this did not invalidate the smoke outputs because from_pretrained successfully loaded the missing-listed text-encoder shards/tokenizer support files during the run.

Boundaries:
- all four PNGs remain smoke evidence only and Pod-local pending sync;
- production_acceptance=false, selection_authorized=false, publish_authority=false;
- no model winner is declared; next step is Z-Image qualification on the same population.
