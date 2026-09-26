#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def sha256(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--media-root",default="/home/dragon/ai-film-dev/media/slice01/voice-voxcpm2-20260926")
    args=ap.parse_args()
    media_root=Path(args.media_root).resolve()
    shortlist=load(ROOT/"model-evaluations/auto-eval/voice_shortlist_20260926.json")
    requests=load(ROOT/"model-evaluations/slice01/voice/requests/requests.json")["requests"]
    formal=load(ROOT/"run-evidence/VOXCPM2_FORMAL_BATCH_20260926.json")
    req_by_blind={r["blind_id"]:r for r in requests}
    formal_by_req={r["request_id"]:r for r in formal["samples"]}

    rows=[]
    for item in shortlist["samples"]:
        req=req_by_blind[item["asset_id"]]
        sample=formal_by_req[req["request_id"]]
        wav=media_root/f"{req['request_id']}.wav"
        ev=media_root/f"{req['request_id']}.evidence.json"
        if not wav.is_file() or not ev.is_file():
            raise SystemExit(f"missing local voice artifact/evidence: {req['request_id']}")
        wav_sha=sha256(wav)
        if wav_sha!=sample["audio_sha256"]:
            raise SystemExit(f"voice hash drift: {req['request_id']}")
        rows.append({
          "asset_id":item["asset_id"],
          "request_id":req["request_id"],
          "dialogue_id":item["dialogue_id"],
          "language":item["language"],
          "target_text":item["target_text"],
          "score":item["score"],
          "cue_fit":item["cue_fit"],
          "duration_sec":sample["duration_sec"],
          "sha256":wav_sha,
          "manifest_sha256":sha256(ev),
          "local_path":str(wav),
          "evidence_path":str(ev),
          "status":"ROUGH_CUT_CANDIDATE_ONLY",
          "production_acceptance":False,
        })
    rows.sort(key=lambda r:(r["language"],r["dialogue_id"]))
    catalog={
      "schema_version":1,
      "status":"ROUGH_CUT_CANDIDATES_HASH_VERIFIED",
      "sample_count":len(rows),
      "source_auto_eval":"run-evidence/AUTO_EVAL_VOICE_WHISPER_V2_20260926.json",
      "production_acceptance":False,
      "publish_authority":False,
      "samples":rows,
    }
    out=ROOT/"projects/slice01/audio/rough_cut_voice_candidates.json"
    out.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    for lang in ("en","vi","zh-CN"):
        tracks={
          r["dialogue_id"]:{
            "asset_id":r["asset_id"],
            "sha256":r["sha256"],
            "manifest_sha256":r["manifest_sha256"],
            "language":lang,
            "path_ref":r["local_path"],
            "candidate_only":True,
          }
          for r in rows if r["language"]==lang
        }
        idx={
          "schema_version":1,
          "project_id":"slice01",
          "status":"ROUGH_CUT_CANDIDATE_ONLY",
          "language":lang,
          "videos":{},
          "dialogue_audio":tracks,
          "execution_permitted":False,
          "production_acceptance":False,
        }
        path=ROOT/f"projects/slice01/lipsync/media_index.rough_{lang}.json"
        path.write_text(json.dumps(idx,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":catalog["status"],"sample_count":len(rows)},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
