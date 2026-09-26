from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .admission import evaluate_admission


class ImageKeyframeError(ValueError):
    pass


MODEL_CONFIGS = {
    "flux2-klein-4b": {
        "revision": "e7b7dc27f91deacad38e78976d1f2b499d76a294",
        "steps": 4,
        "guidance_scale": 1.0,
    },
    "z-image": {
        "revision": "04cc4abb7c5069926f75c9bfde9ef43d49423021",
        "steps": 50,
        "guidance_scale": 4.0,
        "cfg_normalization": False,
    },
}


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def select_probe_job(spec: dict[str,Any], probe_job_id: str) -> dict[str,Any]:
    rows=[row for row in spec.get("jobs",[]) if row.get("probe_job_id")==probe_job_id]
    if len(rows)!=1:
        raise ImageKeyframeError("unknown/duplicate probe_job_id")
    return rows[0]


def validate_probe_job(
    spec: dict[str,Any],
    job: dict[str,Any],
    *,
    matrix: dict[str,Any],
    resources: dict[str,Any],
    worker: dict[str,Any],
    gpu_session: dict[str,Any],
) -> dict[str,Any]:
    if spec.get("schema_version")!=1 or spec.get("status")!="READY_NOT_EXECUTED":
        raise ImageKeyframeError("keyframe probe spec is not ready")
    if spec.get("quality_acceptance") is not False or spec.get("selection_authorized") is not False:
        raise ImageKeyframeError("probe must not grant quality/selection authority")
    if job.get("model_id") not in MODEL_CONFIGS:
        raise ImageKeyframeError("unsupported image model")
    cfg=MODEL_CONFIGS[job["model_id"]]
    if job.get("model_revision")!=cfg["revision"]:
        raise ImageKeyframeError("model revision drift")
    if job.get("num_inference_steps")!=cfg["steps"] or float(job.get("guidance_scale",-1))!=cfg["guidance_scale"]:
        raise ImageKeyframeError("model inference parameters drift")
    width=job.get("width"); height=job.get("height")
    if not isinstance(width,int) or not isinstance(height,int) or width%16 or height%16 or width<512 or height<512:
        raise ImageKeyframeError("invalid keyframe dimensions")
    if not isinstance(job.get("prompt"),str) or not job["prompt"].strip():
        raise ImageKeyframeError("prompt required")
    if job.get("style")!="photoreal":
        raise ImageKeyframeError("first quality probe is photoreal only")

    model=next((r for r in matrix.get("models",[]) if r.get("model_id")==job["model_id"]),None)
    if model is None or not model.get("enabled") or model.get("source_revision")!=cfg["revision"]:
        raise ImageKeyframeError("model matrix pin/enable drift")
    if model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
        raise ImageKeyframeError("model license gate not cleared")

    profile=next((r for r in resources.get("profiles",[]) if r.get("model_id")==job["model_id"]),None)
    if profile is None:
        raise ImageKeyframeError("resource profile missing")
    decision=evaluate_admission(profile,worker)
    if not decision["admitted"]:
        raise ImageKeyframeError("worker admission failed: "+",".join(decision["reasons"]))

    if gpu_session.get("provider_state")!="RUNNING" or gpu_session.get("pod_id")!="0h1twwxqw6yx0k":
        raise ImageKeyframeError("authorized Pod is not RUNNING")
    rate=float(gpu_session.get("rate_usd_per_hour",0))
    billed=float(gpu_session.get("provider_billed_usd") or gpu_session.get("paid_runtime_estimate_usd") or 0)
    cap=float(gpu_session.get("budget_cap_usd",0))
    max_runtime=float(job.get("max_runtime_sec",600))
    proposed=rate*max_runtime/3600.0
    if rate<=0 or billed+proposed>cap:
        raise ImageKeyframeError("paid budget guard failed")

    return {
        "schema_version":1,
        "status":"KEYFRAME_PROBE_AUTHORIZED_NOT_EXECUTED",
        "probe_id":spec["probe_id"],
        "probe_job_id":job["probe_job_id"],
        "shot_id":spec["shot_id"],
        "model_id":job["model_id"],
        "model_revision":job["model_revision"],
        "width":width,
        "height":height,
        "seed":int(job["seed"]),
        "num_inference_steps":job["num_inference_steps"],
        "guidance_scale":float(job["guidance_scale"]),
        "cfg_normalization":job.get("cfg_normalization"),
        "prompt":job["prompt"],
        "negative_prompt":job.get("negative_prompt",""),
        "rate_usd_per_hour":rate,
        "provider_billed_snapshot_usd":billed,
        "budget_cap_usd":cap,
        "proposed_max_cost_usd":round(proposed,6),
        "selection_authorized":False,
        "quality_status":"NOT_EVALUATED",
        "production_acceptance":False,
        "publish_authority":False,
    }


def build_evidence(
    plan: dict[str,Any],
    *,
    artifact: Path,
    elapsed_sec: float,
    peak_vram_mib: float,
    returncode: int=0,
) -> dict[str,Any]:
    passed=returncode==0 and artifact.is_file() and artifact.stat().st_size>0
    out={
        **plan,
        "status":"PASS_RUNTIME" if passed else "FAILED",
        "elapsed_sec":round(float(elapsed_sec),6),
        "peak_vram_mib":round(float(peak_vram_mib),3),
        "returncode":int(returncode),
        "quality_status":"AWAITING_OWNER_SCORING" if passed else "NOT_EVALUATED",
        "selection_authorized":False,
        "production_acceptance":False,
    }
    if passed:
        out["output"]={
            "path":str(artifact),
            "bytes":artifact.stat().st_size,
            "sha256":sha256_file(artifact),
            "width":plan["width"],
            "height":plan["height"],
        }
        out["estimated_execution_cost_usd"]=round(float(elapsed_sec)*float(plan["rate_usd_per_hour"])/3600.0,6)
    return out
