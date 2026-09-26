#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.wan22_ti2v_live import (
    build_generate_argv,
    build_smoke_evidence,
    validate_local_inputs,
    validate_smoke_spec,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path,value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    tmp.replace(path)


def gpu_used_mib() -> float:
    try:
        out=subprocess.check_output(
            ["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],
            text=True,timeout=5,
        )
        return max(float(x.strip()) for x in out.splitlines() if x.strip())
    except Exception:
        return 0.0


def ffprobe(path: Path) -> dict:
    try:
        out=subprocess.check_output([
            "ffprobe","-v","error",
            "-show_entries","stream=codec_name,width,height,r_frame_rate",
            "-show_entries","format=duration",
            "-of","json",str(path)
        ],text=True,timeout=30)
        return json.loads(out)
    except Exception as exc:
        return {"error":f"{type(exc).__name__}: {exc}"}


def select_job(spec: dict, probe_job_id: str) -> dict:
    rows=[r for r in spec.get("jobs",[]) if r.get("probe_job_id")==probe_job_id]
    if len(rows)!=1:
        raise SystemExit("unknown/duplicate Wan quality probe job")
    return rows[0]


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--probe-job-id",required=True)
    ap.add_argument("--max-runtime-sec",type=float)
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--wan-repo-dir")
    ap.add_argument("--model-dir")
    ap.add_argument("--reference-image")
    ap.add_argument("--out-root",default="/workspace/runs/wan22-quality-live")
    args=ap.parse_args()

    spec=load(ROOT/"model-evaluations/slice01/video/wan22_quality_probe_sc01_sh04.json")
    row=select_job(spec,args.probe_job_id)
    merged={k:v for k,v in spec.items() if k!="jobs"}
    merged["smoke_id"]=row["probe_job_id"]
    merged["reference_image_sha256"]=row["reference_image_sha256"]
    merged["reference_role"]=row["reference_role"]
    merged["max_runtime_sec"]=float(row["max_runtime_sec"])
    if args.max_runtime_sec is not None:
        if args.max_runtime_sec<=0 or args.max_runtime_sec>float(row["max_runtime_sec"]):
            raise SystemExit("--max-runtime-sec exceeds probe job cap")
        merged["max_runtime_sec"]=float(args.max_runtime_sec)

    plan=validate_smoke_spec(
        merged,
        matrix=load(ROOT/"model-evaluations/slice01/model_matrix.json"),
        gpu_session=load(ROOT/"projects/slice01/runtime/gpu_session.json"),
    )
    plan["probe_id"]=spec["probe_id"]
    plan["probe_job_id"]=row["probe_job_id"]
    plan["reference_model_id"]=row["reference_model_id"]
    plan["quality_status"]="NOT_EVALUATED"
    if not args.execute:
        print(json.dumps(plan,ensure_ascii=False,sort_keys=True))
        return 0
    if not args.wan_repo_dir or not args.model_dir or not args.reference_image:
        ap.error("--execute requires --wan-repo-dir --model-dir --reference-image")

    wan_repo=Path(args.wan_repo_dir).resolve()
    model_dir=Path(args.model_dir).resolve()
    reference_image=Path(args.reference_image).resolve()
    validate_local_inputs(merged,wan_repo_dir=wan_repo,model_dir=model_dir,reference_image=reference_image)

    expected_code=merged["code_revision"]
    head=subprocess.check_output(["git","-C",str(wan_repo),"rev-parse","HEAD"],text=True,timeout=10).strip()
    if head!=expected_code:
        raise RuntimeError(f"Wan2.2 runtime revision drift: {head}")
    marker=model_dir/".aifilm_model_revision"
    if not marker.is_file() or marker.read_text().strip()!=merged["model_revision"]:
        raise RuntimeError("Wan2.2 model revision marker missing/drifted")

    out_dir=Path(args.out_root).resolve()/row["probe_job_id"]
    out_dir.mkdir(parents=True,exist_ok=True)
    output=out_dir/(row["probe_job_id"]+".mp4")
    evidence_path=out_dir/"evidence.json"
    stdout_path=out_dir/"runner.stdout.log"
    stderr_path=out_dir/"runner.stderr.log"
    atomic_json(evidence_path,{**plan,"status":"STARTED"})

    argv=build_generate_argv(
        merged,
        python_exe=sys.executable,
        wan_repo_dir=wan_repo,
        model_dir=model_dir,
        reference_image=reference_image,
        output_file=output,
    )
    peak=gpu_used_mib()
    stop=threading.Event()
    def sample_gpu():
        nonlocal peak
        while not stop.wait(.5):
            peak=max(peak,gpu_used_mib())
    sampler=threading.Thread(target=sample_gpu,daemon=True)
    sampler.start()
    started=time.perf_counter()
    rc=124
    failure=None
    try:
        with stdout_path.open("w",encoding="utf-8") as out, stderr_path.open("w",encoding="utf-8") as err:
            proc=subprocess.Popen(argv,cwd=wan_repo,stdout=out,stderr=err,text=True)
            try:
                rc=proc.wait(timeout=float(merged["max_runtime_sec"]))
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=30); failure="TIMEOUT"
    except Exception as exc:
        failure=f"{type(exc).__name__}: {exc}"
    finally:
        elapsed=time.perf_counter()-started
        stop.set(); sampler.join(timeout=3)
        peak=max(peak,gpu_used_mib())

    ev=build_smoke_evidence(
        plan=plan,
        output_file=output,
        elapsed_sec=elapsed,
        peak_vram_mib=peak,
        ffprobe=ffprobe(output) if output.is_file() else {},
        returncode=rc,
        pass_status="PASS_RUNTIME_QUALITY_PROBE",
    )
    ev["probe_id"]=spec["probe_id"]
    ev["probe_job_id"]=row["probe_job_id"]
    ev["reference_model_id"]=row["reference_model_id"]
    ev["argv"]=argv
    ev["stdout_log"]=str(stdout_path)
    ev["stderr_log"]=str(stderr_path)
    ev["quality_status"]="NOT_EVALUATED"
    if failure:
        ev["failure"]=failure
    if ev["status"]=="FAILED" and stderr_path.is_file():
        ev["stderr_tail"]=stderr_path.read_text(encoding="utf-8",errors="replace")[-4000:]
    atomic_json(evidence_path,ev)
    print(json.dumps({"status":ev["status"],"evidence":str(evidence_path),"output":ev.get("output")},sort_keys=True))
    return 0 if ev["status"]=="PASS_RUNTIME_QUALITY_PROBE" else 2


if __name__=="__main__":
    raise SystemExit(main())