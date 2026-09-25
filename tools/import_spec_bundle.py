#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.spec_transport import import_spec_bundle

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bundle-dir",required=True)
    ap.add_argument("--dest-root",required=True)
    args=ap.parse_args()
    result=import_spec_bundle(Path(args.bundle_dir),Path(args.dest_root))
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
