from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .cost_ledger import budget_decision
from .launch_gate import digest, validate_launch_authorization


class Flux2CastingError(ValueError):
    pass


MODEL_ID = "flux2-klein-4b"
MODEL_REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    if profile.get("model_id") != MODEL_ID:
        raise Flux2CastingError("unexpected model_id")
    if profile.get("revision") != MODEL_REVISION:
        raise Flux2CastingError("unexpected model revision")
    if profile.get("gpu") != "NVIDIA A40":
        raise Flux2CastingError("profile GPU must be NVIDIA A40")
    if profile.get("dtype") != "bfloat16" or profile.get("mode") != "FULL_GPU":
        raise Flux2CastingError("unsupported dtype/mode")
    if profile.get("width") != 1024 or profile.get("height") != 1024:
        raise Flux2CastingError("casting qualification must remain 1024x1024")
    if profile.get("num_inference_steps") != 4 or float(profile.get("guidance_scale", -1)) != 1.0:
        raise Flux2CastingError("unexpected distilled inference parameters")
    if profile.get("smoke_population") != "FACE_FRONT_BY_CHARACTER_STYLE":
        raise Flux2CastingError("unexpected smoke population")
    if profile.get("smoke_jobs") != 4:
        raise Flux2CastingError("smoke population must contain four jobs")
    if profile.get("execution_authorized_by_profile") is not False:
        raise Flux2CastingError("profile must not grant execution authority")
    if profile.get("runtime_lock_ref")!="model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json":
        raise Flux2CastingError("unexpected runtime lock ref")
    if profile.get("authorization_ref")!="model-evaluations/slice01/launch_authorization.active.json":
        raise Flux2CastingError("unexpected authorization ref")
    return dict(profile)


def select_smoke_jobs(
    jobs: list[dict[str, Any]],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    validate_profile(profile)
    candidates = [
        row for row in jobs
        if row.get("model_id") == MODEL_ID
        and row.get("model_revision") == MODEL_REVISION
    ]
    groups = sorted({
        (row.get("character_id"), row.get("style"))
        for row in candidates
    })
    if any(not character or not style for character, style in groups):
        raise Flux2CastingError("invalid character/style group")
    selected: list[dict[str, Any]] = []
    for character_id, style in groups:
        matches = [
            row for row in candidates
            if row.get("character_id") == character_id
            and row.get("style") == style
            and row.get("slot") == "face_front"
        ]
        if len(matches) != 1:
            raise Flux2CastingError(
                f"expected one face_front job for {character_id}/{style}"
            )
        selected.append(matches[0])
    if len(selected) != int(profile["smoke_jobs"]):
        raise Flux2CastingError(
            f"smoke population size drift: {len(selected)}"
        )
    return selected


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_execution_context(
    root: Path,
    profile: dict[str, Any],
) -> dict[str, Any]:
    validate_profile(profile)
    proposal = load_json(
        root / "model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json"
    )
    rates = load_json(
        root / "model-evaluations/slice01/rate_snapshot_20260925.json"
    )
    authorization = load_json(root / profile["authorization_ref"])
    runtime = load_json(root / profile["runtime_lock_ref"])
    matrix = load_json(root / "model-evaluations/slice01/model_matrix.json")
    worker = load_json(root / "projects/slice01/runtime/worker_runpod_a40.json")
    cost_policy = load_json(root / "projects/slice01/runtime/cost_policy.json")
    ledger = load_json(root / "projects/slice01/runtime/cost_ledger.json")

    if runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME" or runtime.get("execution_ready") is not False:
        raise Flux2CastingError("live runtime lock status mismatch")
    target=runtime.get("target",{})
    if target.get("gpu")!="NVIDIA A40" or target.get("torch")!="2.8.0+cu128" or target.get("torch_cuda")!="12.8":
        raise Flux2CastingError("live runtime identity mismatch")
    packages=runtime.get("packages",{})
    if packages.get("diffusers")!="0.40.0" or packages.get("huggingface-hub")!="1.33.0":
        raise Flux2CastingError("live runtime package drift")
    model_rows=[row for row in matrix.get("models",[]) if row.get("model_id")==MODEL_ID]
    if len(model_rows)!=1:
        raise Flux2CastingError("model matrix identity missing/duplicated")
    model=model_rows[0]
    if not model.get("enabled") or model.get("source_revision")!=MODEL_REVISION or model.get("pin_status")!="PINNED":
        raise Flux2CastingError("model matrix pin drift")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise Flux2CastingError("model upstream license gate drift")
    if model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
        raise Flux2CastingError("model commercial evaluation gate drift")
    if model.get("production_gate")!="PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW":
        raise Flux2CastingError("model production gate drift")
    if model.get("execution_ready") is not False:
        raise Flux2CastingError("model matrix must not grant execution authority")
    if worker.get("provider")!="RunPod" or worker.get("gpu",worker.get("gpu_name")) not in (None,"NVIDIA A40"):
        raise Flux2CastingError("worker provider/GPU drift")
    if worker.get("vram_status")!="MEASURED" or worker.get("quarantined") is not False:
        raise Flux2CastingError("worker is not measured/available")

    if cost_policy.get("authorization_id") != authorization.get("authorization_id"):
        raise Flux2CastingError("cost policy authorization mismatch")
    budget = float(cost_policy["current_authorized_budget_usd"])
    launch = validate_launch_authorization(
        authorization,
        proposal_digest=digest(proposal),
        rate_snapshot=rates,
        requested_gpu=profile["gpu"],
        requested_max_usd=budget,
    )
    if authorization.get("new_resource_creation_authorized") is not False:
        raise Flux2CastingError("runner cannot inherit new-resource authority")
    if authorization.get("publish_authority") is not False:
        raise Flux2CastingError("runner cannot inherit publish authority")

    proposed = round(
        float(launch["rate_usd_per_hour"])
        * float(profile["max_wall_sec"])
        / 3600.0,
        6,
    )
    budget_check = budget_decision(
        ledger,
        budget_usd=budget,
        proposed_charge_usd=proposed,
    )
    if not budget_check["allowed"]:
        raise Flux2CastingError("bounded execution budget is exhausted")
    return {
        "authorization_id": authorization["authorization_id"],
        "gpu": launch["gpu"],
        "rate_usd_per_hour": launch["rate_usd_per_hour"],
        "budget": budget_check,
        "max_wall_sec": profile["max_wall_sec"],
        "runtime_status": runtime["status"],
        "runtime_torch": target["torch"],
        "runtime_torch_cuda": target["torch_cuda"],
        "runtime_diffusers": packages["diffusers"],
        "worker_id": worker["worker_id"],
        "new_resource_creation_authorized": False,
        "publish_authority": False,
    }


def build_output_manifest(
    job: dict[str, Any],
    artifact_path: Path,
    *,
    elapsed_sec: float,
    gpu_peak_memory_mb: float | int | None,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    if job.get("model_id") != MODEL_ID:
        raise Flux2CastingError("manifest job model mismatch")
    if job.get("model_revision") != MODEL_REVISION:
        raise Flux2CastingError("manifest job revision mismatch")
    if not artifact_path.is_file():
        raise Flux2CastingError("artifact file missing")
    artifact_sha = sha256_file(artifact_path)
    body = {
        "schema_version": 1,
        "job_id": job["job_id"],
        "job_digest": job["job_digest"],
        "blind_id": job["blind_id"],
        "asset_id": "asset_flux2_" + artifact_sha[:16],
        "asset_path": str(artifact_path),
        "asset_sha256": artifact_sha,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "seed": int(job["seed"]),
        "elapsed_sec": round(float(elapsed_sec), 6),
        "gpu_peak_memory_mb": (
            None if gpu_peak_memory_mb is None
            else round(float(gpu_peak_memory_mb), 3)
        ),
        "parameters": dict(parameters),
        "production_acceptance": False,
        "selection_authorized": False,
        "publish_authority": False,
    }
    manifest_sha = hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    return {**body, "manifest_sha256": manifest_sha}


def build_smoke_plan(
    root: Path,
    profile: dict[str, Any],
    jobs: list[dict[str, Any]],
) -> dict[str, Any]:
    selected = select_smoke_jobs(jobs, profile)
    context = validate_execution_context(root, profile)
    return {
        "schema_version": 1,
        "status": "READY_FOR_EXPLICIT_RUNNER_EXECUTION",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "job_ids": [row["job_id"] for row in selected],
        "characters": sorted({row["character_id"] for row in selected}),
        "styles": sorted({row["style"] for row in selected}),
        "slot": "face_front",
        "parameters": {
            "width": profile["width"],
            "height": profile["height"],
            "num_inference_steps": profile["num_inference_steps"],
            "guidance_scale": profile["guidance_scale"],
            "dtype": profile["dtype"],
            "mode": profile["mode"],
        },
        "execution_context": context,
        "execution_permitted_by_plan": False,
    }
