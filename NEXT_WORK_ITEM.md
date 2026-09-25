# NEXT WORK ITEM — T-019 RunPod A40 Stage A

STATUS: READY
MILESTONE: M2
TASK: qualify the live A40 runtime and produce the first real model-eval/casting/voice evidence under the bounded USD 60 authority.

LIVE HOST:
- RunPod Pod: 0h1twwxqw6yx0k / hurt_scarlet_marsupial
- GPU: NVIDIA A40 ×1, 46068 MiB measured VRAM
- rate: USD 0.49/h
- Python 3.12.3; Torch 2.8.0+cu128; torch CUDA 12.8
- repo: /workspace/ai-film @ fc2cb236f2430984f93816d40e90a8e064731304
- storage: 250 GB root/container overlay; sync outputs before termination

AUTHORIZATION:
- receipt: model-evaluations/slice01/launch_authorization.active.json
- execution plan: model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json
- maximum total project spend: USD 60
- existing A40 Pod only; creating additional resources is NOT authorized

BATCH:
1. Install/qualify exact adapter runtime for the first enabled image candidate, starting with FLUX.2 klein 4B.
2. Run the fixed minimum smoke population and capture peak VRAM, elapsed time, failures, output SHA-256 and estimated compute cost.
3. Update that model's measured resource profile before broader casting jobs.
4. Qualify Z-Image on the same fixed population and compare evidence without inventing a winner.
5. If image smoke is healthy and budget remains, run the fixed VoxCPM2 multilingual voice-eval packet.

STOP:
- projected total project cost would exceed USD 60
- model/license/runtime identity becomes unclear
- same runtime premise fails twice
- evidence/artifact hashes cannot be preserved

DO NOT:
- create another Pod/GPU resource
- mark a model admission-ready before measured VRAM/runtime evidence
- run Wan 14B merely because the host has 48 GB
- publish content or clone a real person's voice
