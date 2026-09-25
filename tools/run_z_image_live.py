#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.z_image_live import (
    build_cost_entry,
    build_output_manifest,
    prepare_z_image_qualification,
    validate_model_dir,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pick_job(job_id: str) -> dict:
    jobs=load(ROOT/"projects/slice01/casting/generation/casting_jobs.json")["jobs"]
    rows=[row for row in jobs if row.get("job_id")==job_id]
    if len(rows)!=1:
        raise SystemExit(f"unknown/duplicate casting job: {job_id}")
    return rows[0]


def gpu_used_mib() -> int|None:
    try:
        out=subprocess.check_output(
            ["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],
            text=True,
        )
        return max(int(x.strip()) for x in out.splitlines() if x.strip())
    except Exception:
        return None


def atomic_json(path: Path,value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    ap=argparse.ArgumentParser(description="Plan or execute one exact Z-Image casting qualification job on the authorized RunPod A40.")
    ap.add_argument("--job-id",required=True)
    ap.add_argument("--max-runtime-sec",type=float,default=1800.0)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--model-dir")
    ap.add_argument("--out-root",default="/workspace/runs/z-image-live")
    args=ap.parse_args()

    job=pick_job(args.job_id)
    matrix=load(ROOT/"model-evaluations/slice01/model_matrix.json")
    base_runtime=load(ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json")
    live_runtime=load(ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json")
    proposal=load(ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json")
    execution_plan=load(ROOT/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json")
    rate_snapshot=load(ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json")
    authorization=load(ROOT/"model-evaluations/slice01/launch_authorization.active.json")
    cost_policy=load(ROOT/"projects/slice01/runtime/cost_policy.json")
    cost_ledger=load(ROOT/"projects/slice01/runtime/cost_ledger.json")
    qual=prepare_z_image_qualification(
        job=job,
        matrix=matrix,
        base_runtime=base_runtime,
        live_runtime=live_runtime,
        proposal=proposal,
        execution_plan=execution_plan,
        rate_snapshot=rate_snapshot,
        authorization=authorization,
        cost_policy=cost_policy,
        cost_ledger=cost_ledger,
        max_runtime_sec=args.max_runtime_sec,
    )
    if not args.execute:
        print(json.dumps(qual,ensure_ascii=False,sort_keys=True))
        return 0
    if not args.model_dir:
        ap.error("--execute requires --model-dir")

    model_dir=Path(args.model_dir).resolve()
    qual["model_dir"]=str(model_dir)
    qual["model_snapshot_shape"]=validate_model_dir(model_dir)
    out_root=Path(args.out_root).resolve()/args.job_id
    out_root.mkdir(parents=True,exist_ok=True)
    evidence_path=out_root/"evidence.json"
    atomic_json(evidence_path,{**qual,"status":"STARTED"})

    started=time.time()
    t0=time.perf_counter()
    try:
        import torch
        from diffusers import ZImagePipeline

        if torch.__version__!="2.8.0+cu128" or torch.version.cuda!="12.8":
            raise RuntimeError(f"torch runtime drift: {torch.__version__} / {torch.version.cuda}")
        if not torch.cuda.is_available() or torch.cuda.get_device_name(0)!="NVIDIA A40":
            raise RuntimeError("authorized NVIDIA A40 CUDA device is not available")

        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        before=gpu_used_mib()

        pipe=ZImagePipeline.from_pretrained(
            str(model_dir),
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=False,
        )
        qual["load_cpu_sec"]=round(time.perf_counter()-t0,6)
        t1=time.perf_counter()
        pipe=pipe.to("cuda")
        torch.cuda.synchronize()
        qual["to_cuda_sec"]=round(time.perf_counter()-t1,6)
        qual["nvidia_smi_after_load_mib"]=gpu_used_mib()
        qual["torch_peak_after_load_mib"]=round(torch.cuda.max_memory_reserved()/1024**2,3)

        torch.cuda.reset_peak_memory_stats()
        generator=torch.Generator(device="cuda").manual_seed(int(job["seed"]))
        t2=time.perf_counter()
        image=pipe(
            prompt=job["prompt"],
            negative_prompt=job["negative_prompt"],
            width=512,
            height=512,
            cfg_normalization=False,
            num_inference_steps=50,
            guidance_scale=4.0,
            generator=generator,
        ).images[0]
        torch.cuda.synchronize()
        inference_sec=time.perf_counter()-t2
        total_elapsed=time.perf_counter()-t0
        peak=max(
            float(torch.cuda.max_memory_reserved()/1024**2),
            float(gpu_used_mib() or 0),
            float(before or 0),
        )
        artifact=out_root/(args.job_id+"_512.png")
        image.save(artifact)
        runtime={
            "torch":torch.__version__,
            "torch_cuda":torch.version.cuda,
            "diffusers":__import__("diffusers").__version__,
            "gpu":torch.cuda.get_device_name(0),
            "mode":"FULL_GPU_BF16",
            "width":512,
            "height":512,
            "num_inference_steps":50,
            "guidance_scale":4.0,
            "cfg_normalization":False,
            "negative_prompt_applied":True,
            "inference_sec":round(inference_sec,6),
        }
        manifest=build_output_manifest(
            request=qual["request"],
            artifact_path=artifact,
            elapsed_sec=total_elapsed,
            gpu_peak_memory_mb=peak,
            runtime=runtime,
        )
        cost=build_cost_entry(
            qualification=qual,
            elapsed_sec=total_elapsed,
            passed=True,
            asset_id=manifest["asset_id"],
        )
        evidence={
            **qual,
            "status":"PASS",
            "started_unix":started,
            "finished_unix":time.time(),
            "elapsed_sec":round(total_elapsed,6),
            "output_manifest":manifest,
            "cost_entry":cost,
        }
        atomic_json(evidence_path,evidence)
        print(json.dumps({"status":"PASS","evidence":str(evidence_path),"manifest":manifest,"cost_entry":cost},ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        elapsed=time.perf_counter()-t0
        cost=build_cost_entry(
            qualification=qual,
            elapsed_sec=elapsed,
            passed=False,
            asset_id=None,
        )
        evidence={
            **qual,
            "status":"FAILED",
            "started_unix":started,
            "finished_unix":time.time(),
            "elapsed_sec":round(elapsed,6),
            "failure_type":type(exc).__name__,
            "failure":str(exc),
            "traceback":traceback.format_exc(),
            "cost_entry":cost,
        }
        atomic_json(evidence_path,evidence)
        print(json.dumps({"status":"FAILED","evidence":str(evidence_path),"failure_type":type(exc).__name__,"failure":str(exc),"cost_entry":cost},ensure_ascii=False,sort_keys=True),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
