#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.decision_templates import get_template, import_cost_rows
from film.decision_ledger import aggregate_benchmark_records

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--template",required=True)
    ap.add_argument("--records",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    template=get_template(args.template)
    raw=json.loads(Path(args.records).read_text(encoding="utf-8")).get("records",[])
    records=import_cost_rows(raw)
    report=aggregate_benchmark_records(records,expected_models=set(template["expected_models"]),expected_shots={row["shot_id"] for row in records})
    report["template"]=args.template
    report["decision_scope"]=template["decision_scope"]
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"selection_authorized":report["selection_authorized"],"template":args.template},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
