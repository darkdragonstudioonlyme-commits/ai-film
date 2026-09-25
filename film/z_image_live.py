from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .cost_ledger import budget_decision
from .image_runner import compile_image_worker_request, validate_image_output_manifest
from .launch_gate import digest as launch_digest, validate_launch_authorization


class ZImageQualificationError(ValueError):
    pass


MODEL_ID="z-image"
MODEL_REVISION="04cc4abb7c5069926f75c9bfde9ef43d49423021"
GPU_NAME="NVIDIA A40"
QUALIFICATION_CONFIG={
    "width":512,
    "height":512,
    "num_inference_steps":50,
    "guidance_scale":4.0,
    "cfg_normalization":False,
    "torch_dtype":"bfloat16",
    "low_cpu_mem_usage":False,
    "mode":"FULL_GPU",
}
REQUIRED_MODEL_FILES=(
    "model_index.json",
    "scheduler/scheduler_config.json",
    "text_encoder/config.json",
    "text_encoder/generation_config.json",
    "text_encoder/model-00001-of-00003.safetensors",
    "text_encoder/model-00002-of-00003.safetensors",
    "text_encoder/model-00003-of-00003.safetensors",
    "text_encoder/model.safetensors.index.json",
    "tokenizer/merges.txt",
    "tokenizer/tokenizer.json",
    "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json",
    "transformer/config.json",
    "transformer/diffusion_pytorch_model-00001-of-00002.safetensors",
    "transformer/diffusion_pytorch_model-00002-of-00002.safetensors",
    "transformer/diffusion_pytorch_model.safetensors.index.json",
    "vae/config.json",
    "vae/diffusion_pytorch_model.safetensors",
)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def _matrix_model(matrix: dict[str,Any]) -> dict[str,Any]:
    rows=[row for row in matrix.get("models",[]) if row.get("model_id")==MODEL_ID]
    if len(rows)!=1:
        raise ZImageQualificationError("Z-Image model matrix identity missing/duplicated")
    model=rows[0]
    if not model.get("enabled") or model.get("stage")!="image":
        raise ZImageQualificationError("Z-Image is not enabled image candidate")
    if model.get("pin_status")!="PINNED" or model.get("source_revision")!=MODEL_REVISION:
        raise ZImageQualificationError("Z-Image exact revision pin drift")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise ZImageQualificationError("Z-Image upstream license pin is not cleared")
    if model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
        raise ZImageQualificationError("Z-Image commercial-use status is not permitted")
    if model.get("production_gate")!="PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW":
        raise ZImageQualificationError("Z-Image production gate drift")
    if model.get("execution_ready") is not False:
        raise ZImageQualificationError("model matrix must not grant execution authority")
    return model


def prepare_z_image_qualification(
    *,
    job: dict[str,Any],
    matrix: dict[str,Any],
    base_runtime: dict[str,Any],
    live_runtime: dict[str,Any],
    proposal: dict[str,Any],
    execution_plan: dict[str,Any],
    rate_snapshot: dict[str,Any],
    authorization: dict[str,Any],
    cost_policy: dict[str,Any],
    cost_ledger: dict[str,Any],
    max_runtime_sec: float=1800.0,
) -> dict[str,Any]:
    if max_runtime_sec<=0:
        raise ZImageQualificationError("max_runtime_sec must be positive")
    model=_matrix_model(matrix)
    if job.get("model_id")!=MODEL_ID:
        raise ZImageQualificationError("job is not Z-Image")
    if job.get("model_repo")!=model.get("source_repo") or job.get("model_revision")!=MODEL_REVISION:
        raise ZImageQualificationError("job model source identity drift")

    if live_runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME":
        raise ZImageQualificationError("live A40 runtime lock missing")
    target=live_runtime.get("target",{})
    if target.get("gpu")!=GPU_NAME or target.get("torch")!="2.8.0+cu128" or target.get("torch_cuda")!="12.8":
        raise ZImageQualificationError("live A40 runtime identity mismatch")
    packages=live_runtime.get("packages",{})
    if packages.get("diffusers")!="0.40.0" or packages.get("huggingface-hub")!="1.33.0":
        raise ZImageQualificationError("live runtime package drift")

    launch=validate_launch_authorization(
        authorization,
        proposal_digest=launch_digest(proposal),
        rate_snapshot=rate_snapshot,
        requested_gpu=GPU_NAME,
        requested_max_usd=float(cost_policy["current_authorized_budget_usd"]),
    )
    if execution_plan.get("plan_digest")!=authorization.get("execution_plan_digest"):
        raise ZImageQualificationError("execution plan / authorization digest mismatch")
    if execution_plan.get("pod_id")!=authorization.get("pod_id"):
        raise ZImageQualificationError("execution plan / authorization pod mismatch")
    if execution_plan.get("new_resource_creation_authorized") is not False:
        raise ZImageQualificationError("runner does not accept new-resource authority")
    if authorization.get("publish_authority") is not False:
        raise ZImageQualificationError("runner does not accept publish authority")

    rate=float(launch["rate_usd_per_hour"])
    proposed_max_cost=round(rate*float(max_runtime_sec)/3600.0,6)
    budget=budget_decision(
        cost_ledger,
        budget_usd=float(cost_policy["current_authorized_budget_usd"]),
        proposed_charge_usd=proposed_max_cost,
    )
    if not budget["allowed"]:
        raise ZImageQualificationError("qualification max runtime would exceed project budget")

    request=compile_image_worker_request(job,matrix,base_runtime)
    return {
        "schema_version":1,
        "status":"QUALIFICATION_AUTHORIZED_NOT_EXECUTED",
        "request":request,
        "authorization_id":authorization["authorization_id"],
        "authorization_receipt_digest":authorization["receipt_digest"],
        "execution_plan_digest":execution_plan["plan_digest"],
        "pod_id":authorization["pod_id"],
        "gpu":GPU_NAME,
        "model_id":MODEL_ID,
        "model_repo":model["source_repo"],
        "model_revision":MODEL_REVISION,
        "production_gate":model["production_gate"],
        "qualification":dict(QUALIFICATION_CONFIG),
        "negative_prompt_handling":"APPLIED_NATIVE_ZIMAGE_PIPELINE_STRING",
        "max_runtime_sec":float(max_runtime_sec),
        "rate_usd_per_hour":rate,
        "proposed_max_cost_usd":proposed_max_cost,
        "current_ledger_cost_usd":budget["spent_usd"],
        "project_budget_usd":budget["budget_usd"],
        "budget_headroom_after_max_usd":round(float(budget["budget_usd"])-float(budget["projected_usd"]),6),
        "new_resource_creation_authorized":False,
        "production_acceptance":False,
        "selection_authorized":False,
        "publish_authority":False,
    }


def validate_model_dir(model_dir: Path) -> dict[str,Any]:
    if model_dir.is_symlink() or not model_dir.is_dir():
        raise ZImageQualificationError("model_dir must be a real directory")
    missing=[rel for rel in REQUIRED_MODEL_FILES if not (model_dir/rel).is_file()]
    if missing:
        raise ZImageQualificationError(f"model_dir missing required files: {missing}")
    rows=[]
    total=0
    for rel in REQUIRED_MODEL_FILES:
        path=model_dir/rel
        size=path.stat().st_size
        total+=size
        rows.append({"path":rel,"bytes":size})
    return {
        "required_file_count":len(rows),
        "required_bytes":total,
        "required_gib":round(total/1024**3,6),
        "files":rows,
    }


def build_output_manifest(
    *,
    request: dict[str,Any],
    artifact_path: Path,
    elapsed_sec: float,
    gpu_peak_memory_mb: float,
    runtime: dict[str,Any],
) -> dict[str,Any]:
    if elapsed_sec<=0:
        raise ZImageQualificationError("elapsed_sec must be positive")
    if gpu_peak_memory_mb<=0:
        raise ZImageQualificationError("gpu peak memory must be positive")
    if not artifact_path.is_file():
        raise ZImageQualificationError("artifact missing")
    artifact_sha=sha256_file(artifact_path)
    body={
        "schema_version":1,
        "request_digest":request["request_digest"],
        "job_id":request["job_id"],
        "job_digest":request["job_digest"],
        "blind_id":request["blind_id"],
        "asset_id":"asset_zimage_"+artifact_sha[:16],
        "asset_path":str(artifact_path),
        "asset_sha256":artifact_sha,
        "model_id":MODEL_ID,
        "model_revision":MODEL_REVISION,
        "seed":request["seed"],
        "elapsed_sec":round(float(elapsed_sec),6),
        "gpu_peak_memory_mb":round(float(gpu_peak_memory_mb),3),
        "runtime":runtime,
    }
    body["manifest_sha256"]=hashlib.sha256(canonical_json_bytes(body)).hexdigest()
    return validate_image_output_manifest(request,body)


def build_cost_entry(
    *,
    qualification: dict[str,Any],
    elapsed_sec: float,
    passed: bool,
    asset_id: str|None,
) -> dict[str,Any]:
    amount=round(float(elapsed_sec)*float(qualification["rate_usd_per_hour"])/3600.0,6)
    return {
        "cost_id":"zimage-"+qualification["request"]["job_id"]+"-"+("pass" if passed else "failed"),
        "category":"COMPUTE_ACCEPTED" if passed else "COMPUTE_FAILED",
        "amount_usd":amount,
        "logical_key":"T-019-ZIMAGE-QUALIFICATION",
        "attempt_id":qualification["request"]["job_id"],
        "asset_id":asset_id,
        "note":"Estimated from measured runner elapsed time at the active RunPod A40 hourly rate; provider accrued bill is not exposed by MCP.",
    }
