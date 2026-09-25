#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from film.project_scaffold import build_project_scaffold

def main() -> int:
    ap=argparse.ArgumentParser(description="Create a clean project scaffold with no generated/runtime state.")
    ap.add_argument("--project-id",required=True)
    ap.add_argument("--title",required=True)
    ap.add_argument("--source-packet",required=True)
    ap.add_argument("--out-dir",required=True)
    args=ap.parse_args()
    source_path=Path(args.source_packet)
    if not source_path.is_absolute():
        source_path=ROOT/source_path
    source=json.loads(source_path.read_text(encoding="utf-8"))
    scaffold=build_project_scaffold(project_id=args.project_id,title=args.title,source_packet=source)
    out=Path(args.out_dir)
    if not out.is_absolute():
        out=ROOT/out
    if out.exists() and any(out.iterdir()):
        raise SystemExit("scaffold output directory must be empty")
    out.mkdir(parents=True,exist_ok=True)
    for rel,value in scaffold["files"].items():
        path=out/rel
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    manifest={
        "schema_version":1,
        "project_id":scaffold["project_id"],
        "status":scaffold["status"],
        "files":sorted(scaffold["files"]),
        "generated_media_copied":False,
        "runtime_state_copied":False,
        "secrets_copied":False,
    }
    (out/"SCAFFOLD_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"project_id":scaffold["project_id"],"files":len(scaffold["files"]),"status":scaffold["status"]},sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
