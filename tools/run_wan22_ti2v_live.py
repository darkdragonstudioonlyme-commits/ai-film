#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.wan22_ti2v_live import (
    CODE_REVISION,
    Wan22TI2VError,
    build_generate_argv,
    build_smoke_evidence,
    validate_local_inputs,
    validate_smoke_spec,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def gpu_used_mib() -> float:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True,
            timeout=5,
        )
        return max(float(x.strip()) for x in out.splitlines() if x.strip())
    except Exception:
        return 0.0


def ffprobe(path: Path) -> dict:
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "stream=codec_name,width,height,r_frame_rate",
                "-show_entries", "format=duration",
                "-of", "json", str(path),
            ],
            text=True,
            timeout=30,
        )
        return json.loads(out)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    ap = argparse.ArgumentParser(description="Plan or execute a bounded Wan2.2 TI2V-5B A40 technical smoke.")
    ap.add_argument("--smoke-id", required=True)
    ap.add_argument("--spec-path", default="model-evaluations/slice01/video/wan22_ti2v_smoke.json")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--max-runtime-sec", type=float)
    ap.add_argument("--wan-repo-dir")
    ap.add_argument("--model-dir")
    ap.add_argument("--reference-image")
    ap.add_argument("--out-root", default="/workspace/runs/wan22-ti2v-live")
    args = ap.parse_args()

    spec_path=Path(args.spec_path)
    if not spec_path.is_absolute():
        spec_path=ROOT/spec_path
    spec=load(spec_path)
    if spec.get("smoke_id") != args.smoke_id:
        raise SystemExit("unknown Wan2.2 smoke id")
    if args.max_runtime_sec is not None:
        if args.max_runtime_sec <= 0 or args.max_runtime_sec > float(spec["max_runtime_sec"]):
            raise SystemExit("--max-runtime-sec must be positive and cannot exceed the smoke spec cap")
        spec = {**spec, "max_runtime_sec": float(args.max_runtime_sec)}
    matrix = load(ROOT / "model-evaluations/slice01/model_matrix.json")
    gpu_session = load(ROOT / "projects/slice01/runtime/gpu_session.json")
    plan = validate_smoke_spec(spec, matrix=matrix, gpu_session=gpu_session)
    plan["spec_path"]=str(spec_path)
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, sort_keys=True))
        return 0

    if not args.wan_repo_dir or not args.model_dir or not args.reference_image:
        ap.error("--execute requires --wan-repo-dir --model-dir --reference-image")
    wan_repo = Path(args.wan_repo_dir).resolve()
    model_dir = Path(args.model_dir).resolve()
    reference_image = Path(args.reference_image).resolve()
    validate_local_inputs(spec, wan_repo_dir=wan_repo, model_dir=model_dir, reference_image=reference_image)

    head = subprocess.check_output(["git", "-C", str(wan_repo), "rev-parse", "HEAD"], text=True, timeout=10).strip()
    if head != CODE_REVISION:
        raise Wan22TI2VError(f"Wan2.2 runtime revision drift: {head}")
    marker = model_dir / ".aifilm_model_revision"
    if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != spec["model_revision"]:
        raise Wan22TI2VError("Wan2.2 model revision marker missing/drifted")

    out_dir = Path(args.out_root).resolve() / args.smoke_id
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / f"{args.smoke_id}.mp4"
    evidence_path = out_dir / "evidence.json"
    stdout_path = out_dir / "runner.stdout.log"
    stderr_path = out_dir / "runner.stderr.log"
    atomic_json(evidence_path, {**plan, "status": "STARTED"})

    argv = build_generate_argv(
        spec,
        python_exe=sys.executable,
        wan_repo_dir=wan_repo,
        model_dir=model_dir,
        reference_image=reference_image,
        output_file=output_file,
    )
    peak = gpu_used_mib()
    stop = threading.Event()

    def sample_gpu():
        nonlocal peak
        while not stop.wait(0.5):
            peak = max(peak, gpu_used_mib())

    sampler = threading.Thread(target=sample_gpu, daemon=True)
    sampler.start()
    started = time.perf_counter()
    returncode = 124
    failure = None
    try:
        with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
            proc = subprocess.Popen(argv, cwd=wan_repo, stdout=out, stderr=err, text=True)
            try:
                returncode = proc.wait(timeout=float(spec["max_runtime_sec"]))
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=30)
                failure = "TIMEOUT"
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
    finally:
        elapsed = time.perf_counter() - started
        stop.set()
        sampler.join(timeout=3)
        peak = max(peak, gpu_used_mib())

    evidence = build_smoke_evidence(
        plan=plan,
        output_file=output_file,
        elapsed_sec=elapsed,
        peak_vram_mib=peak,
        ffprobe=ffprobe(output_file) if output_file.is_file() else {},
        returncode=returncode,
    )
    evidence["argv"] = argv
    evidence["stdout_log"] = str(stdout_path)
    evidence["stderr_log"] = str(stderr_path)
    if failure:
        evidence["failure"] = failure
    if evidence["status"] == "FAILED" and stderr_path.is_file():
        evidence["stderr_tail"] = stderr_path.read_text(encoding="utf-8", errors="replace")[-4000:]
    atomic_json(evidence_path, evidence)
    print(json.dumps({"status": evidence["status"], "evidence": str(evidence_path), "output": evidence.get("output")}, ensure_ascii=False, sort_keys=True))
    return 0 if evidence["status"] == "PASS_RUNTIME_SMOKE" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        traceback.print_exc()
        raise