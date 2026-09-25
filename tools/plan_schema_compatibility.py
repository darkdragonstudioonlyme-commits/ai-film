#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.schema_compat import plan_schema_compatibility

TYPE_BY_PATH={
 "projects/slice01/project.json":"project",
 "projects/slice01/source/source_packet.json":"source",
 "projects/slice01/story/screenplay.json":"screenplay",
 "projects/slice01/continuity.json":"continuity",
 "projects/slice01/casting.json":"casting",
 "projects/slice01/shots/benchmark_shots.json":"shots",
 "projects/slice01/timing/timing.json":"timing",
 "projects/slice01/localization/dialogue_bundle.json":"localization",
 "projects/slice01/framing/reframe_policy.json":"framing",
 "projects/slice01/lipsync/policy.json":"lipsync",
 "projects/slice01/audio/cue_sheet.json":"audio_cues",
 "projects/slice01/audio/mix_policy.json":"audio_mix",
 "projects/slice01/qc_policy.json":"qc",
 "projects/slice01/rights/publication_policy.json":"publication_policy",
 "projects/slice01/subtitles/layout_policy.json":"subtitle_layout",
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="projects/slice01/schema_compatibility.json")
    args=ap.parse_args()
    package=json.loads((ROOT/"projects/slice01/production_spec_package.json").read_text(encoding="utf-8"))
    docs={}
    for entry in package["entries"]:
        path=entry["path"]
        docs[path]={"document_type":TYPE_BY_PATH[path],"value":json.loads((ROOT/path).read_text(encoding="utf-8"))}
    report=plan_schema_compatibility(docs)
    out=Path(args.out)
    if not out.is_absolute(): out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"upgrade_required":report["upgrade_required"],"unsupported":report["unsupported"],"mutations_applied":report["mutations_applied"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
