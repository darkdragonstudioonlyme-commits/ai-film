#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(text:str)->str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def main():
    ap=argparse.ArgumentParser(description="Build fixed VoxCPM2 EN/ZH/VI voice-design evaluation packet. No synthesis is executed.")
    ap.add_argument("--out-dir",default="model-evaluations/slice01/voice/packet")
    args=ap.parse_args()
    cfg=json.loads((ROOT/"model-evaluations/slice01/voice/voxcpm2_eval_config.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    plan=json.loads((ROOT/"projects/slice01/timing/voice_plan.json").read_text(encoding="utf-8"))
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    character_map=plan["dialogue_character_map"]
    cue_by_id={row["dialogue_id"]:row for row in timing["dialogue_cues"]}
    rows=[]
    private=[]
    for shot in shots:
        dialogue_id=shot.get("dialogue_id")
        if not dialogue_id: continue
        char=character_map[dialogue_id]
        profile=cfg["character_profiles"][char]
        voice_group="voice_"+digest(char)[:8]
        for language in cfg["languages"]:
            target=shot["dialogue"][language]
            blind_id="vox_"+digest(f"{dialogue_id}:{language}:{char}")[:12]
            design=profile["description"]
            rows.append({
              "blind_id":blind_id,
              "voice_group":voice_group,
              "dialogue_id":dialogue_id,
              "language":language,
              "target_text":target,
              "voice_design_description":design,
              "model_input_text":f"({design}){target}",
              "seed":profile["seed"],
              "cfg_value":cfg["parameters"]["cfg_value"],
              "inference_timesteps":cfg["parameters"]["inference_timesteps"],
              "cue_budget_sec":round(float(cue_by_id[dialogue_id]["end_offset_sec"])-float(cue_by_id[dialogue_id]["start_offset_sec"]),6),
              "reference_audio":None,
              "mode":"voice_design",
            })
            private.append({"blind_id":blind_id,"voice_group":voice_group,"character_id":char})
    if len(rows)!=12:
        raise RuntimeError(f"expected 12 samples, got {len(rows)}")
    out=Path(args.out_dir)
    if not out.is_absolute(): out=ROOT/out
    out.mkdir(parents=True,exist_ok=True)
    public={"schema_version":1,"evaluation_id":cfg["evaluation_id"],"model":cfg["model"],"mode":cfg["mode"],"samples":rows}
    (out/"eval_packet.json").write_text(json.dumps(public,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"blind_map_private.json").write_text(json.dumps({"schema_version":1,"mapping":private},indent=2,sort_keys=True)+"\n",encoding="utf-8")
    with (out/"scores.csv").open("w",newline="",encoding="utf-8") as fh:
        w=csv.writer(fh,lineterminator="\n"); w.writerow(["blind_id","intelligibility","character_match","cross_language_identity","between_character_separation","prosody","artifact_free","overall","audio_duration_sec","cue_fit","failure_tags","notes"])
        for row in rows:w.writerow([row["blind_id"],"","","","","","","","","","",""])
    print(json.dumps({"samples":len(rows),"languages":cfg["languages"],"mode":cfg["mode"],"voice_groups":len(set(x["voice_group"] for x in rows))},ensure_ascii=False))
if __name__=="__main__":main()
