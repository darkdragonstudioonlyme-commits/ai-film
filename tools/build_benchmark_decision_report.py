#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.decision_ledger import aggregate_benchmark_records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--records",required=True)
    ap.add_argument("--expected-model",action="append",default=[])
    ap.add_argument("--expected-shot",action="append",default=[])
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    records=json.loads(Path(args.records).read_text(encoding="utf-8")).get("records",[])
    report=aggregate_benchmark_records(records,expected_models=set(args.expected_model),expected_shots=set(args.expected_shot))
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"records":report["record_count"],"total_cost_usd":report["total_cost_usd"],"selection_authorized":report["selection_authorized"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
