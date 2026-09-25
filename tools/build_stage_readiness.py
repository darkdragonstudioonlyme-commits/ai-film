#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.stage_readiness import SLICE01_STAGE_DAG,evaluate_stage_readiness

def main():
    source=json.loads((ROOT/"projects/slice01/source/source_packet.json").read_text(encoding="utf-8"))
    screenplay=json.loads((ROOT/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
    loc=json.loads((ROOT/"projects/slice01/localization/dialogue_bundle.json").read_text(encoding="utf-8"))
    continuity=json.loads((ROOT/"projects/slice01/continuity.json").read_text(encoding="utf-8"))
    shots=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
    timing=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
    auth=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.placeholder.json").read_text(encoding="utf-8"))
    cast_ref=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
    selected=json.loads((ROOT/"projects/slice01/edit/selected_takes.json").read_text(encoding="utf-8"))
    mix=json.loads((ROOT/"projects/slice01/audio/mix_plan_en.json").read_text(encoding="utf-8"))
    rights=json.loads((ROOT/"projects/slice01/rights/rights_register.json").read_text(encoding="utf-8"))
    rights_by={(r["subject_type"],r["subject_id"]):r for r in rights["records"]}
    evidence={
      "source_packet_ready":source.get("tool_authority") is False and source.get("rights",{}).get("status")=="ORIGINAL",
      "screenplay_ready":bool(screenplay.get("scenes")),
      "localization_text_ready":all(all(str(v).strip() for v in row["texts"].values()) for row in loc.get("lines",[])),
      "continuity_ready":bool(continuity.get("timeline")),
      "shots_ready":len(shots)>0,
      "timing_ready":len(timing.get("shots",[]))>0,
      "paid_gpu_authorized":auth.get("status")=="AUTHORIZED",
      "generated_casting_assets":bool(cast_ref.get("generated_reference_paths")),
      "final_voice_eval_complete":False,
      "visual_model_selected":False,
      "selected_video_takes":bool(selected.get("takes") or selected.get("selected_takes")),
      "final_music_asset":False,
      "music_rights_ready":rights_by.get(("music","project-music"),{}).get("status") in {"LICENSED","ORIGINAL","PUBLIC_DOMAIN"},
      "final_audio_mix":mix.get("status")=="READY_TO_MIX" and not mix.get("blockers"),
      "final_lipsync_assets":False,
      "rendered_final_media":False,
      "publication_rights_ready":rights.get("status")!="INCOMPLETE_BLOCK_PUBLICATION",
      "technical_qc_pass":False,
      "creative_qc_pass":False,
      "delivery_package_ready":False,
    }
    report=evaluate_stage_readiness(SLICE01_STAGE_DAG,evidence)
    report["evidence"]=evidence
    out=ROOT/"projects/slice01/readiness/stage_readiness.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"ready_stages":report["ready_stages"],"blocking_frontier":report["blocking_frontier"],"execution_permitted":report["execution_permitted"]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
