#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.qc import acceptance_decision

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--record",required=True)
    ap.add_argument("--policy",default="projects/slice01/qc_policy.json")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    record=json.loads(Path(args.record).read_text(encoding="utf-8"))
    policy_path=Path(args.policy)
    if not policy_path.is_absolute(): policy_path=ROOT/policy_path
    policy=json.loads(policy_path.read_text(encoding="utf-8"))
    result=acceptance_decision(record,required_scores=policy["required_scores"],severe_tags=set(policy["severe_failure_tags"]))
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"accepted":result["accepted"],"blockers":len(result["blockers"]),"selection_authorized":result["selection_authorized"]},sort_keys=True))
    return 0 if result["accepted"] else 2
if __name__=="__main__": raise SystemExit(main())
