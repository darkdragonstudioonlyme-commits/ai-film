#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.reframe import compile_reframe_plan

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--media-index",default="projects/slice01/framing/media_index.json")
    ap.add_argument("--out",default="projects/slice01/framing/reframe_plan_16x9.json")
    args=ap.parse_args()
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    policy=json.loads((ROOT/"projects/slice01/framing/reframe_policy.json").read_text(encoding="utf-8"))
    idx_path=Path(args.media_index)
    if not idx_path.is_absolute(): idx_path=ROOT/idx_path
    index=json.loads(idx_path.read_text(encoding="utf-8"))
    plan=compile_reframe_plan(shots,policy,master_assets=index.get("master_assets",{}))
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":plan["status"],
        "shots":len(plan["shots"]),
        "fallback_to_rerender_count":plan["fallback_to_rerender_count"],
        "render_authorized":plan["render_authorized"],
    },sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
