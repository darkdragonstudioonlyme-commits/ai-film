from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .cost_ledger import budget_decision
from .image_runner import compile_image_worker_request, digest as request_digest, validate_image_output_manifest
from .launch_gate import digest as launch_digest, validate_launch_authorization


class Flux2KleinQualificationError(ValueError):
    pass


MODEL_ID="flux2-klein-4b"
GPU_NAME="NVIDIA A40"
QUALIFICATION_CONFIG={
    "width":512,
    "height":512,
    "num_inference_steps":4,
    "guidance_scale":1.0,
    "torch_dtype":"bfloat16",
    "mode":"FULL_GPU",
}
REQUIRED_MODEL_FILES=(
    "model_index.json",
    "scheduler/scheduler_config.json",
    "transformer/config.json",
    "transformer/diffusion_pytorch_model.safetensors",
    "text_encoder/config.json",
    "text_encoder/model.safetensors.index.json",
    "tokenizer/tokenizer.json",
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
        raise Flux2KleinQualificationError("FLUX.2 klein model matrix identity missing/duplicated")
    model=rows[0]
    if not model.get("enabled") or model.get("stage")!="image":
        raise Flux2KleinQualificationError("FLUX.2 klein is not enabled image candidate")
    if model.get("pin_status")!="PINNED":
        raise Flux2KleinQualificationError("FLUX.2 klein is not pinned")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise Flux2KleinQualificationError("FLUX.2 klein upstream license pin is not cleared")
    if model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
        raise Flux2KleinQualificationError("FLUX.2 klein upstream commercial-use status is not permitted")
    return model


def prepare_flux2_qualification(
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
        raise Flux2KleinQualificationError("max_runtime_sec must be positive")
    model=_matrix_model(matrix)
    if job.get("model_id")!=MODEL_ID:
        raise Flux2KleinQualificationError("job is not FLUX.2 klein")
    if job.get("model_repo")!=model.get("source_repo") or job.get("model_revision")!=model.get("source_revision"):
        raise Flux2KleinQualificationError("job model source identity drift")
    if live_runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME":
        raise Flux2KleinQualificationError("live A40 runtime lock missing")
    target=live_runtime.get("target",{})
    if target.get("gpu")!=GPU_NAME or target.get("torch")!="2.8.0+cu128" or target.get("torch_cuda")!="12.8":
        raise Flux2KleinQualificationError("live A40 runtime identity mismatch")
    if live_runtime.get("packages",{}).get("diffusers")!="0.40.0":
        raise Flux2KleinQualificationError("diffusers runtime drift")
    if live_runtime.get("packages",{}).get("huggingface-hub")!="1.33.0":
        raise Flux2KleinQualificationError("huggingface hub runtime drift")

    proposal_digest=launch_digest(proposal)
    launch=validate_launch_authorization(
        authorization,
        proposal_digest=proposal_digest,
        rate_snapshot=rate_snapshot,
        requested_gpu=GPU_NAME,
        requested_max_usd=float(cost_policy["current_authorized_budget_usd"]),
    )
    if execution_plan.get("plan_digest")!=authorization.get("execution_plan_digest"):
        raise Flux2KleinQualificationError("execution plan / authorization digest mismatch")
    if execution_plan.get("pod_id")!=authorization.get("pod_id"):
        raise Flux2KleinQualificationError("execution plan / authorization pod mismatch")
    if execution_plan.get("new_resource_creation_authorized") is not False:
        raise Flux2KleinQualificationError("runner does not accept authority to create resources")

    rate=float(launch["rate_usd_per_hour"])
    proposed_max_cost=round(rate*float(max_runtime_sec)/3600.0,6)
    budget=budget_decision(
        cost_ledger,
        budget_usd=float(cost_policy["current_authorized_budget_usd"]),
        proposed_charge_usd=proposed_max_cost,
    )
    if not budget["allowed"]:
        raise Flux2KleinQualificationError("qualification max runtime would exceed project budget")

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
        "model_revision":model["source_revision"],
        "qualification":dict(QUALIFICATION_CONFIG),
        "negative_prompt_handling":"NOT_APPLIED_PIPELINE_API_HAS_NO_NEGATIVE_PROMPT_STRING",
        "max_runtime_sec":float(max_runtime_sec),
        "rate_usd_per_hour":rate,
        "proposed_max_cost_usd":proposed_max_cost,
        "current_ledger_cost_usd":budget["spent_usd"],
        "project_budget_usd":budget["budget_usd"],
        "budget_headroom_after_max_usd":round(float(budget["budget_usd"])-float(budget["projected_usd"]),6),
        "new_resource_creation_authorized":False,
        "publish_authority":False,
    }


def validate_model_dir(model_dir: Path) -> dict[str,Any]:
    if model_dir.is_symlink() or not model_dir.is_dir():
        raise Flux2KleinQualificationError("model_dir must be a real directory")
    missing=[rel for rel in REQUIRED_MODEL_FILES if not (model_dir/rel).is_file()]
    if missing:
        raise Flux2KleinQualificationError(f"model_dir missing required files: {missing}")
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
        raise Flux2KleinQualificationError("elapsed_sec must be positive")
    if gpu_peak_memory_mb<=0:
        raise Flux2KleinQualificationError("gpu peak memory must be positive")
    if not artifact_path.is_file():
        raise Flux2KleinQualificationError("artifact missing")
    body={
        "schema_version":1,
        "request_digest":request["request_digest"],
        "job_id":request["job_id"],
        "job_digest":request["job_digest"],
        "blind_id":request["blind_id"],
        "asset_id":"asset_"+hashlib.sha256((request["job_id"]+":"+sha256_file(artifact_path)).encode("utf-8")).hexdigest()[:16],
        "asset_path":str(artifact_path),
        "asset_sha256":sha256_file(artifact_path),
        "model_id":request["model"]["model_id"],
        "model_revision":request["model"]["revision"],
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
        "cost_id":"flux2-"+qualification["request"]["job_id"]+"-"+("pass" if passed else "failed"),
        "category":"COMPUTE_ACCEPTED" if passed else "COMPUTE_FAILED",
        "amount_usd":amount,
        "logical_key":"T-019-FLUX2-QUALIFICATION",
        "attempt_id":qualification["request"]["job_id"],
        "asset_id":asset_id,
        "note":"Estimated from measured runner elapsed time at the active RunPod A40 hourly rate; provider accrued bill is not exposed by MCP.",
    }
