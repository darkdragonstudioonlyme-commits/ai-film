# AI-FILM-SERVER — Server Environment and Benchmark Identity

## Purpose

Environment facts are evidence. Performance/model conclusions bind exact immutable environment records.

## Current development environment pointer

```yaml
ENVIRONMENT_ID: DEV-WSL-20260915
RECORD: environments/ENV-DEV-WSL-20260915.md
SNAPSHOT_DIGEST: 00915ec4684c42f3d0214b7395c20275ffa0133efd0c4ded038a18caec499d0f
ROLE: AUTHORING_AND_REVIEW_ONLY
GPU_PERFORMANCE_ELIGIBLE: false
```

Exact measured facts/provenance live in the immutable record, not duplicated here.

## Fact status vocabulary

- `OBSERVED` — measured in that environment.
- `OBSERVED_POINT_IN_TIME` — volatile measurement captured at snapshot time.
- `NOT_VISIBLE` — current measurement interface did not expose the fact; not evidence of absence.
- `NOT_CONFIRMED` — a requested tool/runtime could not be confirmed.
- `UNKNOWN` — not measured.
- `REQUIRES_SEPARATE_MEASUREMENT` — dependent claims are blocked until measured.

## Model-evaluation environment requirements

Before model comparison, create/reuse an immutable `environments/ENV-*.md` containing the relevant OS/kernel, CPU/visible cores, RAM, GPU/count/VRAM/driver, CUDA/runtime/framework, attention/runtime stack, storage class, resource limits, background load and exact canonical-payload digest.

If GPU/VRAM/runtime facts are unavailable, GPU performance comparison is `BLOCKED_ENVIRONMENT`, not estimated.

## Change detection

Material changes in GPU/driver/CUDA/framework, CPU/RAM allocation, WSL/container limits, storage class, inference engine, quantization backend or thermal/power policy require a new environment record. Never overwrite an old record already referenced by evaluation evidence.
