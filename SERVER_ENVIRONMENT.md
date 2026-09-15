# AI-FILM-SERVER — Server / Development Environment and Model-Evaluation Readiness

## Classification

This file records **observed development-server facts**, not Phase00 native validation and not a claim that a model benchmark environment is ready.

```yaml
OBSERVED_AT: 2026-09-15T05:51:38.012719+00:00
ENVIRONMENT_CLASS: WSL_DEVELOPMENT_AUTHORING
DEV_AUTHOR_READY: true
NATIVE_WINDOWS_VALIDATION_READY: false
MODEL_EVALUATION_READY: false
GPU_STATUS: DXG_DEVICE_PRESENT_BUT_NVIDIA_SMI_NOT_OBSERVED
ENVIRONMENT_FINGERPRINT: fde8230f226af7bdd2492144131d3e6f54aa2ac139927ae2751e77553437e7f8
```

## Observed WSL environment

| Field | Observation |
|---|---|
| Machine name | `DESKTOP-LCISMET` |
| WSL | WSL2 kernel `6.18.33.2-microsoft-standard-WSL2` |
| Distro | Ubuntu 24.04.4 LTS |
| Architecture | x86_64 |
| Visible CPU allocation | 24 logical CPUs |
| Reported CPU model | AMD Ryzen 9 9950X 16-Core Processor |
| WSL-visible RAM | 50,513,731,584 bytes |
| `/home/dragon` filesystem | 1,081,101,176,832 bytes total; ~968,675,287,040 bytes free at observation |
| `/dev/dxg` | present |
| `nvidia-smi` | not available/observable in current WSL PATH/runtime |
| System Python | 3.12.3 |
| Project venv Python | 3.12.3 |
| Project venv pip | missing |
| Git | 2.43.0 |
| GCC | `/usr/bin/gcc` |
| ffmpeg/docker/podman/git-lfs/uv/cmake | not observed in PATH |
| ambient `pip3` | `/home/dragon/arb/.venv/bin/pip3` — unrelated environment; forbidden as implicit project tool |

Do not infer physical host core count from WSL-visible logical CPUs. Do not infer “no GPU” from missing `nvidia-smi`; GPU capability is **not yet established**.

## Tool provenance rule

A tool is usable for project testing/benchmarking only when its executable path and owning environment are explicit. Ambient PATH resolution from another project is not authority. This is especially important for Python/pip, CUDA tooling, ffmpeg and model runtimes.

## Environment freshness

Refresh the environment snapshot:

- before each model-evaluation campaign;
- after WSL resource/config changes;
- after GPU/driver/CUDA/runtime changes;
- after storage/memory topology changes;
- after changing the Python/model environment;
- when a benchmark result appears inconsistent with prior runs.

The canonical capture script is `tools/capture_server_environment.py`; its JSON output/fingerprint is evidence for environment identity.

## Model-evaluation readiness gate

Before comparing models, establish and persist:

```yaml
ENVIRONMENT_FINGERPRINT:
GPU_NAME:
GPU_VRAM_BYTES:
GPU_DRIVER:
CUDA_RUNTIME:
PYTORCH_VERSION:
MODEL_RUNTIME:
FFMPEG_VERSION:
MODEL_ID_AND_HASH:
PRECISION:
INPUT_PROFILE:
SEED:
RESOLUTION:
FRAMES_OR_DURATION:
FPS:
BATCH_AND_CONCURRENCY:
WARMUP_POLICY:
```

A benchmark must additionally record wall time, throughput, peak RAM, peak VRAM, output artifacts and quality metrics. Results from different environment fingerprints are not directly comparable unless the comparison explicitly controls the difference.

Current status is `MODEL_EVALUATION_READY=false` because GPU/runtime identity is not yet established in this environment.
