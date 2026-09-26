from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class Wan22TI2VError(ValueError):
    pass


MODEL_ID = "wan22-ti2v-5b"
MODEL_REPO = "Wan-AI/Wan2.2-TI2V-5B"
MODEL_REVISION = "921dbaf3f1674a56f47e83fb80a34bac8a8f203e"
CODE_REPO = "Wan-Video/Wan2.2"
CODE_REVISION = "1ea34ff48f87168174e12956e200b1d908b1c5ff"
TASK = "ti2v-5B"
ALLOWED_SIZES = {"1280*704", "704*1280"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _matrix_model(matrix: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in matrix.get("models", []) if row.get("model_id") == MODEL_ID]
    if len(rows) != 1:
        raise Wan22TI2VError("Wan2.2 TI2V-5B matrix row missing/duplicate")
    row = rows[0]
    if row.get("stage") != "video" or not row.get("enabled"):
        raise Wan22TI2VError("Wan2.2 TI2V-5B is not an enabled video candidate")
    if row.get("pin_status") != "PINNED":
        raise Wan22TI2VError("Wan2.2 TI2V-5B is not pinned")
    if row.get("source_repo") != MODEL_REPO or row.get("source_revision") != MODEL_REVISION:
        raise Wan22TI2VError("Wan2.2 TI2V-5B model pin drift")
    if row.get("license_gate") != "UPSTREAM_APACHE_2_0_PINNED":
        raise Wan22TI2VError("Wan2.2 TI2V-5B license gate is not cleared")
    if row.get("commercial_production_allowed") != "UPSTREAM_MODEL_LICENSE_PERMITS":
        raise Wan22TI2VError("Wan2.2 TI2V-5B commercial-use status is not permitted")
    return row


def validate_smoke_spec(
    spec: dict[str, Any],
    *,
    matrix: dict[str, Any],
    gpu_session: dict[str, Any],
) -> dict[str, Any]:
    _matrix_model(matrix)
    if spec.get("schema_version") != 1:
        raise Wan22TI2VError("unsupported smoke schema")
    if spec.get("model_id") != MODEL_ID:
        raise Wan22TI2VError("smoke model_id drift")
    if spec.get("model_repo") != MODEL_REPO or spec.get("model_revision") != MODEL_REVISION:
        raise Wan22TI2VError("smoke model pin drift")
    if spec.get("code_repo") != CODE_REPO or spec.get("code_revision") != CODE_REVISION:
        raise Wan22TI2VError("smoke code pin drift")
    if spec.get("task") != TASK:
        raise Wan22TI2VError("smoke task drift")
    if spec.get("size") not in ALLOWED_SIZES:
        raise Wan22TI2VError("unsupported TI2V smoke size")
    frame_num = spec.get("frame_num")
    if not isinstance(frame_num, int) or frame_num < 5 or (frame_num - 1) % 4:
        raise Wan22TI2VError("frame_num must be 4n+1 and >=5")
    sample_steps = spec.get("sample_steps")
    if not isinstance(sample_steps, int) or not 1 <= sample_steps <= 50:
        raise Wan22TI2VError("invalid sample_steps")
    if spec.get("offload_model") is not True or spec.get("convert_model_dtype") is not True or spec.get("t5_cpu") is not True:
        raise Wan22TI2VError("A40 smoke requires offload_model + convert_model_dtype + t5_cpu")
    if spec.get("reference_role") != "TECHNICAL_SMOKE_INPUT_NOT_MODEL_SELECTION":
        raise Wan22TI2VError("reference image role must not imply model selection")
    ref_sha = spec.get("reference_image_sha256")
    if not isinstance(ref_sha, str) or len(ref_sha) != 64:
        raise Wan22TI2VError("reference image hash missing")
    if not isinstance(spec.get("prompt"), str) or not spec["prompt"].strip():
        raise Wan22TI2VError("prompt required")
    if spec.get("quality_acceptance") is not False or spec.get("production_acceptance") is not False:
        raise Wan22TI2VError("technical smoke cannot grant quality/production acceptance")

    if gpu_session.get("provider") != "RunPod" or gpu_session.get("pod_id") != "0h1twwxqw6yx0k":
        raise Wan22TI2VError("GPU session does not bind the authorized RunPod")
    if gpu_session.get("gpu") != "NVIDIA A40" or gpu_session.get("provider_state") != "RUNNING":
        raise Wan22TI2VError("authorized A40 is not RUNNING")
    rate = float(gpu_session.get("rate_usd_per_hour", 0))
    cap = float(gpu_session.get("budget_cap_usd", 0))
    billed = float(gpu_session.get("provider_billed_usd") or gpu_session.get("paid_runtime_estimate_usd") or 0)
    max_runtime = float(spec.get("max_runtime_sec", 1800))
    if rate <= 0 or cap <= 0 or max_runtime <= 0:
        raise Wan22TI2VError("invalid paid-resource budget inputs")
    proposed_max = rate * max_runtime / 3600.0
    if billed + proposed_max > cap:
        raise Wan22TI2VError("video smoke max runtime would exceed paid budget")
    return {
        "schema_version": 1,
        "status": "SMOKE_AUTHORIZED_NOT_EXECUTED",
        "smoke_id": spec["smoke_id"],
        "model_id": MODEL_ID,
        "model_repo": MODEL_REPO,
        "model_revision": MODEL_REVISION,
        "code_repo": CODE_REPO,
        "code_revision": CODE_REVISION,
        "task": TASK,
        "size": spec["size"],
        "frame_num": frame_num,
        "sample_steps": sample_steps,
        "base_seed": int(spec["base_seed"]),
        "reference_image_sha256": ref_sha,
        "reference_role": spec["reference_role"],
        "rate_usd_per_hour": rate,
        "provider_billed_snapshot_usd": billed,
        "budget_cap_usd": cap,
        "proposed_max_cost_usd": round(proposed_max, 6),
        "quality_acceptance": False,
        "production_acceptance": False,
        "new_resource_creation_authorized": False,
        "publish_authority": False,
    }


def build_generate_argv(
    spec: dict[str, Any],
    *,
    python_exe: str,
    wan_repo_dir: Path,
    model_dir: Path,
    reference_image: Path,
    output_file: Path,
) -> list[str]:
    return [
        python_exe,
        str(wan_repo_dir / "generate.py"),
        "--task", TASK,
        "--size", str(spec["size"]),
        "--ckpt_dir", str(model_dir),
        "--offload_model", "True",
        "--convert_model_dtype",
        "--t5_cpu",
        "--image", str(reference_image),
        "--prompt", str(spec["prompt"]),
        "--frame_num", str(int(spec["frame_num"])),
        "--sample_steps", str(int(spec["sample_steps"])),
        "--base_seed", str(int(spec["base_seed"])),
        "--save_file", str(output_file),
    ]


def validate_local_inputs(
    spec: dict[str, Any],
    *,
    wan_repo_dir: Path,
    model_dir: Path,
    reference_image: Path,
) -> None:
    if not (wan_repo_dir / "generate.py").is_file() or not (wan_repo_dir / "wan").is_dir():
        raise Wan22TI2VError("Wan2.2 runtime source is incomplete")
    git_head = wan_repo_dir / ".git/HEAD"
    if not git_head.exists():
        raise Wan22TI2VError("Wan2.2 runtime source must be a git checkout")
    if not model_dir.is_dir():
        raise Wan22TI2VError("Wan2.2 model directory missing")
    if not reference_image.is_file():
        raise Wan22TI2VError("reference image missing")
    if sha256_file(reference_image) != spec["reference_image_sha256"]:
        raise Wan22TI2VError("reference image hash mismatch")


def build_smoke_evidence(
    *,
    plan: dict[str, Any],
    output_file: Path,
    elapsed_sec: float,
    peak_vram_mib: float,
    ffprobe: dict[str, Any],
    returncode: int,
) -> dict[str, Any]:
    passed = returncode == 0 and output_file.is_file() and output_file.stat().st_size > 0
    evidence = {
        **plan,
        "status": "PASS_RUNTIME_SMOKE" if passed else "FAILED",
        "elapsed_sec": round(float(elapsed_sec), 6),
        "peak_vram_mib": round(float(peak_vram_mib), 3),
        "returncode": int(returncode),
        "ffprobe": ffprobe,
        "quality_status": "NOT_EVALUATED",
        "quality_acceptance": False,
        "production_acceptance": False,
    }
    if passed:
        evidence["output"] = {
            "path": str(output_file),
            "bytes": output_file.stat().st_size,
            "sha256": sha256_file(output_file),
        }
        evidence["estimated_execution_cost_usd"] = round(
            float(elapsed_sec) * float(plan["rate_usd_per_hour"]) / 3600.0, 6
        )
    return evidence