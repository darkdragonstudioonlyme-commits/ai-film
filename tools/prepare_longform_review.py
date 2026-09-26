#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.longform_review import build_review_packet

def load(p: Path): return json.loads(p.read_text(encoding="utf-8"))
def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=["longform_rough_cut","final_cut"],required=True)
    ap.add_argument("--project-id",required=True)
    ap.add_argument("--media-qc",required=True)
    ap.add_argument("--auto-eval-summary-ref",action="append",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    policy=load(ROOT/"model-evaluations/auto-eval/longform_review_policy.json")
    packet=build_review_packet(policy,stage=a.stage,project_id=a.project_id,media_qc=load(Path(a.media_qc)),auto_eval_summary_refs=a.auto_eval_summary_ref)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"LONGFORM_REVIEW_PACKET_READY","review_id":packet["review_id"],"out":str(out)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
