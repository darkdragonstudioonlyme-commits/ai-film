#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.rights import publication_gate

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--assets",required=True)
    ap.add_argument("--creative-qc-pass",action="store_true")
    ap.add_argument("--technical-qc-pass",action="store_true")
    ap.add_argument("--provenance-complete",action="store_true")
    ap.add_argument("--distribution-rules-checked-on")
    ap.add_argument("--as-of",required=True)
    ap.add_argument("--owner-approved",action="store_true")
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    assets=json.loads(Path(args.assets).read_text(encoding="utf-8")).get("assets",[])
    policy=json.loads((ROOT/"projects/slice01/rights/publication_policy.json").read_text(encoding="utf-8"))
    register=json.loads((ROOT/"projects/slice01/rights/rights_register.json").read_text(encoding="utf-8"))
    result=publication_gate(
        selected_assets=assets,
        rights_records=register["records"],
        creative_qc_pass=args.creative_qc_pass,
        technical_qc_pass=args.technical_qc_pass,
        provenance_complete=args.provenance_complete,
        distribution_rules_checked_on=args.distribution_rules_checked_on,
        as_of=args.as_of,
        required_subjects=policy["required_subjects"],
        owner_approved=args.owner_approved,
    )
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"blockers":len(result["blockers"]),"publish_action_performed":result["publish_action_performed"]},sort_keys=True))
    return 0 if result["status"]!="BLOCKED" else 2
if __name__=="__main__": raise SystemExit(main())
