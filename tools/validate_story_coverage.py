#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.story_coverage import compile_story_shot_coverage

def main():
    screenplay=json.loads((ROOT/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    report=compile_story_shot_coverage(screenplay,timing,shots)
    print(json.dumps({"status":report["status"],"duration_sec":report["duration_sec"],"beats":len(report["beat_coverage"]),"shots":len(report["shots"]),"blockers":report["blockers"]},sort_keys=True))
    return 0 if report["status"]=="COMPLETE" else 2
if __name__=="__main__": raise SystemExit(main())
