#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.audio_cues import validate_cue_sheet

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    sheet=json.loads((ROOT/"projects/slice01/audio/cue_sheet.json").read_text(encoding="utf-8"))
    total=sum(float(row["duration_sec"]) for row in timing["shots"])
    result=validate_cue_sheet(sheet,total_duration_sec=total)
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"cues":len(result["cues"]),"blockers":len(result["blockers"])},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
