# PRODUCT V2 — FLUX.2 klein 512 A40 qualification review

VERDICT: PASS FOR FORMAL 1024 SMOKE; NOT ADMISSION-READY

Observed on the owner-authorized RunPod A40:
- exact revision e7b7dc27f91deacad38e78976d1f2b499d76a294
- canonical job castjob_d3ec86da4ca6b1fc / seed 3555493594
- 512×512, four distilled steps, guidance 1.0, BF16, FULL_GPU
- runtime: Torch 2.8.0+cu128 / CUDA 12.8 / diffusers 0.40.0
- load CPU 5.481112s; transfer to CUDA 3.347752s
- inference 1.285966s; total 10.139162s
- nvidia-smi after load 15,561 MiB; measured peak 16,577 MiB
- output PNG 280,407 bytes, SHA-256 f1af28a78a13be0bc8f3cb82f591f6c2bfa7046658b51b142c67532dc2871bf9
- raw Pod evidence SHA-256 494b833da19cc03b9dc4146f0c74eeab0ed0d2adb1fe7f07c9247348c1bbf7df
- estimated compute cost USD 0.00138

Boundary:
- this measurement is not promoted to required_vram_gb because the formal casting profile is 1024×1024 and contains four jobs;
- admission_ready remains false;
- artifact is smoke evidence only, production_acceptance/selection/publish authority remain false;
- the next valid step is the fixed formal 1024 smoke already defined in flux2_casting_profile.json.
