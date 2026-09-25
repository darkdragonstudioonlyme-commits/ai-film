#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from film.production_package import build_production_spec_package, verify_production_spec_package

DEFAULT_SLICE01_INPUTS=[
 "projects/slice01/project.json",
 "projects/slice01/source/source_packet.json",
 "projects/slice01/story/screenplay.json",
 "projects/slice01/continuity.json",
 "projects/slice01/casting.json",
 "projects/slice01/shots/benchmark_shots.json",
 "projects/slice01/timing/timing.json",
 "projects/slice01/localization/dialogue_bundle.json",
 "projects/slice01/framing/reframe_policy.json",
 "projects/slice01/lipsync/policy.json",
 "projects/slice01/audio/cue_sheet.json",
 "projects/slice01/audio/mix_policy.json",
 "projects/slice01/qc_policy.json",
 "projects/slice01/rights/publication_policy.json",
 "projects/slice01/subtitles/layout_policy.json",
]

def main() -> int:
    ap=argparse.ArgumentParser(description="Build/verify a portable spec-only production package manifest.")
    ap.add_argument("--project-id",default="slice01")
    ap.add_argument("--out",default="projects/slice01/production_spec_package.json")
    args=ap.parse_args()
    package=build_production_spec_package(ROOT,DEFAULT_SLICE01_INPUTS,project_id=args.project_id)
    verified=verify_production_spec_package(ROOT,package)
    if verified["status"]!="PASS":
        raise SystemExit("production package self-verification failed")
    out=Path(args.out)
    if not out.is_absolute():
        out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(package,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":package["status"],
        "entry_count":package["entry_count"],
        "package_digest":package["package_digest"],
        "verified":verified["status"],
    },sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
