#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.lipsync_plan import compile_lipsync_plan

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--language",required=True)
    ap.add_argument("--media-index",default="projects/slice01/lipsync/media_index.json")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    policy=json.loads((ROOT/"projects/slice01/lipsync/policy.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    idx_path=Path(args.media_index)
    if not idx_path.is_absolute(): idx_path=ROOT/idx_path
    index=json.loads(idx_path.read_text(encoding="utf-8"))
    plan=compile_lipsync_plan(
        policy,shots,language=args.language,
        selected_videos=index.get("videos",{}),
        dialogue_audio=index.get("dialogue_audio",{}),
    )
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"language":args.language,"status":plan["status"],"requests":len(plan["requests"]),"skipped":len(plan["skipped"]),"blockers":len(plan["blockers"])},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
