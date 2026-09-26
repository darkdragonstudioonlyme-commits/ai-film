# PRODUCT V2 — Z-Image A40 formal 1024 smoke review

VERDICT: PASS 4/4 FOR RESOURCE ADMISSION; NO MODEL WINNER OR PRODUCTION ACCEPTANCE

Execution:
- RunPod Pod 0h1twwxqw6yx0k / NVIDIA A40
- exact model Tongyi-MAI/Z-Image @ 04cc4abb7c5069926f75c9bfde9ef43d49423021
- fixed population: An/Linh × photoreal/stylized_3d × face_front
- 1024×1024, 50 steps, guidance 4.0, cfg_normalization=false
- canonical negative prompt applied natively for every job
- BF16 FULL_GPU

Results:
- 4 planned / 4 PASS / 0 failed
- load CPU 2.318896s; transfer CUDA 4.13009s
- per-job elapsed: 85.740514s, 86.439482s, 86.631247s, 86.630369s
- mean 86.360403s; median 86.534926s
- total elapsed 353.466833s
- Torch peak 25,892 MiB; nvidia-smi peak 26,227 MiB
- estimated compute cost USD 0.048111
- canonical ledger after run USD 0.166508 / USD 60 cap
- raw batch evidence SHA-256 ce43303ec34682f843b9b4e16ef39a68d40a51fd9e4ff04bd21fb0fbb2a9b942

Admission:
- required_vram_gb = ceil(26227/1024) = 26 GiB
- fixed operational reserve = 4 GiB
- admission threshold = 30 GiB
- Z-Image resource profile is now admission_ready=true on the measured A40 worker

Boundary:
- all four images remain Pod-local and are not production references
- model_matrix.execution_ready remains false
- selection_authorized=false; production_acceptance=false; publish_authority=false
- formal runner becomes FORMAL_SMOKE_COMPLETE_NO_RERUN to prevent accidental duplicate paid execution
- next gate is complete blind scoring of the 8-sample FLUX2-vs-Z-Image comparison packet

Validation:
- product checker PASS
- focused current-state suite PASS
- full film/product suite 233/233 PASS
- six stale historical test expectations were updated to distinguish immutable 512 qualification evidence from the current 1024 formal-admission state
- blind comparison packet is deterministic, 8 samples, model identity excluded from public packet, score template blank
- Z-Image formal runner now reports FORMAL_SMOKE_COMPLETE_NO_RERUN and refuses accidental paid reruns
