#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.continuity_expectations import compile_continuity_expectations

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="projects/slice01/continuity_expectations.json")
    args=ap.parse_args()
    ledger=json.loads((ROOT/"projects/slice01/continuity.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    report=compile_continuity_expectations(ledger,shots)
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"shots":len(report["shots"])},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
