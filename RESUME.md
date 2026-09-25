# AI-FILM — Resume v2

GOAL: ship a measurable 60–90 second vertical slice before adding more infrastructure.
MILESTONE: M2 live model-eval/casting execution on RunPod A40.
CANONICAL_BASE_BEFORE_LIVE_GPU_AUTH: origin/main @ fc2cb236f2430984f93816d40e90a8e064731304.
DONE: T-001..T-004, T-008..T-018, T-020..T-055.
LIVE_GPU: RunPod Pod 0h1twwxqw6yx0k, NVIDIA A40, 46068 MiB, USD 0.49/h, 250 GB container/root disk, Torch 2.8.0+cu128, Python 3.12.3.
AUTHORITY: project owner explicitly authorized maximum USD 60 for T-019 Stage A. Active receipt and live rate/host evidence are hash-bound; no new resource creation or publication authority is granted.
NEXT: T-019 — qualify exact model adapter runtimes, then run fixed casting-reference/image smoke and multilingual voice eval while recording VRAM/time/failure/cost evidence.
READINESS: casting_reference_generation and voice_eval are READY; execution_permitted remains false at the generic DAG layer and model-specific admission remains fail-closed until VRAM/runtime measurements exist.
STORAGE_NOTE: /workspace currently shares the 250 GB root overlay rather than a separate Network Volume; sync evidence/artifacts before Pod termination.
LEGACY_P00: frozen at archive/p00-governance-2026-09-24; scheduled P00 timers disabled/inactive.
SAFETY: hard project cap USD 60; no extra Pod/resource creation, no publish, no destructive cleanup, no real-person voice cloning.
