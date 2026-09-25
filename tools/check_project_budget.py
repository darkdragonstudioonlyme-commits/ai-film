#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.cost_ledger import budget_decision

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ledger",default="projects/slice01/runtime/cost_ledger.json")
    ap.add_argument("--policy",default="projects/slice01/runtime/cost_policy.json")
    ap.add_argument("--proposed-usd",type=float,default=0)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    lpath=Path(args.ledger); ppath=Path(args.policy)
    if not lpath.is_absolute(): lpath=ROOT/lpath
    if not ppath.is_absolute(): ppath=ROOT/ppath
    ledger=json.loads(lpath.read_text(encoding="utf-8"))
    policy=json.loads(ppath.read_text(encoding="utf-8"))
    result=budget_decision(ledger,budget_usd=policy["current_authorized_budget_usd"],proposed_charge_usd=args.proposed_usd)
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"allowed":result["allowed"],"spent_usd":result["spent_usd"],"projected_usd":result["projected_usd"]},sort_keys=True))
    return 0 if result["allowed"] else 2
if __name__=="__main__": raise SystemExit(main())
