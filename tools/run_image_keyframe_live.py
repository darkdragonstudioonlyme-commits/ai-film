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

from film.image_keyframe_live import build_evidence,select_probe_job,validate_probe_job
from film.flux2_klein_live import validate_model_dir as validate_flux_dir
from film.z_image_live import validate_model_dir as validate_z_dir


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path,value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    tmp.replace(path)


def gpu_used_mib() -> float:
    try:
        out=subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True,timeout=5)
        return max(float(x.strip()) for x in out.splitlines() if x.strip())
    except Exception:
        return 0.0


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--probe-job-id",required=True)
    ap.add_argument("--max-runtime-sec",type=float)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--model-dir")
    ap.add_argument("--out-root",default="/workspace/runs/image-keyframe-live")
    args=ap.parse_args()

    spec=load(ROOT/"model-evaluations/slice01/video/keyframe_probe_sc01_sh04.json")
    job=select_probe_job(spec,args.probe_job_id)
    if args.max_runtime_sec is not None:
        if args.max_runtime_sec<=0 or args.max_runtime_sec>float(job.get("max_runtime_sec",600)):
            raise SystemExit("--max-runtime-sec exceeds spec cap")
        job={**job,"max_runtime_sec":float(args.max_runtime_sec)}
    plan=validate_probe_job(
        spec,job,
        matrix=load(ROOT/"model-evaluations/slice01/model_matrix.json"),
        resources=load(ROOT/"model-evaluations/slice01/resource_profiles.json"),
        worker=load(ROOT/"projects/slice01/runtime/worker_runpod_a40.json"),
        gpu_session=load(ROOT/"projects/slice01/runtime/gpu_session.json"),
    )
    if not args.execute:
        print(json.dumps(plan,ensure_ascii=False,sort_keys=True))
        return 0
    if not args.model_dir:
        ap.error("--execute requires --model-dir")

    model_dir=Path(args.model_dir).resolve()
    if job["model_id"]=="flux2-klein-4b":
        validate_flux_dir(model_dir)
    else:
        validate_z_dir(model_dir)

    import torch
    if torch.__version__!="2.8.0+cu128" or not torch.cuda.is_available() or torch.cuda.get_device_name(0)!="NVIDIA A40":
        raise RuntimeError("image keyframe runtime drift")
    out_dir=Path(args.out_root).resolve()/args.probe_job_id
    out_dir.mkdir(parents=True,exist_ok=True)
    artifact=out_dir/(args.probe_job_id+".png")
    evidence_path=out_dir/"evidence.json"
    atomic_json(evidence_path,{**plan,"status":"STARTED"})

    started=time.perf_counter()
    peak=gpu_used_mib()
    try:
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        if job["model_id"]=="flux2-klein-4b":
            from diffusers import Flux2KleinPipeline
            pipe=Flux2KleinPipeline.from_pretrained(str(model_dir),torch_dtype=torch.bfloat16).to("cuda")
            gen=torch.Generator(device="cuda").manual_seed(int(job["seed"]))
            image=pipe(
                prompt=job["prompt"],
                width=job["width"],height=job["height"],
                num_inference_steps=job["num_inference_steps"],
                guidance_scale=job["guidance_scale"],
                generator=gen,
            ).images[0]
        else:
            from diffusers import ZImagePipeline
            pipe=ZImagePipeline.from_pretrained(str(model_dir),torch_dtype=torch.bfloat16,low_cpu_mem_usage=False).to("cuda")
            gen=torch.Generator(device="cuda").manual_seed(int(job["seed"]))
            image=pipe(
                prompt=job["prompt"],negative_prompt=job["negative_prompt"],
                width=job["width"],height=job["height"],
                num_inference_steps=job["num_inference_steps"],
                guidance_scale=job["guidance_scale"],
                cfg_normalization=job["cfg_normalization"],
                generator=gen,
            ).images[0]
        torch.cuda.synchronize()
        peak=max(peak,float(torch.cuda.max_memory_reserved()/1024**2),gpu_used_mib())
        image.save(artifact)
        ev=build_evidence(plan,artifact=artifact,elapsed_sec=time.perf_counter()-started,peak_vram_mib=peak)
        atomic_json(evidence_path,ev)
        print(json.dumps({"status":ev["status"],"evidence":str(evidence_path),"output":ev.get("output")},sort_keys=True))
        return 0
    except Exception as exc:
        ev=build_evidence(plan,artifact=artifact,elapsed_sec=time.perf_counter()-started,peak_vram_mib=max(peak,gpu_used_mib()),returncode=2)
        ev["failure_type"]=type(exc).__name__; ev["failure"]=str(exc); ev["traceback"]=traceback.format_exc()
        atomic_json(evidence_path,ev)
        print(json.dumps({"status":"FAILED","failure":str(exc),"evidence":str(evidence_path)},sort_keys=True),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
