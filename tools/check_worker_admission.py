#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.admission import evaluate_admission

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--profile-id",required=True)
    ap.add_argument("--worker",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    profiles=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
    by={row["profile_id"]:row for row in profiles["profiles"]}
    if args.profile_id not in by:
        raise SystemExit("unknown profile")
    worker=json.loads(Path(args.worker).read_text(encoding="utf-8"))
    result=evaluate_admission(by[args.profile_id],worker)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"admitted":result["admitted"],"reasons":result["reasons"],"throughput_claimed":result["throughput_claimed"]},sort_keys=True))
    return 0 if result["admitted"] else 2
if __name__=="__main__": raise SystemExit(main())
