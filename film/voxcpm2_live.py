from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .cost_ledger import budget_decision
from .launch_gate import digest as launch_digest, validate_launch_authorization
from .voice_eval import validate_voice_output_manifest


class VoxCPM2QualificationError(ValueError):
    pass


MODEL_ID="voxcpm2"
GPU_NAME="NVIDIA A40"
PACKAGE_PIN="voxcpm==2.0.3"
SAMPLE_RATE_HZ=48000
REQUIRED_MODEL_FILES=(
    "config.json",
    "model.safetensors",
    "audiovae.pth",
    "tokenizer.json",
    "tokenizer_config.json",
    "tokenization_voxcpm2.py",
    "special_tokens_map.json",
)


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def _matrix_model(matrix: dict[str,Any]) -> dict[str,Any]:
    rows=[row for row in matrix.get("models",[]) if row.get("model_id")==MODEL_ID]
    if len(rows)!=1:
        raise VoxCPM2QualificationError("VoxCPM2 model matrix identity missing/duplicated")
    model=rows[0]
    if model.get("stage")!="voice":
        raise VoxCPM2QualificationError("VoxCPM2 is not a voice candidate")
    if model.get("pin_status")!="PINNED":
        raise VoxCPM2QualificationError("VoxCPM2 is not pinned")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise VoxCPM2QualificationError("VoxCPM2 upstream license pin is not cleared")
    if model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
        raise VoxCPM2QualificationError("VoxCPM2 commercial-use status is not permitted")
    if model.get("package_pin")!=PACKAGE_PIN:
        raise VoxCPM2QualificationError("VoxCPM2 package pin drift")
    return model


def prepare_voxcpm2_qualification(
    *,
    request: dict[str,Any],
    matrix: dict[str,Any],
    config: dict[str,Any],
    live_runtime: dict[str,Any],
    proposal: dict[str,Any],
    execution_plan: dict[str,Any],
    rate_snapshot: dict[str,Any],
    authorization: dict[str,Any],
    cost_policy: dict[str,Any],
    cost_ledger: dict[str,Any],
    max_runtime_sec: float=900.0,
) -> dict[str,Any]:
    if max_runtime_sec<=0:
        raise VoxCPM2QualificationError("max_runtime_sec must be positive")
    model=_matrix_model(matrix)
    cfg_model=config.get("model",{})
    expected={
        "model_id":MODEL_ID,
        "repo":model["source_repo"],
        "revision":model["source_revision"],
        "package":PACKAGE_PIN,
        "sample_rate_hz":SAMPLE_RATE_HZ,
    }
    if any(request.get("model",{}).get(k)!=v for k,v in expected.items()):
        raise VoxCPM2QualificationError("request model identity drift")
    if any(cfg_model.get(k)!=v for k,v in expected.items()):
        raise VoxCPM2QualificationError("voice config model identity drift")
    if request.get("mode")!="voice_design" or config.get("mode")!="voice_design":
        raise VoxCPM2QualificationError("qualification only permits voice_design mode")
    if request.get("reference_audio") is not None:
        raise VoxCPM2QualificationError("reference audio must remain disabled")
    if config.get("reference_audio_allowed") or config.get("voice_cloning_allowed"):
        raise VoxCPM2QualificationError("voice cloning/reference audio gate is not closed")
    if request.get("execution_permitted") is not False:
        raise VoxCPM2QualificationError("canonical request must remain non-executing")

    if live_runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME":
        raise VoxCPM2QualificationError("live A40 runtime lock missing")
    target=live_runtime.get("target",{})
    if target.get("gpu")!=GPU_NAME or target.get("torch")!="2.8.0+cu128" or target.get("torch_cuda")!="12.8":
        raise VoxCPM2QualificationError("live A40 runtime identity mismatch")

    launch=validate_launch_authorization(
        authorization,
        proposal_digest=launch_digest(proposal),
        rate_snapshot=rate_snapshot,
        requested_gpu=GPU_NAME,
        requested_max_usd=float(cost_policy["current_authorized_budget_usd"]),
    )
    if execution_plan.get("plan_digest")!=authorization.get("execution_plan_digest"):
        raise VoxCPM2QualificationError("execution plan / authorization digest mismatch")
    if execution_plan.get("pod_id")!=authorization.get("pod_id"):
        raise VoxCPM2QualificationError("execution plan / authorization pod mismatch")
    if execution_plan.get("new_resource_creation_authorized") is not False:
        raise VoxCPM2QualificationError("new resource creation is not permitted")

    rate=float(launch["rate_usd_per_hour"])
    proposed_max_cost=round(rate*float(max_runtime_sec)/3600.0,6)
    budget=budget_decision(
        cost_ledger,
        budget_usd=float(cost_policy["current_authorized_budget_usd"]),
        proposed_charge_usd=proposed_max_cost,
    )
    if not budget["allowed"]:
        raise VoxCPM2QualificationError("qualification max runtime would exceed project budget")

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
        "package":PACKAGE_PIN,
        "mode":"voice_design",
        "sample_rate_hz":SAMPLE_RATE_HZ,
        "load_denoiser":False,
        "optimize":False,
        "reference_audio":None,
        "prompt_audio":None,
        "cfg_value":float(request["cfg_value"]),
        "inference_timesteps":int(request["inference_timesteps"]),
        "seed":int(request["seed"]),
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
        raise VoxCPM2QualificationError("model_dir must be a real directory")
    missing=[rel for rel in REQUIRED_MODEL_FILES if not (model_dir/rel).is_file()]
    if missing:
        raise VoxCPM2QualificationError(f"model_dir missing required files: {missing}")
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
    audio_path: Path,
    duration_sec: float,
    gpu_peak_memory_mb: float,
    runtime: dict[str,Any],
) -> dict[str,Any]:
    if duration_sec<=0:
        raise VoxCPM2QualificationError("audio duration must be positive")
    if gpu_peak_memory_mb<=0:
        raise VoxCPM2QualificationError("gpu peak memory must be positive")
    if not audio_path.is_file():
        raise VoxCPM2QualificationError("audio artifact missing")
    manifest={
        "schema_version":1,
        "request_digest":request["request_digest"],
        "request_id":request["request_id"],
        "blind_id":request["blind_id"],
        "audio_sha256":sha256_file(audio_path),
        "sample_rate_hz":SAMPLE_RATE_HZ,
        "duration_sec":round(float(duration_sec),6),
        "bytes":audio_path.stat().st_size,
        "asset_path":str(audio_path),
        "gpu_peak_memory_mb":round(float(gpu_peak_memory_mb),3),
        "runtime":runtime,
    }
    return validate_voice_output_manifest(request,manifest)


def build_cost_entry(
    *,
    qualification: dict[str,Any],
    elapsed_sec: float,
    passed: bool,
) -> dict[str,Any]:
    amount=round(float(elapsed_sec)*float(qualification["rate_usd_per_hour"])/3600.0,6)
    return {
        "cost_id":"voxcpm2-"+qualification["request"]["request_id"]+"-"+("pass" if passed else "failed"),
        "category":"COMPUTE_ACCEPTED" if passed else "COMPUTE_FAILED",
        "amount_usd":amount,
        "logical_key":"T-019-VOXCPM2-QUALIFICATION",
        "attempt_id":qualification["request"]["request_id"],
        "asset_id":None,
        "note":"Estimated from measured runner elapsed time at the active RunPod A40 hourly rate; provider accrued bill is not exposed by MCP.",
    }
