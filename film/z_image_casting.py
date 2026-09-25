from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .cost_ledger import budget_decision
from .launch_gate import digest, validate_launch_authorization


class ZImageCastingError(ValueError):
    pass


MODEL_ID="z-image"
MODEL_REVISION="04cc4abb7c5069926f75c9bfde9ef43d49423021"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_profile(profile: dict[str,Any]) -> dict[str,Any]:
    if profile.get("model_id")!=MODEL_ID:
        raise ZImageCastingError("unexpected model_id")
    if profile.get("revision")!=MODEL_REVISION:
        raise ZImageCastingError("unexpected model revision")
    if profile.get("gpu")!="NVIDIA A40":
        raise ZImageCastingError("profile GPU must be NVIDIA A40")
    if profile.get("dtype")!="bfloat16" or profile.get("mode")!="FULL_GPU":
        raise ZImageCastingError("unsupported dtype/mode")
    if profile.get("width")!=1024 or profile.get("height")!=1024:
        raise ZImageCastingError("casting smoke must remain 1024x1024")
    if profile.get("num_inference_steps")!=50 or float(profile.get("guidance_scale",-1))!=4.0:
        raise ZImageCastingError("unexpected Z-Image inference parameters")
    if profile.get("cfg_normalization") is not False:
        raise ZImageCastingError("cfg_normalization must remain false")
    if profile.get("low_cpu_mem_usage") is not False:
        raise ZImageCastingError("low_cpu_mem_usage must remain false")
    if profile.get("negative_prompt_mode")!="NATIVE_JOB_NEGATIVE_PROMPT":
        raise ZImageCastingError("negative prompt mode drift")
    if profile.get("smoke_population")!="FACE_FRONT_BY_CHARACTER_STYLE":
        raise ZImageCastingError("unexpected smoke population")
    if profile.get("smoke_jobs")!=4:
        raise ZImageCastingError("smoke population must contain four jobs")
    if profile.get("execution_authorized_by_profile") is not False:
        raise ZImageCastingError("profile must not grant execution authority")
    if profile.get("runtime_lock_ref")!="model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json":
        raise ZImageCastingError("unexpected runtime lock ref")
    if profile.get("authorization_ref")!="model-evaluations/slice01/launch_authorization.active.json":
        raise ZImageCastingError("unexpected authorization ref")
    if float(profile.get("max_wall_sec",0))<=0:
        raise ZImageCastingError("max wall must be positive")
    return dict(profile)


def select_smoke_jobs(jobs: list[dict[str,Any]],profile: dict[str,Any]) -> list[dict[str,Any]]:
    validate_profile(profile)
    candidates=[
        row for row in jobs
        if row.get("model_id")==MODEL_ID and row.get("model_revision")==MODEL_REVISION
    ]
    groups=sorted({(row.get("character_id"),row.get("style")) for row in candidates})
    if any(not c or not s for c,s in groups):
        raise ZImageCastingError("invalid character/style group")
    selected=[]
    for character_id,style in groups:
        matches=[
            row for row in candidates
            if row.get("character_id")==character_id
            and row.get("style")==style
            and row.get("slot")=="face_front"
        ]
        if len(matches)!=1:
            raise ZImageCastingError(f"expected one face_front job for {character_id}/{style}")
        if not str(matches[0].get("negative_prompt","")).strip():
            raise ZImageCastingError(f"missing canonical negative prompt for {character_id}/{style}")
        selected.append(matches[0])
    if len(selected)!=int(profile["smoke_jobs"]):
        raise ZImageCastingError(f"smoke population size drift: {len(selected)}")
    return selected


def validate_execution_context(root: Path,profile: dict[str,Any]) -> dict[str,Any]:
    validate_profile(profile)
    proposal=load_json(root/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json")
    rates=load_json(root/"model-evaluations/slice01/rate_snapshot_20260925.json")
    authorization=load_json(root/profile["authorization_ref"])
    runtime=load_json(root/profile["runtime_lock_ref"])
    matrix=load_json(root/"model-evaluations/slice01/model_matrix.json")
    worker=load_json(root/"projects/slice01/runtime/worker_runpod_a40.json")
    cost_policy=load_json(root/"projects/slice01/runtime/cost_policy.json")
    ledger=load_json(root/"projects/slice01/runtime/cost_ledger.json")

    if runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME" or runtime.get("execution_ready") is not False:
        raise ZImageCastingError("live runtime lock status mismatch")
    target=runtime.get("target",{})
    if target.get("gpu")!="NVIDIA A40" or target.get("torch")!="2.8.0+cu128" or target.get("torch_cuda")!="12.8":
        raise ZImageCastingError("live runtime identity mismatch")
    packages=runtime.get("packages",{})
    if packages.get("diffusers")!="0.40.0" or packages.get("huggingface-hub")!="1.33.0":
        raise ZImageCastingError("live runtime package drift")
    zqual=runtime.get("z_image_qualification") or {}
    if zqual.get("status")!="PASS_512_FULL_GPU" or zqual.get("formal_1024_smoke_pending") is not True:
        raise ZImageCastingError("Z-Image 512 qualification gate missing")

    rows=[row for row in matrix.get("models",[]) if row.get("model_id")==MODEL_ID]
    if len(rows)!=1:
        raise ZImageCastingError("model matrix identity missing/duplicated")
    model=rows[0]
    if not model.get("enabled") or model.get("source_revision")!=MODEL_REVISION or model.get("pin_status")!="PINNED":
        raise ZImageCastingError("model matrix pin drift")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise ZImageCastingError("model upstream license gate drift")
    if model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
        raise ZImageCastingError("model commercial evaluation gate drift")
    if model.get("production_gate")!="PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW":
        raise ZImageCastingError("model production gate drift")
    if model.get("execution_ready") is not False:
        raise ZImageCastingError("model matrix must not grant execution authority")

    if worker.get("provider")!="RunPod" or worker.get("vram_status")!="MEASURED" or worker.get("quarantined") is not False:
        raise ZImageCastingError("worker provider/measurement/availability drift")
    zw=(worker.get("qualified_models") or {}).get("z-image",{})
    if zw.get("status")!="PASS_512_QUALIFICATION" or zw.get("formal_1024_smoke_pending") is not True:
        raise ZImageCastingError("worker Z-Image qualification gate missing")
    if zw.get("admission_ready") is not False:
        raise ZImageCastingError("Z-Image must not be admission-ready before formal smoke")

    if cost_policy.get("authorization_id")!=authorization.get("authorization_id"):
        raise ZImageCastingError("cost policy authorization mismatch")
    budget=float(cost_policy["current_authorized_budget_usd"])
    launch=validate_launch_authorization(
        authorization,
        proposal_digest=digest(proposal),
        rate_snapshot=rates,
        requested_gpu=profile["gpu"],
        requested_max_usd=budget,
    )
    if authorization.get("new_resource_creation_authorized") is not False:
        raise ZImageCastingError("runner cannot inherit new-resource authority")
    if authorization.get("publish_authority") is not False:
        raise ZImageCastingError("runner cannot inherit publish authority")

    proposed=round(float(launch["rate_usd_per_hour"])*float(profile["max_wall_sec"])/3600.0,6)
    budget_check=budget_decision(ledger,budget_usd=budget,proposed_charge_usd=proposed)
    if not budget_check["allowed"]:
        raise ZImageCastingError("bounded execution budget is exhausted")
    return {
        "authorization_id":authorization["authorization_id"],
        "gpu":launch["gpu"],
        "rate_usd_per_hour":launch["rate_usd_per_hour"],
        "budget":budget_check,
        "max_wall_sec":profile["max_wall_sec"],
        "runtime_status":runtime["status"],
        "runtime_torch":target["torch"],
        "runtime_torch_cuda":target["torch_cuda"],
        "runtime_diffusers":packages["diffusers"],
        "worker_id":worker["worker_id"],
        "qualification_gate":"PASS_512_FULL_GPU",
        "new_resource_creation_authorized":False,
        "publish_authority":False,
    }


def build_output_manifest(
    job: dict[str,Any],
    artifact_path: Path,
    *,
    elapsed_sec: float,
    gpu_peak_memory_mb: float|int|None,
    parameters: dict[str,Any],
) -> dict[str,Any]:
    if job.get("model_id")!=MODEL_ID:
        raise ZImageCastingError("manifest job model mismatch")
    if job.get("model_revision")!=MODEL_REVISION:
        raise ZImageCastingError("manifest job revision mismatch")
    if not artifact_path.is_file():
        raise ZImageCastingError("artifact file missing")
    artifact_sha=sha256_file(artifact_path)
    body={
        "schema_version":1,
        "job_id":job["job_id"],
        "job_digest":job["job_digest"],
        "blind_id":job["blind_id"],
        "asset_id":"asset_zimage_"+artifact_sha[:16],
        "asset_path":str(artifact_path),
        "asset_sha256":artifact_sha,
        "model_id":MODEL_ID,
        "model_revision":MODEL_REVISION,
        "seed":int(job["seed"]),
        "elapsed_sec":round(float(elapsed_sec),6),
        "gpu_peak_memory_mb":None if gpu_peak_memory_mb is None else round(float(gpu_peak_memory_mb),3),
        "negative_prompt_sha256":hashlib.sha256(str(job["negative_prompt"]).encode("utf-8")).hexdigest(),
        "parameters":dict(parameters),
        "production_acceptance":False,
        "selection_authorized":False,
        "publish_authority":False,
    }
    return {**body,"manifest_sha256":hashlib.sha256(canonical_json_bytes(body)).hexdigest()}


def build_smoke_plan(root: Path,profile: dict[str,Any],jobs: list[dict[str,Any]]) -> dict[str,Any]:
    selected=select_smoke_jobs(jobs,profile)
    context=validate_execution_context(root,profile)
    return {
        "schema_version":1,
        "status":"READY_FOR_EXPLICIT_RUNNER_EXECUTION",
        "model_id":MODEL_ID,
        "model_revision":MODEL_REVISION,
        "job_ids":[row["job_id"] for row in selected],
        "characters":sorted({row["character_id"] for row in selected}),
        "styles":sorted({row["style"] for row in selected}),
        "slot":"face_front",
        "parameters":{
            "width":profile["width"],
            "height":profile["height"],
            "num_inference_steps":profile["num_inference_steps"],
            "guidance_scale":profile["guidance_scale"],
            "cfg_normalization":profile["cfg_normalization"],
            "low_cpu_mem_usage":profile["low_cpu_mem_usage"],
            "negative_prompt_mode":profile["negative_prompt_mode"],
            "negative_prompt_applied":True,
            "dtype":profile["dtype"],
            "mode":profile["mode"],
        },
        "execution_context":context,
        "execution_permitted_by_plan":False,
    }
