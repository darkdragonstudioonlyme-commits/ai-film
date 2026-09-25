from __future__ import annotations

from typing import Any


class AdmissionError(ValueError):
    pass


def evaluate_admission(
    job_profile: dict[str, Any],
    worker: dict[str, Any],
) -> dict[str, Any]:
    reasons: list[str] = []
    profile_id = job_profile.get("profile_id")
    worker_id = worker.get("worker_id")
    if not profile_id or not worker_id:
        raise AdmissionError("profile_id and worker_id required")

    if not job_profile.get("admission_ready", False):
        reasons.append("PROFILE_NOT_ADMISSION_READY")
    if job_profile.get("vram_status") != "MEASURED":
        reasons.append("VRAM_REQUIREMENT_UNMEASURED")
    required_vram = job_profile.get("required_vram_gb")
    if required_vram is None:
        reasons.append("VRAM_REQUIREMENT_MISSING")
    else:
        try:
            required_vram = float(required_vram)
        except (TypeError, ValueError) as exc:
            raise AdmissionError("invalid required_vram_gb") from exc
        if required_vram <= 0:
            raise AdmissionError("required_vram_gb must be positive")

    if worker.get("quarantined"):
        reasons.append("WORKER_QUARANTINED")
    if worker.get("vram_status") != "MEASURED":
        reasons.append("WORKER_VRAM_UNMEASURED")
    available = worker.get("available_vram_gb")
    if available is None:
        reasons.append("WORKER_AVAILABLE_VRAM_MISSING")
    else:
        try:
            available = float(available)
        except (TypeError, ValueError) as exc:
            raise AdmissionError("invalid worker available_vram_gb") from exc
        reserve = float(job_profile.get("vram_reserve_gb", 0))
        if required_vram is not None and available < required_vram + reserve:
            reasons.append(
                f"INSUFFICIENT_VRAM:{available}<{required_vram + reserve}"
            )

    required_caps = set(job_profile.get("required_capabilities", []))
    worker_caps = set(worker.get("capabilities", []))
    missing_caps = sorted(required_caps - worker_caps)
    if missing_caps:
        reasons.append("MISSING_CAPABILITIES:" + ",".join(missing_caps))

    runtime_id = job_profile.get("required_runtime_id")
    if runtime_id and runtime_id not in set(worker.get("runtime_ids", [])):
        reasons.append("RUNTIME_MISMATCH:" + str(runtime_id))

    return {
        "schema_version": 1,
        "profile_id": profile_id,
        "worker_id": worker_id,
        "admitted": not reasons,
        "reasons": reasons,
        "throughput_claimed": False,
        "measured_throughput": None,
    }
