# Environment Record — DEV-WSL-20260915

```yaml
ENVIRONMENT_ID: DEV-WSL-20260915
ROLE: AUTHORING_AND_REVIEW_ONLY
OBSERVED_DATE: 2026-09-15
SNAPSHOT_DIGEST: 00915ec4684c42f3d0214b7395c20275ffa0133efd0c4ded038a18caec499d0f
DIGEST_ALGORITHM: SHA-256
DIGEST_INPUT: exact UTF-8 bytes of CANONICAL_JSON_PAYLOAD below; the digest field itself is not part of the payload
```

## Canonical JSON payload

```json
{"environment_id":"DEV-WSL-20260915","facts":{"arch":{"status":"OBSERVED","value":"x86_64"},"cpu":{"status":"OBSERVED","value":"AMD Ryzen 9 9950X 16-Core Processor"},"cuda_toolkit_from_current_wsl":{"status":"NOT_CONFIRMED","value":null},"distro":{"status":"OBSERVED","value":"Ubuntu 24.04.4 LTS"},"git":{"status":"OBSERVED","value":"2.43.0"},"gpu_from_current_wsl":{"status":"NOT_VISIBLE","value":null},"home_filesystem_available_at_snapshot":{"status":"OBSERVED_POINT_IN_TIME","value":967905660928},"home_filesystem_bytes":{"status":"OBSERVED","value":1081101176832},"host_alias":{"status":"OBSERVED","value":"DESKTOP-LCISMET"},"kernel":{"status":"OBSERVED","value":"6.18.33.2-microsoft-standard-WSL2"},"logical_cpu_visible":{"status":"OBSERVED","value":24},"memory_available_at_snapshot":{"status":"OBSERVED_POINT_IN_TIME","value":48830582784},"memory_bytes_visible":{"status":"OBSERVED","value":50513731584},"platform":{"status":"OBSERVED","value":"WSL2"},"python":{"status":"OBSERVED","value":"3.12.3"},"swap_bytes_visible":{"status":"OBSERVED","value":17179869184},"user":{"status":"OBSERVED","value":"dragon"}},"observed_date":"2026-09-15","role":"AUTHORING_AND_REVIEW_ONLY","schema_version":1}
```

## Measurement provenance

- host/user: `hostname`, `whoami`
- distro/kernel/arch: `/etc/os-release`, `uname -r`, `uname -m`
- CPU/visible logical CPUs: `lscpu`, `nproc`
- RAM/swap: `free -b`
- home filesystem: `df -B1 /home/dragon`
- Python/Git: `/usr/bin/python3 --version`, `git --version`
- GPU visibility: `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader` → not available in this WSL context
- CUDA toolkit: `nvcc --version` → not confirmed in this WSL context

Available RAM and available disk are point-in-time observations. `NOT_VISIBLE` does not prove GPU absence. This environment is authoring/review only and is not sufficient for GPU model performance claims.
