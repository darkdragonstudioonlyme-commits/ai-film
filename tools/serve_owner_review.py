#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.owner_review import OwnerReviewError, validate_owner_review


def expected_voice_ids() -> set[str]:
    packet=json.loads((ROOT/"model-evaluations/slice01/voice/packet/eval_packet.json").read_text(encoding="utf-8"))
    return {row["blind_id"] for row in packet["samples"]}


def validate_and_save(payload: dict[str,Any], *, output_path: Path) -> dict[str,Any]:
    normalized=validate_owner_review(payload,expected_voice_ids=expected_voice_ids())
    output_path=output_path.resolve()
    output_path.parent.mkdir(parents=True,exist_ok=True)
    tmp=output_path.with_suffix(output_path.suffix+".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    os.replace(tmp,output_path)
    return {
        "status":"PASS_COMPLETE_OWNER_REVIEW_SAVED",
        "score_set_complete":normalized["score_set_complete"],
        "voice_samples":len(normalized["voice"]),
        "motion_samples":len(normalized["motion"]),
        "output_path":str(output_path),
    }


class OwnerReviewHandler(SimpleHTTPRequestHandler):
    server_version="AIFilmOwnerReview/1.0"

    def _json(self,status:int,payload:dict[str,Any]) -> None:
        body=(json.dumps(payload,ensure_ascii=False)+"\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path=="/status":
            out=Path(self.server.output_path)
            return self._json(200,{
                "saved":out.is_file(),
                "output_path":str(out),
                "bytes":out.stat().st_size if out.is_file() else 0,
            })
        return super().do_GET()

    def do_POST(self):
        if self.path!="/submit":
            return self._json(404,{"status":"NOT_FOUND"})
        try:
            length=int(self.headers.get("Content-Length","0"))
        except ValueError:
            return self._json(400,{"status":"INVALID_CONTENT_LENGTH"})
        if length<=0 or length>128*1024:
            return self._json(413,{"status":"PAYLOAD_SIZE_REJECTED"})
        try:
            payload=json.loads(self.rfile.read(length).decode("utf-8"))
            result=validate_and_save(payload,output_path=Path(self.server.output_path))
        except (UnicodeDecodeError,json.JSONDecodeError,OwnerReviewError) as exc:
            return self._json(400,{"status":"INVALID_OWNER_REVIEW","error":str(exc)})
        return self._json(200,result)

    def log_message(self,fmt,*args):
        sys.stderr.write("[owner-review] "+(fmt%args)+"\n")


def main() -> int:
    default_review=ROOT.parent/"media/slice01/owner-review-20260926"
    ap=argparse.ArgumentParser(description="Serve the local owner media review UI and save only a complete validated 0-8 score set.")
    ap.add_argument("--review-dir",default=str(default_review))
    ap.add_argument("--output")
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=8765)
    args=ap.parse_args()

    review_dir=Path(args.review_dir).resolve()
    if not (review_dir/"index.html").is_file():
        raise SystemExit("review index.html missing")
    output=Path(args.output).resolve() if args.output else review_dir/"owner_review_scores_20260926.json"

    handler=partial(OwnerReviewHandler,directory=str(review_dir))
    server=ThreadingHTTPServer((args.host,args.port),handler)
    server.output_path=str(output)
    print(json.dumps({
        "status":"OWNER_REVIEW_SERVER_READY",
        "url":f"http://{args.host}:{args.port}/",
        "output":str(output),
    }),flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__=="__main__":
    raise SystemExit(main())