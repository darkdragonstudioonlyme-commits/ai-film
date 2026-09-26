#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.longform_review import ingest_owner_review, calibration_status

def load(p: Path): return json.loads(p.read_text(encoding="utf-8"))
def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--packet",required=True)
    ap.add_argument("--completed",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    policy=load(ROOT/"model-evaluations/auto-eval/longform_review_policy.json")
    result=ingest_owner_review(policy,load(Path(a.packet)),load(Path(a.completed)))
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    dataset=ROOT/policy["calibration"]["dataset_path"]
    dataset.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    if dataset.is_file():
        rows=[json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows=[r for r in rows if r.get("review_id")!=result["review_id"]]+[result]
    dataset.write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows),encoding="utf-8")
    status=calibration_status(policy,rows)
    print(json.dumps({"status":"LONGFORM_OWNER_REVIEW_INGESTED","review_id":result["review_id"],"calibration":status,"out":str(out)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
