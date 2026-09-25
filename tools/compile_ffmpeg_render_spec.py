#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.render_compile import RenderCompileError,compile_ffmpeg_render_spec

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--edit-plan",required=True)
    ap.add_argument("--asset-catalog",required=True)
    ap.add_argument("--output-media",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    plan=json.loads(Path(args.edit_plan).read_text(encoding="utf-8"))
    catalog=json.loads(Path(args.asset_catalog).read_text(encoding="utf-8")).get("assets",{})
    try:
        spec=compile_ffmpeg_render_spec(plan,catalog,output_path=args.output_media)
    except RenderCompileError as exc:
        print("RENDER_COMPILE_BLOCKED: "+str(exc),file=sys.stderr)
        return 2
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(spec,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"spec_digest":spec["spec_digest"],"execution_permitted":spec["execution_permitted"],"inputs":len(spec["video_inputs"])+len(spec["audio_inputs"])},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
