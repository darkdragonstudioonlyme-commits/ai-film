#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.casting_ingest import ingest_casting_outputs

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outputs",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    contract=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
    jobs=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]
    manifests=json.loads(Path(args.outputs).read_text(encoding="utf-8")).get("outputs",[])
    updated,index,public=ingest_casting_outputs(contract,jobs,manifests)
    out=Path(args.out_dir)
    if not out.is_absolute(): out=ROOT/out
    write(out/"reference_contract.updated.json",updated)
    write(out/"reference_index.json",index)
    write(out/"blind_items.bound.json",public)
    print(json.dumps({"status":updated["status"],"assets":len(index["assets"]),"index_status":index["status"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
