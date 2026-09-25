#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.delivery import build_delivery_manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--deliverables",required=True)
    ap.add_argument("--publication-gate",required=True)
    ap.add_argument("--creative-qc-ref",required=True)
    ap.add_argument("--rights-gate-ref",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    deliverables=json.loads(Path(args.deliverables).read_text(encoding="utf-8")).get("deliverables",[])
    pub=json.loads(Path(args.publication_gate).read_text(encoding="utf-8"))
    manifest=build_delivery_manifest(
        deliverables,
        publication_gate_status=pub["status"],
        creative_qc_ref=args.creative_qc_ref,
        rights_gate_ref=args.rights_gate_ref,
    )
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":manifest["status"],"variants":len(manifest["deliverables"]),"published":manifest["published"]},sort_keys=True))
    return 0 if manifest["status"]!="INCOMPLETE" else 2
if __name__=="__main__": raise SystemExit(main())
