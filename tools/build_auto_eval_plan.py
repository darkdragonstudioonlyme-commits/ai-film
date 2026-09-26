#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.auto_eval import build_eval_plan

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main()->int:
    ap=argparse.ArgumentParser(description="Build a fail-closed multi-model auto-evaluation plan.")
    ap.add_argument("--stage",required=True)
    ap.add_argument("--asset-id",required=True)
    ap.add_argument("--asset-path",required=True)
    ap.add_argument("--registry",default="model-evaluations/auto-eval/evaluator_registry.json")
    ap.add_argument("--policy",default="model-evaluations/auto-eval/policy.json")
    ap.add_argument("--out")
    args=ap.parse_args()
    registry=load(ROOT/args.registry)
    policy=load(ROOT/args.policy)
    plan=build_eval_plan(registry,policy,stage=args.stage,asset_id=args.asset_id,asset_path=args.asset_path)
    if args.out:
        out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(plan,ensure_ascii=False,sort_keys=True))
    return 0 if plan["status"]=="READY" else 3

if __name__=="__main__":
    raise SystemExit(main())
