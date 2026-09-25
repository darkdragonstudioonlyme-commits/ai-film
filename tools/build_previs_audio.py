#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.audio import file_sha256, mix_dialogue_timeline

PACKAGE_VERSION="3.8.3"
MODEL_REPO="pnnbao-ump/VieNeu-TTS-v3-Turbo"
MODEL_REVISION="61b85e3d937fbbacb387714180e8182823512523"
SAMPLE_RATE=48000


def main() -> int:
    parser=argparse.ArgumentParser(description="Build full EN/VI preset-voice previsualization dialogue and 75s mix tracks.")
    parser.add_argument("--output-dir",default="/home/dragon/ai-film-dev/artifacts/slice01-previs-audio")
    parser.add_argument("--evidence",default="run-evidence/PREVIS_AUDIO_20260925.json")
    args=parser.parse_args()

    version=importlib.metadata.version("vieneu")
    if version!=PACKAGE_VERSION:
        parser.error(f"expected vieneu=={PACKAGE_VERSION}, got {version}")

    from vieneu import Vieneu
    engine=Vieneu(backend="onnx")
    available={
        row[1] if isinstance(row,(list,tuple)) and len(row)>1 else str(row)
        for row in engine.list_preset_voices()
    }

    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    plan=json.loads((ROOT/"projects/slice01/timing/voice_plan.json").read_text(encoding="utf-8"))
    voice_map=plan["cpu_previs_candidate"]["dialogue_voice_map"]
    shot_by_dialogue={shot["dialogue_id"]:shot for shot in shots if shot.get("dialogue_id")}

    cursor=0.0
    shot_start={}
    for row in timing["shots"]:
        shot_start[row["shot_id"]]=cursor
        cursor+=float(row["duration_sec"])
    total=cursor

    cue_by_id={cue["dialogue_id"]:cue for cue in timing["dialogue_cues"]}
    out=Path(args.output_dir).expanduser().resolve()
    out.mkdir(parents=True,exist_ok=True)

    generated=[]
    for language in ("en","vi"):
        for dialogue_id in sorted(cue_by_id):
            cue=cue_by_id[dialogue_id]
            shot=shot_by_dialogue[dialogue_id]
            voice=voice_map[dialogue_id]
            if voice not in available:
                raise RuntimeError(f"preset voice unavailable: {voice}")
            text=shot["dialogue"][language]
            started=time.perf_counter()
            audio=engine.infer(text,voice=voice)
            elapsed=time.perf_counter()-started
            clip_dir=out/language
            clip_dir.mkdir(parents=True,exist_ok=True)
            path=clip_dir/f"{dialogue_id}.wav"
            engine.save(audio,str(path))
            duration=len(audio)/SAMPLE_RATE
            cue_budget=float(cue["end_offset_sec"])-float(cue["start_offset_sec"])
            generated.append({
                "dialogue_id":dialogue_id,
                "language":language,
                "voice":voice,
                "voice_source":"built_in_presets_no_cloning",
                "text":text,
                "path":str(path),
                "start_sec":shot_start[cue["shot_id"]]+float(cue["start_offset_sec"]),
                "audio_duration_sec":round(duration,6),
                "cue_budget_sec":round(cue_budget,6),
                "fits_cue_budget":duration<=cue_budget,
                "elapsed_sec":round(elapsed,6),
                "rtf":round(elapsed/duration,6) if duration else None,
                "sha256":file_sha256(path),
                "bytes":path.stat().st_size,
            })

    tracks={}
    for language in ("en","vi"):
        clips=[row for row in generated if row["language"]==language]
        track=out/f"dialogue_{language}.wav"
        tracks[language]=mix_dialogue_timeline(clips,total_duration_sec=total,output_path=track,sample_rate=SAMPLE_RATE)

    evidence={
        "schema_version":1,
        "status":"PASS" if all(row["fits_cue_budget"] for row in generated) else "FINDINGS",
        "purpose":"FULL_EN_VI_CPU_PREVIS_DIALOGUE_NOT_FINAL_CASTING",
        "model":{"repo":MODEL_REPO,"revision":MODEL_REVISION},
        "package_version":version,
        "backend":"onnx_cpu",
        "voice_source":"built_in_presets_no_cloning",
        "languages":["en","vi"],
        "zh_status":"SUBTITLE_ONLY_PENDING_VOXCPM2_MODEL_EVAL",
        "total_duration_sec":total,
        "clips":generated,
        "tracks":tracks,
        "platform":platform.platform(),
    }
    ep=Path(args.evidence)
    if not ep.is_absolute():
        ep=ROOT/ep
    ep.parent.mkdir(parents=True,exist_ok=True)
    ep.write_text(json.dumps(evidence,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":evidence["status"],"clips":len(generated),"tracks":{k:v["sha256"] for k,v in tracks.items()}},sort_keys=True))
    return 0 if evidence["status"]=="PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())
