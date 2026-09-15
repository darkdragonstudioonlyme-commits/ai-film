# AI-FILM-SERVER — Server Environment and Benchmark Identity

## Purpose

Environment facts are evidence, not background prose. Performance/model conclusions are valid only for a known environment identity.

## Current prepared WSL development snapshot

Snapshot time: 2026-09-15 (project local date).

Snapshot digest (canonical sorted JSON of the YAML fact values below):

`b6873887b10300ea04c9356d8b1d3e02c335da624188274be245ec2ee0c32ca5`

```yaml
ENVIRONMENT_ID: DEV-WSL-20260915
ROLE: AUTHORING_AND_REVIEW_ONLY
HOST_ALIAS: DESKTOP-LCISMET
USER: dragon
PLATFORM: WSL2
DISTRO: Ubuntu 24.04.4 LTS
KERNEL: 6.18.33.2-microsoft-standard-WSL2
ARCH: x86_64
CPU: AMD Ryzen 9 9950X 16-Core Processor
LOGICAL_CPU_VISIBLE: 24
MEMORY_BYTES_VISIBLE: 50513731584
MEMORY_AVAILABLE_AT_SNAPSHOT: 48830582784
SWAP_BYTES_VISIBLE: 17179869184
HOME_FILESYSTEM_BYTES: 1081101176832
HOME_FILESYSTEM_AVAILABLE_AT_SNAPSHOT: 967905660928
PYTHON: 3.12.3
GIT: 2.43.0
GPU_FROM_CURRENT_WSL: NOT_VISIBLE
CUDA_TOOLKIT_FROM_CURRENT_WSL: NOT_CONFIRMED
SNAPSHOT_DIGEST: b6873887b10300ea04c9356d8b1d3e02c335da624188274be245ec2ee0c32ca5
```

### Measurement provenance

| Fact | Measurement source | Status |
|---|---|---|
| host/user | `hostname`, `whoami` | OBSERVED |
| distro/kernel/arch | `/etc/os-release`, `uname -r`, `uname -m` | OBSERVED |
| CPU/core visibility | `lscpu`, `nproc` | OBSERVED |
| RAM/swap | `free -b` | OBSERVED_POINT_IN_TIME |
| home filesystem | `df -B1 /home/dragon` | OBSERVED_POINT_IN_TIME |
| Python/Git | `/usr/bin/python3 --version`, `git --version` | OBSERVED |
| GPU | `nvidia-smi --query-gpu=...` | NOT_VISIBLE |
| CUDA toolkit | `nvcc --version` | NOT_CONFIRMED |

Available-memory and available-disk values are **point-in-time**, not stable capacity guarantees. Benchmark runs capture their own start/end availability and background-load context.

`NOT_VISIBLE` is not evidence of GPU absence. It means this execution context did not expose a trustworthy GPU/CUDA measurement.

## Fact status vocabulary

- `OBSERVED`: measured in this environment with a named command/tool.
- `NOT_VISIBLE`: measurement interface unavailable from the current context.
- `UNKNOWN`: not measured.
- `REQUIRES_SEPARATE_MEASUREMENT`: must be captured from the actual target execution environment before a dependent claim.

Never infer hardware from earlier chats, product names or expected configuration.

## Model-evaluation environment snapshot

Before model comparison/benchmarking, create a new immutable environment record containing at least:

```yaml
EVAL_ENV_ID:
TIMESTAMP:
OS_AND_KERNEL:
CPU_MODEL_AND_VISIBLE_CORES:
RAM_TOTAL_AND_AVAILABLE:
GPU_MODEL_COUNT:
VRAM_PER_GPU:
GPU_DRIVER:
CUDA_RUNTIME_TOOLKIT:
PYTORCH_OR_FRAMEWORK:
ATTENTION_KERNELS:
MODEL_RUNTIME:
DISK_MODEL_OR_CLASS:
MODEL_STORAGE_PATH_CLASS:
POWER_LIMITS_IF_RELEVANT:
WSL_OR_CONTAINER_LIMITS:
BACKGROUND_LOAD_NOTES:
ENVIRONMENT_DIGEST:
```

If GPU/VRAM/runtime facts are unavailable, GPU performance comparison is `BLOCKED_ENVIRONMENT`, not estimated.

## Change detection

Create a new environment ID when material benchmark inputs change: GPU/driver/CUDA/framework, CPU/RAM allocation, WSL/container resource limits, storage class, inference engine, quantization backend or thermal/power policy.

Do not overwrite old benchmark environment facts; model results refer to their original environment ID.

## Snapshot digest procedure

Canonicalize the fact map using sorted JSON keys and compact separators, excluding prose/Markdown formatting. SHA-256 of those canonical bytes is `SNAPSHOT_DIGEST`. Model-evaluation results reference the environment ID plus digest; any changed material fact creates a new environment record/digest.
