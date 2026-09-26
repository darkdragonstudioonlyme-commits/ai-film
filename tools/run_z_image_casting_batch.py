#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.cost_ledger import budget_decision
from film.z_image_live import validate_model_dir
from film.z_image_casting import (
    ZImageCastingError,
    build_output_manifest,
    build_smoke_plan,
    load_json,
    select_smoke_jobs,
    validate_execution_context,
    validate_profile,
)

PROFILE_PATH = ROOT / "model-evaluations/slice01/z_image_casting_profile.json"
JOBS_PATH = ROOT / "projects/slice01/casting/generation/casting_jobs.json"
COST_LEDGER_PATH = ROOT / "projects/slice01/runtime/cost_ledger.json"
COST_POLICY_PATH = ROOT / "projects/slice01/runtime/cost_policy.json"

def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def nvidia_memory_used_mib() -> int | None:
    proc = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    values = []
    for line in proc.stdout.splitlines():
        try:
            values.append(int(line.strip()))
        except ValueError:
            return None
    return max(values) if values else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the fixed Z-Image casting smoke on an authorized A40."
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--model-dir",
        default="/workspace/models/z-image",
    )
    parser.add_argument(
        "--out-root",
        default="/workspace/artifacts/z-image-casting-smoke",
    )
    parser.add_argument(
        "--evidence-out",
        default="/workspace/runs/z-image-casting-smoke/evidence.json",
    )
    parser.add_argument("--max-jobs", type=int)
    args = parser.parse_args()

    profile = validate_profile(load_json(PROFILE_PATH))
    jobs = load_json(JOBS_PATH)["jobs"]
    selected = select_smoke_jobs(jobs, profile)
    max_jobs = profile["smoke_jobs"] if args.max_jobs is None else args.max_jobs
    if max_jobs < 1 or max_jobs > profile["smoke_jobs"]:
        parser.error("--max-jobs must be within the fixed smoke population")
    selected = selected[:max_jobs]

    plan = build_smoke_plan(ROOT, profile, jobs)
    plan["job_ids"] = [row["job_id"] for row in selected]
    plan["planned_jobs"] = len(selected)

    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
        return 0
    if plan.get("status")!="READY_FOR_EXPLICIT_RUNNER_EXECUTION":
        raise ZImageCastingError("formal smoke already complete; rerun is not authorized")

    model_dir = Path(args.model_dir).expanduser().resolve()
    model_snapshot_shape = validate_model_dir(model_dir)

    context = validate_execution_context(ROOT, profile)
    out_root = Path(args.out_root).expanduser().resolve()
    evidence_path = Path(args.evidence_out).expanduser().resolve()
    out_root.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)

    import torch
    from diffusers import ZImagePipeline

    if not torch.cuda.is_available():
        raise ZImageCastingError("CUDA is not available")
    if torch.cuda.get_device_name(0) != profile["gpu"]:
        raise ZImageCastingError(
            f"unexpected GPU: {torch.cuda.get_device_name(0)}"
        )

    parameters = {
        "width": profile["width"],
        "height": profile["height"],
        "num_inference_steps": profile["num_inference_steps"],
        "guidance_scale": profile["guidance_scale"],
        "cfg_normalization": profile["cfg_normalization"],
        "low_cpu_mem_usage": profile["low_cpu_mem_usage"],
        "negative_prompt_mode": profile["negative_prompt_mode"],
        "negative_prompt_applied": True,
        "dtype": profile["dtype"],
        "mode": profile["mode"],
    }
    started = time.time()
    started_mono = time.perf_counter()
    evidence = {
        "schema_version": 1,
        "status": "RUNNING",
        "profile_id": profile["profile_id"],
        "model_id": profile["model_id"],
        "repo": profile["repo"],
        "revision": profile["revision"],
        "authorization_id": context["authorization_id"],
        "rate_usd_per_hour": context["rate_usd_per_hour"],
        "planned_jobs": len(selected),
        "parameters": parameters,
        "model_dir": str(model_dir),
        "model_snapshot_shape": model_snapshot_shape,
        "jobs": [],
        "selection_authorized": False,
        "publish_authority": False,
    }

    try:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        load_start = time.perf_counter()
        pipe = ZImagePipeline.from_pretrained(
            str(model_dir),
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=profile["low_cpu_mem_usage"],
        )
        evidence["load_cpu_sec"] = round(
            time.perf_counter() - load_start, 6
        )
        cuda_start = time.perf_counter()
        pipe = pipe.to("cuda")
        torch.cuda.synchronize()
        evidence["to_cuda_sec"] = round(
            time.perf_counter() - cuda_start, 6
        )
        evidence["nvidia_smi_after_load_mib"] = nvidia_memory_used_mib()
        evidence["torch_peak_after_load_mib"] = round(
            torch.cuda.max_memory_reserved() / 1024**2, 3
        )

        outputs = []
        for job in selected:
            torch.cuda.reset_peak_memory_stats()
            generator = torch.Generator(device="cuda").manual_seed(
                int(job["seed"])
            )
            job_start = time.perf_counter()
            image = pipe(
                prompt=job["prompt"],
                negative_prompt=job["negative_prompt"],
                height=profile["height"],
                width=profile["width"],
                cfg_normalization=profile["cfg_normalization"],
                num_inference_steps=profile["num_inference_steps"],
                guidance_scale=profile["guidance_scale"],
                generator=generator,
            ).images[0]
            torch.cuda.synchronize()
            elapsed = time.perf_counter() - job_start
            artifact = out_root / f"{job['job_id']}.png"
            image.save(artifact)
            peak = round(
                torch.cuda.max_memory_reserved() / 1024**2, 3
            )
            manifest = build_output_manifest(
                job,
                artifact,
                elapsed_sec=elapsed,
                gpu_peak_memory_mb=peak,
                parameters=parameters,
            )
            manifest["nvidia_smi_after_inference_mib"] = (
                nvidia_memory_used_mib()
            )
            atomic_json(
                out_root / f"{job['job_id']}.manifest.json",
                manifest,
            )
            outputs.append(manifest)
            evidence["jobs"].append(
                {
                    "job_id": job["job_id"],
                    "blind_id": job["blind_id"],
                    "character_id": job["character_id"],
                    "style": job["style"],
                    "slot": job["slot"],
                    "elapsed_sec": manifest["elapsed_sec"],
                    "gpu_peak_memory_mb": manifest["gpu_peak_memory_mb"],
                    "nvidia_smi_after_inference_mib": (
                        manifest["nvidia_smi_after_inference_mib"]
                    ),
                    "asset_id": manifest["asset_id"],
                    "asset_sha256": manifest["asset_sha256"],
                    "manifest_sha256": manifest["manifest_sha256"],
                    "status": "PASS",
                }
            )

        total_elapsed = time.perf_counter() - started_mono
        estimated_cost = round(
            total_elapsed * context["rate_usd_per_hour"] / 3600.0,
            6,
        )
        ledger = load_json(COST_LEDGER_PATH)
        cost_policy = load_json(COST_POLICY_PATH)
        post_budget = budget_decision(
            ledger,
            budget_usd=cost_policy["current_authorized_budget_usd"],
            proposed_charge_usd=estimated_cost,
        )
        evidence.update(
            {
                "status": "PASS",
                "started_unix": started,
                "finished_unix": time.time(),
                "elapsed_sec_total": round(total_elapsed, 6),
                "estimated_compute_cost_usd": estimated_cost,
                "post_run_budget_decision": post_budget,
                "max_gpu_peak_memory_mb": max(
                    row["gpu_peak_memory_mb"]
                    for row in evidence["jobs"]
                ),
                "max_nvidia_smi_memory_mib": max(
                    row["nvidia_smi_after_inference_mib"]
                    for row in evidence["jobs"]
                    if row["nvidia_smi_after_inference_mib"] is not None
                ),
            }
        )
        atomic_json(
            out_root / "outputs.json",
            {
                "schema_version": 1,
                "model_id": profile["model_id"],
                "model_revision": profile["revision"],
                "outputs": outputs,
            },
        )
        atomic_json(evidence_path, evidence)
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
        return 0
    except Exception as exc:
        evidence.update(
            {
                "status": "FAILED",
                "finished_unix": time.time(),
                "elapsed_sec_total": round(
                    time.perf_counter() - started_mono, 6
                ),
                "failure_type": type(exc).__name__,
                "failure": str(exc),
            }
        )
        atomic_json(evidence_path, evidence)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
