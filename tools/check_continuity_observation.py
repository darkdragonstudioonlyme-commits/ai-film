#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.continuity_expectations import diff_observed_state

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shot-id",required=True)
    ap.add_argument("--observed",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    expectations=json.loads((ROOT/"projects/slice01/continuity_expectations.json").read_text(encoding="utf-8"))
    by_id={row["shot_id"]:row for row in expectations["shots"]}
    if args.shot_id not in by_id:
        raise SystemExit("unknown shot id")
    observed=json.loads(Path(args.observed).read_text(encoding="utf-8"))
    result=diff_observed_state(by_id[args.shot_id],observed)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"mismatches":len(result["mismatches"]),"tags":result["suggested_failure_tags"]},sort_keys=True))
    return 0 if result["status"]=="MATCH" else 2
if __name__=="__main__": raise SystemExit(main())
