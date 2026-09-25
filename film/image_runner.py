from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class RunnerContractError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def compile_image_worker_request(
    casting_job: dict[str, Any],
    model_matrix: dict[str, Any],
    runtime_lock: dict[str, Any],
) -> dict[str, Any]:
    if casting_job.get("execution_permitted") is not False:
        raise RunnerContractError("casting job must remain non-executing before worker authorization")
    model_id = casting_job.get("model_id")
    models = {m["model_id"]: m for m in model_matrix.get("models", [])}
    if model_id not in models:
        raise RunnerContractError(f"unknown model: {model_id}")
    model = models[model_id]
    if not model.get("enabled") or model.get("stage") != "image":
        raise RunnerContractError(f"model is not an enabled image candidate: {model_id}")
    if model.get("pin_status") != "PINNED":
        raise RunnerContractError(f"model pin missing: {model_id}")
    if model.get("execution_ready"):
        raise RunnerContractError("worker compiler does not grant model execution authority")
    if runtime_lock.get("status") != "PINNED_BASE_DRY_RUN_ONLY" or runtime_lock.get("execution_ready") is not False:
        raise RunnerContractError("runtime lock is not in dry-run-only state")

    source = {
        "schema_version": 1,
        "worker_contract_version": "casting-image-worker-v1",
        "job_id": casting_job["job_id"],
        "job_digest": casting_job["job_digest"],
        "blind_id": casting_job["blind_id"],
        "character_id": casting_job["character_id"],
        "style": casting_job["style"],
        "slot": casting_job["slot"],
        "seed": int(casting_job["seed"]),
        "model": {
            "model_id": model_id,
            "repo": model["source_repo"],
            "revision": model["source_revision"],
            "license_gate": model["license_gate"],
            "production_gate": model.get("production_gate"),
        },
        "prompt": casting_job["prompt"],
        "negative_prompt": casting_job["negative_prompt"],
        "runtime": {
            "os": runtime_lock["target"]["os"],
            "python": runtime_lock["target"]["python"],
            "gpu_vendor": runtime_lock["target"]["gpu_vendor"],
            "cuda": runtime_lock["target"]["cuda"],
            "packages": runtime_lock["packages"],
        },
        "output_contract": {
            "required_fields": [
                "request_digest",
                "job_id",
                "job_digest",
                "blind_id",
                "asset_id",
                "asset_path",
                "asset_sha256",
                "manifest_sha256",
                "model_id",
                "model_revision",
                "seed",
                "elapsed_sec",
                "gpu_peak_memory_mb",
            ],
            "kind": "image",
        },
        "provider_resource_required": True,
        "provider_resource_created": False,
        "paid_authority_inherited": False,
        "execution_permitted": False,
    }
    source["request_digest"] = digest(source)
    return source


def validate_image_output_manifest(
    request: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    required = set(request["output_contract"]["required_fields"])
    missing = sorted(required - set(manifest))
    if missing:
        raise RunnerContractError(f"image output manifest missing fields: {missing}")
    exact_pairs = {
        "request_digest": request["request_digest"],
        "job_id": request["job_id"],
        "job_digest": request["job_digest"],
        "blind_id": request["blind_id"],
        "model_id": request["model"]["model_id"],
        "model_revision": request["model"]["revision"],
        "seed": request["seed"],
    }
    for key, expected in exact_pairs.items():
        if manifest.get(key) != expected:
            raise RunnerContractError(f"image output identity mismatch: {key}")
    for field in ("asset_sha256", "manifest_sha256"):
        value = manifest.get(field)
        if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise RunnerContractError(f"invalid sha256 field: {field}")
    if not isinstance(manifest.get("asset_id"), str) or not manifest["asset_id"]:
        raise RunnerContractError("invalid asset_id")
    if not isinstance(manifest.get("asset_path"), str) or not manifest["asset_path"]:
        raise RunnerContractError("invalid asset_path")
    if float(manifest.get("elapsed_sec", 0)) <= 0:
        raise RunnerContractError("invalid elapsed_sec")
    peak = manifest.get("gpu_peak_memory_mb")
    if peak is not None and float(peak) <= 0:
        raise RunnerContractError("invalid gpu_peak_memory_mb")
    return dict(manifest)
