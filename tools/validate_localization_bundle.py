#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.localization import validate_localization_bundle

def main():
    bundle=json.loads((ROOT/"projects/slice01/localization/dialogue_bundle.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    expected={shot["dialogue_id"] for shot in shots if shot.get("dialogue_id")}
    budgets={row["dialogue_id"]:float(row["end_offset_sec"])-float(row["start_offset_sec"]) for row in timing["dialogue_cues"]}
    report=validate_localization_bundle(bundle,expected_dialogue_ids=expected,cue_budgets_sec=budgets)
    print(json.dumps({
        "status":report["status"],
        "lines":len(report["lines"]),
        "blockers":report["blockers"],
    },ensure_ascii=False,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
