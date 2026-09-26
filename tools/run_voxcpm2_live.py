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

from film.voxcpm2_live import (
    SAMPLE_RATE_HZ,
    build_cost_entry,
    build_output_manifest,
    prepare_voxcpm2_qualification,
    validate_model_dir,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pick_request(request_id: str, request_file: Path | None=None) -> dict:
    source=request_file or (ROOT/"model-evaluations/slice01/voice/requests/requests.json")
    payload=load(source)
    rows=payload.get("requests")
    if not isinstance(rows,list):
        raise SystemExit(f"VoxCPM2 request file has no requests list: {source}")
    found=[row for row in rows if row.get("request_id")==request_id]
    if len(found)!=1:
        raise SystemExit(f"unknown/duplicate VoxCPM2 request: {request_id}")
    return found[0]


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
    ap=argparse.ArgumentParser(description="Plan or execute one exact VoxCPM2 Voice Design qualification request on the authorized RunPod A40.")
    ap.add_argument("--request-id",required=True)
    ap.add_argument("--request-file",help="optional JSON containing a requests array; defaults to canonical fixed packet")
    ap.add_argument("--max-runtime-sec",type=float,default=900.0)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--model-dir")
    ap.add_argument("--out-root",default="/workspace/runs/voxcpm2-live")
    args=ap.parse_args()

    request_file=None
    if args.request_file:
        request_file=Path(args.request_file)
        if not request_file.is_absolute():
            request_file=ROOT/request_file
        request_file=request_file.resolve()
        if not request_file.is_file():
            raise SystemExit(f"request file missing: {request_file}")
    request=pick_request(args.request_id,request_file=request_file)
    matrix=load(ROOT/"model-evaluations/slice01/model_matrix.json")
    config=load(ROOT/"model-evaluations/slice01/voice/voxcpm2_eval_config.json")
    live_runtime=load(ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json")
    proposal=load(ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json")
    execution_plan=load(ROOT/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json")
    rate_snapshot=load(ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json")
    authorization=load(ROOT/"model-evaluations/slice01/launch_authorization.active.json")
    cost_policy=load(ROOT/"projects/slice01/runtime/cost_policy.json")
    cost_ledger=load(ROOT/"projects/slice01/runtime/cost_ledger.json")
    qual=prepare_voxcpm2_qualification(
        request=request,
        matrix=matrix,
        config=config,
        live_runtime=live_runtime,
        proposal=proposal,
        execution_plan=execution_plan,
        rate_snapshot=rate_snapshot,
        authorization=authorization,
        cost_policy=cost_policy,
        cost_ledger=cost_ledger,
        max_runtime_sec=args.max_runtime_sec,
    )
    qual["request_source"]=str(request_file) if request_file else "model-evaluations/slice01/voice/requests/requests.json"
    if not args.execute:
        print(json.dumps(qual,ensure_ascii=False,sort_keys=True))
        return 0
    if not args.model_dir:
        ap.error("--execute requires --model-dir")

    model_dir=Path(args.model_dir).resolve()
    qual["model_dir"]=str(model_dir)
    qual["model_snapshot_shape"]=validate_model_dir(model_dir)
    out_dir=Path(args.out_root).resolve()/args.request_id
    out_dir.mkdir(parents=True,exist_ok=True)
    evidence_path=out_dir/"evidence.json"
    atomic_json(evidence_path,{**qual,"status":"STARTED"})

    started=time.time()
    t0=time.perf_counter()
    try:
        import numpy as np
        import soundfile as sf
        import torch
        import torchaudio
        from voxcpm import VoxCPM

        if torch.__version__!="2.8.0+cu128" or torchaudio.__version__!="2.8.0+cu128":
            raise RuntimeError(f"torch/torchaudio runtime drift: {torch.__version__} / {torchaudio.__version__}")
        if not torch.cuda.is_available() or torch.cuda.get_device_name(0)!="NVIDIA A40":
            raise RuntimeError("authorized NVIDIA A40 CUDA device is not available")

        torch.manual_seed(int(request["seed"]))
        torch.cuda.manual_seed_all(int(request["seed"]))
        np.random.seed(int(request["seed"]) % (2**32))
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        before=gpu_used_mib()

        model=VoxCPM.from_pretrained(
            str(model_dir),
            load_denoiser=False,
            local_files_only=True,
            optimize=False,
            device="cuda",
        )
        torch.cuda.synchronize()
        qual["load_sec"]=round(time.perf_counter()-t0,6)
        qual["nvidia_smi_after_load_mib"]=gpu_used_mib()
        qual["torch_peak_after_load_mib"]=round(torch.cuda.max_memory_reserved()/1024**2,3)

        torch.cuda.reset_peak_memory_stats()
        t1=time.perf_counter()
        wav=model.generate(
            text=request["model_input_text"],
            prompt_wav_path=None,
            prompt_text=None,
            reference_wav_path=None,
            cfg_value=float(request["cfg_value"]),
            inference_timesteps=int(request["inference_timesteps"]),
            normalize=False,
            denoise=False,
            retry_badcase=False,
        )
        torch.cuda.synchronize()
        inference_sec=time.perf_counter()-t1
        total_elapsed=time.perf_counter()-t0
        wav=np.asarray(wav,dtype=np.float32).reshape(-1)
        if wav.size<1 or not np.isfinite(wav).all():
            raise RuntimeError("VoxCPM2 returned invalid waveform")
        duration=wav.size/float(SAMPLE_RATE_HZ)
        peak=max(
            float(torch.cuda.max_memory_reserved()/1024**2),
            float(gpu_used_mib() or 0),
            float(before or 0),
        )
        audio_path=out_dir/(args.request_id+".wav")
        sf.write(audio_path,wav,SAMPLE_RATE_HZ,subtype="PCM_16")
        runtime={
            "package":"voxcpm==2.0.3",
            "torch":torch.__version__,
            "torchaudio":torchaudio.__version__,
            "gpu":torch.cuda.get_device_name(0),
            "load_denoiser":False,
            "optimize":False,
            "retry_badcase":False,
            "inference_sec":round(inference_sec,6),
        }
        manifest=build_output_manifest(
            request=request,
            audio_path=audio_path,
            duration_sec=duration,
            gpu_peak_memory_mb=peak,
            runtime=runtime,
        )
        cost=build_cost_entry(qualification=qual,elapsed_sec=total_elapsed,passed=True)
        evidence={
            **qual,
            "status":"PASS_RUNTIME",
            "started_unix":started,
            "finished_unix":time.time(),
            "elapsed_sec":round(total_elapsed,6),
            "output_manifest":manifest,
            "cue_fit":manifest["cue_fit"],
            "cost_entry":cost,
        }
        atomic_json(evidence_path,evidence)
        print(json.dumps({"status":"PASS_RUNTIME","evidence":str(evidence_path),"cue_fit":manifest["cue_fit"],"manifest":manifest,"cost_entry":cost},ensure_ascii=False,sort_keys=True))
        return 0
    except Exception as exc:
        elapsed=time.perf_counter()-t0
        cost=build_cost_entry(qualification=qual,elapsed_sec=elapsed,passed=False)
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
