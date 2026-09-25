#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.spec_transport import export_spec_bundle, verify_spec_bundle

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--package",default="projects/slice01/production_spec_package.json")
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    package_path=Path(args.package)
    if not package_path.is_absolute(): package_path=ROOT/package_path
    package=json.loads(package_path.read_text(encoding="utf-8"))
    out=Path(args.out_dir)
    manifest=export_spec_bundle(ROOT,package,out)
    verified=verify_spec_bundle(out)
    if verified["status"]!="PASS":
        raise SystemExit("bundle verification failed")
    print(json.dumps({"status":manifest["status"],"entry_count":manifest["entry_count"],"bundle_digest":manifest["bundle_digest"],"verified":verified["status"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
