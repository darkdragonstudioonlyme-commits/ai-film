#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",default="projects/slice01/casting/eval")
    args=ap.parse_args()
    contract=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
    out=Path(args.out_dir)
    if not out.is_absolute(): out=ROOT/out
    out.mkdir(parents=True,exist_ok=True)
    public=[]; private=[]
    for cid in sorted(contract["characters"]):
        for style in contract["styles"]:
            for slot in contract["reference_slots"]:
                raw=f"{cid}:{style}:{slot['slot']}"
                blind="cast_"+hashlib.sha256(raw.encode()).hexdigest()[:12]
                public.append({"blind_id":blind,"style":style,"slot":slot["slot"],"asset_id":None})
                private.append({"blind_id":blind,"character_id":cid,"style":style,"slot":slot["slot"]})
    (out/"blind_items.json").write_text(json.dumps({"schema_version":1,"items":public},indent=2)+"\n")
    (out/"blind_map_private.json").write_text(json.dumps({"schema_version":1,"mapping":private},indent=2)+"\n")
    with (out/"scores.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.writer(fh,lineterminator="\n"); w.writerow(["blind_id","identity_match","within_character_consistency","between_character_separation","style_quality","anatomy_artifact_free","overall","failure_tags","notes"])
        for row in public: w.writerow([row["blind_id"],"","","","","","","",""])
    print(json.dumps({"items":len(public),"characters":len(contract["characters"]),"styles":len(contract["styles"])}))
if __name__=="__main__": main()
