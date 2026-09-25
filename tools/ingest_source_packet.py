#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from film.source_ingest import SourceIngestError, normalize_source_packet

def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(description="Normalize a source/adaptation packet as inert data with rights evidence.")
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    inp=Path(args.input)
    if not inp.is_absolute():
        inp=ROOT/inp
    packet=json.loads(inp.read_text(encoding="utf-8"))
    evidence_ref=packet.get("evidence",{}).get("ref")
    if not evidence_ref:
        raise SourceIngestError("evidence ref required")
    evidence_path=Path(evidence_ref)
    if not evidence_path.is_absolute():
        evidence_path=ROOT/evidence_path
    if not evidence_path.is_file():
        raise SourceIngestError("evidence file missing")
    actual=file_sha256(evidence_path)
    if packet.get("evidence",{}).get("sha256")!=actual:
        raise SourceIngestError("evidence sha256 mismatch")
    normalized=normalize_source_packet(packet)
    out=Path(args.out)
    if not out.is_absolute():
        out=ROOT/out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(normalized,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "source_id":normalized["source_id"],
        "kind":normalized["kind"],
        "embedded_instruction_flags":len(normalized["embedded_instruction_flags"]),
        "tool_authority":normalized["tool_authority"],
        "publish_authority":normalized["publish_authority"],
    },sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
