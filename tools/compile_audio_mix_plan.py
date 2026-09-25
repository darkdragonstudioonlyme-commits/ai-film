#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.audio_mix_plan import compile_audio_mix_plan

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--language",required=True)
    ap.add_argument("--media-index",default="projects/slice01/audio/media_index.json")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    cues=json.loads((ROOT/"projects/slice01/audio/cue_sheet.json").read_text(encoding="utf-8"))
    policy=json.loads((ROOT/"projects/slice01/audio/mix_policy.json").read_text(encoding="utf-8"))
    idx_path=Path(args.media_index)
    if not idx_path.is_absolute(): idx_path=ROOT/idx_path
    index=json.loads(idx_path.read_text(encoding="utf-8"))
    plan=compile_audio_mix_plan(
        timing,shots,cues,
        language=args.language,
        dialogue_assets=index.get("dialogue_audio",{}),
        target=policy["target"],
    )
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"language":args.language,"status":plan["status"],"blockers":len(plan["blockers"]),"execution_permitted":plan["execution_permitted"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
