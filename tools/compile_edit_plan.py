#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.edit_plan import compile_edit_plan

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--language",choices=["en","zh-CN","vi"],default="en")
    ap.add_argument("--aspect",choices=["9:16","16:9"],default="9:16")
    ap.add_argument("--selected-takes",default="projects/slice01/edit/selected_takes.json")
    ap.add_argument("--dialogue-tracks",default="projects/slice01/edit/dialogue_tracks.json")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    sel_path=Path(args.selected_takes)
    if not sel_path.is_absolute(): sel_path=ROOT/sel_path
    aud_path=Path(args.dialogue_tracks)
    if not aud_path.is_absolute(): aud_path=ROOT/aud_path
    selected=json.loads(sel_path.read_text(encoding="utf-8")).get("selected_takes",{})
    dialogue=json.loads(aud_path.read_text(encoding="utf-8")).get("tracks",{})
    subtitles={
        "en":"projects/slice01/timing/subtitles/en.srt",
        "zh-CN":"projects/slice01/timing/subtitles/zh-CN.srt",
        "vi":"projects/slice01/timing/subtitles/vi.srt",
    }
    plan=compile_edit_plan(timing,shots,selected_takes=selected,dialogue_tracks=dialogue,subtitle_tracks=subtitles,aspect=args.aspect,language=args.language)
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":plan["status"],"duration_sec":plan["duration_sec"],"blockers":len(plan["blockers"]),"render_authorized":plan["render_authorized"]},sort_keys=True))
    return 0 if plan["status"]=="READY_TO_RENDER" else 2
if __name__=="__main__": raise SystemExit(main())
