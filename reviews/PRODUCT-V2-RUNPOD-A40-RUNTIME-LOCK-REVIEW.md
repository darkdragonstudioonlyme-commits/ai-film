# PRODUCT V2 — RunPod A40 runtime lock correction review

VERDICT: PASS FOR MERGE CANDIDATE

Finding:
- RunPod A40 pip resolver rejected the canonical base lock because diffusers==0.40.0 requires huggingface-hub>=1.23.0,<2.0 while the repo pinned huggingface-hub==2.0.0.
- A dry-run with the remaining exact pins selected huggingface_hub==1.33.0.

Correction:
- canonical base lock and requirements pin huggingface-hub==1.33.0;
- historical base torch target 2.14.0 remains a desired base pin and is not falsely claimed as executed;
- a separate RunPod-A40 host lock binds the actual template runtime: Python 3.12.3, Torch 2.8.0+cu128, CUDA 12.8, A40;
- host-specific requirements omit torch because the base image supplies the verified CUDA build;
- worker/prelaunch evidence regenerated with corrected SHA-256 values.

Safety:
- no model inference occurred during resolver qualification;
- live A40 runtime lock remains execution_ready=false;
- model-specific adapter install + VRAM measurements are still required before admission_ready.
