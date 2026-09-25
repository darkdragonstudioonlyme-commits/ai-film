#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.script_engine import validate_screenplay_against_shots, validate_source_rights

def main():
    screenplay=json.loads((ROOT/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    rights=json.loads((ROOT/"projects/slice01/rights/rights_register.json").read_text(encoding="utf-8"))
    normalized=validate_source_rights(screenplay,rights["records"])
    normalized=validate_screenplay_against_shots(screenplay,shots)
    print(json.dumps({
        "project_id":normalized["project_id"],
        "scenes":len(normalized["scenes"]),
        "beats":len(normalized["beat_ids"]),
        "dialogue":len(normalized["dialogue_ids"]),
        "duration_sec":normalized["target_duration_sec"],
        "source_rights_id":normalized["source"]["rights_id"],
    },sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
