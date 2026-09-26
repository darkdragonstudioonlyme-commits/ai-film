#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--execute",action="store_true")
    ap.add_argument("--out-root",default="/workspace/runs/auto-eval/video-20260926")
    args=ap.parse_args()
    pending=json.loads((ROOT/"model-evaluations/auto-eval/vbench_pending_20260926.json").read_text())
    lock=json.loads((ROOT/"model-evaluations/auto-eval/vbench_runtime_lock.json").read_text())
    argv=[
      f"{lock['venv']}/bin/python",
      str(ROOT/"tools/run_current_video_auto_eval.py"),
      "--asset-path-mode","pod",
      "--run-evaluator","vbench",
      "--vbench-python",f"{lock['venv']}/bin/python",
      "--vbench-repo",lock["code_dir"],
      "--out-root",args.out_root,
    ]
    for asset_id in pending["eligible_asset_ids"]:
        argv += ["--asset-id",asset_id]
    if args.execute:
        argv.append("--execute")
    if not args.execute:
        print(json.dumps({"status":"PLANNED","eligible_count":pending["eligible_count"],"argv":argv,"new_resource_creation_authorized":False},indent=2))
        return 0
    return subprocess.run(argv,cwd=ROOT).returncode

if __name__=="__main__":
    raise SystemExit(main())
