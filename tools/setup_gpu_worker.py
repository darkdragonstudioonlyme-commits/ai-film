#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser=argparse.ArgumentParser(description="Plan the pinned GPU worker setup. This tool does not launch or install.")
    parser.add_argument("--out",default="/tmp/aifilm-gpu-worker-plan.json")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    if args.apply:
        parser.error("--apply is intentionally disabled until a rented GPU host is explicitly authorized")
    lock_path=ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json"
    req_path=ROOT/"model-evaluations/slice01/gpu-worker/requirements-base.lock.txt"
    lock=json.loads(lock_path.read_text(encoding="utf-8"))
    commands=[
      "nvidia-smi",
      "python3 --version",
      "df -h /",
      "python3 -m venv /opt/aifilm/venv",
      "/opt/aifilm/venv/bin/python -m pip install --upgrade pip",
      "/opt/aifilm/venv/bin/python -m pip install -r requirements-base.lock.txt",
      "/opt/aifilm/venv/bin/python -c 'import torch; print(torch.__version__, torch.cuda.is_available())'",
    ]
    plan={
      "schema_version":1,
      "mode":"DRY_RUN",
      "execution_ready":False,
      "runtime_lock_sha256":sha256(lock_path),
      "requirements_lock_sha256":sha256(req_path),
      "target":lock["target"],
      "blockers":lock["blockers"],
      "commands":commands,
      "note":"Commands are a plan only. CUDA-compatible torch source and model runtimes are pinned after rented-host preflight.",
    }
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(plan,ensure_ascii=False,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
