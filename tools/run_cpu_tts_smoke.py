#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
VIE_REPO = "pnnbao-ump/VieNeu-TTS-v3-Turbo"
VIE_REVISION = "61b85e3d937fbbacb387714180e8182823512523"
CODEC_REPO = "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano-ONNX"
CODEC_REVISION = "ceff0d0749bfb3fa2d61149794ec6feef0d1e1ae"
PACKAGE_VERSION = "3.8.3"
SAMPLE_RATE = 48_000

SAMPLES = [
    {"sample_id":"dlg_001_vi","dialogue_id":"dlg_001","language":"vi","voice":"Phạm Tuyên"},
    {"sample_id":"dlg_002_vi","dialogue_id":"dlg_002","language":"vi","voice":"Mai Anh"},
    {"sample_id":"dlg_001_en","dialogue_id":"dlg_001","language":"en","voice":"Phạm Tuyên"},
    {"sample_id":"dlg_002_en","dialogue_id":"dlg_002","language":"en","voice":"Mai Anh"},
]


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def materialize_snapshot(repo_id: str, revision: str) -> dict:
    from huggingface_hub import snapshot_download

    snapshot=Path(snapshot_download(repo_id=repo_id, revision=revision))
    replaced=[]
    for path in sorted(snapshot.rglob("*")):
        if not path.is_symlink():
            continue
        source=path.resolve()
        tmp=path.with_name(path.name+".materializing")
        shutil.copyfile(source,tmp)
        digest=file_sha256(tmp)
        size=tmp.stat().st_size
        path.unlink()
        os.replace(tmp,path)
        replaced.append({"path":str(path),"bytes":size,"sha256":digest})
    return {
        "repo_id":repo_id,
        "revision":revision,
        "snapshot":str(snapshot),
        "materialized_files":len(replaced),
        "materialized_bytes":sum(row["bytes"] for row in replaced),
        "files":replaced,
    }


def load_dialogue() -> tuple[dict, dict]:
    shots=json.loads(
        (ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8")
    )
    timing=json.loads(
        (ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8")
    )
    text_by_id={}
    for shot in shots:
        if shot.get("dialogue_id"):
            text_by_id[shot["dialogue_id"]]=shot["dialogue"]
    cue_budget={
        cue["dialogue_id"]: float(cue["end_offset_sec"])-float(cue["start_offset_sec"])
        for cue in timing["dialogue_cues"]
    }
    return text_by_id,cue_budget


def main() -> int:
    parser=argparse.ArgumentParser(description="CPU EN/VI TTS feasibility smoke using preset voices only.")
    parser.add_argument("--output-dir",default="/home/dragon/ai-film-dev/artifacts/tts-cpu-smoke")
    parser.add_argument("--evidence",default="run-evidence/CPU_TTS_SMOKE_20260924.json")
    parser.add_argument("--materialize-cache",action="store_true")
    args=parser.parse_args()

    try:
        current=importlib.metadata.version("vieneu")
    except importlib.metadata.PackageNotFoundError:
        parser.error("vieneu is not installed; use a dedicated environment with vieneu==3.8.3")
    if current != PACKAGE_VERSION:
        parser.error(f"expected vieneu=={PACKAGE_VERSION}, got {current}")

    materialization=[]
    if args.materialize_cache:
        materialization.append(materialize_snapshot(VIE_REPO,VIE_REVISION))
        materialization.append(materialize_snapshot(CODEC_REPO,CODEC_REVISION))

    from vieneu import Vieneu
    engine=Vieneu(backend="onnx")
    voices=engine.list_preset_voices()
    available={
        row[1] if isinstance(row,(list,tuple)) and len(row)>1 else str(row)
        for row in voices
    }

    text_by_id,cue_budget=load_dialogue()
    out=Path(args.output_dir).expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for spec in SAMPLES:
        if spec["voice"] not in available:
            raise RuntimeError(f"preset voice not available: {spec['voice']}")
        text=text_by_id[spec["dialogue_id"]][spec["language"]]
        started=time.perf_counter()
        audio=engine.infer(text,voice=spec["voice"])
        elapsed=time.perf_counter()-started
        path=out/(spec["sample_id"]+".wav")
        engine.save(audio,str(path))
        duration=len(audio)/SAMPLE_RATE
        budget=cue_budget[spec["dialogue_id"]]
        results.append({
            **spec,
            "text":text,
            "elapsed_sec":round(elapsed,6),
            "audio_duration_sec":round(duration,6),
            "cue_budget_sec":round(budget,6),
            "fits_cue_budget":duration <= budget,
            "rtf":round(elapsed/duration,6) if duration else None,
            "sample_rate":SAMPLE_RATE,
            "bytes":path.stat().st_size,
            "sha256":file_sha256(path),
            "external_path":str(path),
        })

    import onnxruntime
    evidence={
        "schema_version":1,
        "status":"PASS" if all(row["fits_cue_budget"] for row in results) else "FINDINGS",
        "purpose":"CPU_TIMING_AND_PREVIS_FEASIBILITY_NOT_FINAL_VOICE_CASTING",
        "engine":"VieNeu-TTS-v3-Turbo",
        "package_version":current,
        "backend":"onnx_cpu",
        "onnxruntime_version":onnxruntime.__version__,
        "voice_source":"built_in_presets_no_cloning",
        "languages_tested":["en","vi"],
        "language_not_tested":{"zh-CN":"ROUTE_TO_VOXCPM2_MODEL_EVAL"},
        "model":{"repo":VIE_REPO,"revision":VIE_REVISION},
        "codec":{"repo":CODEC_REPO,"revision":CODEC_REVISION},
        "platform":platform.platform(),
        "python":platform.python_version(),
        "cache_materialization":materialization,
        "samples":results,
        "rtf_mean":round(sum(row["rtf"] for row in results)/len(results),6),
    }
    ep=Path(args.evidence)
    if not ep.is_absolute():
        ep=ROOT/ep
    ep.parent.mkdir(parents=True,exist_ok=True)
    ep.write_text(json.dumps(evidence,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(evidence,ensure_ascii=False,sort_keys=True))
    return 0 if evidence["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
