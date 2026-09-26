#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.scored_media_promotion import build_scored_benchmark_plan


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap=argparse.ArgumentParser(description="Build a fail-closed multi-shot benchmark promotion plan from complete owner scores.")
    ap.add_argument("--owner-summary",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    owner=load(Path(args.owner_summary))
    shots=load(ROOT/"projects/slice01/shots/benchmark_shots.json")
    shot_ids=[row["shot_id"] for row in shots]
    plan=build_scored_benchmark_plan(owner,benchmark_shot_ids=shot_ids)

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":plan["status"],
        "motion_status":plan["motion"]["status"],
        "selected_reference_model_id":plan["motion"].get("selected_reference_model_id"),
        "voice_overall_mean":plan["voice"]["overall_mean"],
        "out":str(out),
    },ensure_ascii=False,sort_keys=True))
    return 0 if plan["status"]=="READY_FOR_MULTI_SHOT_BENCHMARK_CONFIGURATION" else 3


if __name__=="__main__":
    raise SystemExit(main())