#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.auto_eval import aggregate_auto_eval

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main()->int:
    ap=argparse.ArgumentParser(description="Aggregate normalized evaluator receipts into a fail-closed automatic take decision.")
    ap.add_argument("--stage",required=True)
    ap.add_argument("--asset-id",required=True)
    ap.add_argument("--receipt",action="append",default=[])
    ap.add_argument("--deterministic-metrics")
    ap.add_argument("--policy",default="model-evaluations/auto-eval/policy.json")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    receipts=[load(Path(path)) for path in args.receipt]
    deterministic=load(Path(args.deterministic_metrics)) if args.deterministic_metrics else {}
    result=aggregate_auto_eval(
        load(ROOT/args.policy),
        stage=args.stage,
        asset_id=args.asset_id,
        receipts=receipts,
        deterministic_metrics=deterministic,
    )
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"score":result.get("score"),"asset_id":result["asset_id"]},sort_keys=True))
    return 0 if result["status"]=="AUTO_SHORTLIST" else 2

if __name__=="__main__":
    raise SystemExit(main())
