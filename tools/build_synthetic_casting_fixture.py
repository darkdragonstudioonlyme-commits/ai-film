#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.synthetic_fixtures import build_synthetic_casting_outputs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--manifest",required=True)
    args=ap.parse_args()
    jobs=json.loads((ROOT/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))["jobs"]
    outputs=build_synthetic_casting_outputs(jobs,Path(args.out_dir))
    out=Path(args.manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"schema_version":1,"fixture":True,"outputs":outputs},ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"fixture":True,"outputs":len(outputs)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
