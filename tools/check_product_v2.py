#!/usr/bin/env python3
"""Structural contract for the active product-first control plane."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REQUIRED_ROOT = [
    "RESUME.md","BACKLOG.yaml","MILESTONES.md","CONTINUE_PROTOCOL.md",
    "DECISIONS.md","FILM_LEARNINGS.md","PROGRESS_LOG.jsonl",
]
REQUIRED_PRODUCT_FILES = [
    "model-evaluations/slice01/model_matrix.json",
    "model-evaluations/slice01/benchmark_plan.json",
    "model-evaluations/slice01/SCORING_RUBRIC.md",
    "model-evaluations/slice01/RUNNER_CONTRACT.md",
    "projects/slice01/timing/timing.json",
    "projects/slice01/timing/timing_manifest.json",
    "projects/slice01/timing/subtitles/en.srt",
    "projects/slice01/timing/subtitles/zh-CN.srt",
    "projects/slice01/timing/subtitles/vi.srt",
    "projects/slice01/timing/voice_plan.json",
    "model-evaluations/slice01/gpu-worker/runtime_lock.json",
    "model-evaluations/slice01/gpu-worker/requirements-base.lock.txt",
    "model-evaluations/slice01/BACKEND_ADAPTERS.md",
    "run-evidence/GPU_WORKER_DRYRUN_20260925.json",
    "run-evidence/PREVIS_AUDIO_20260925.json",
    "run-evidence/PREVIS_ANIMATIC_EN_20260925.json",
    "run-evidence/PREVIS_ANIMATIC_VI_20260925.json",
    "projects/slice01/timing/voice_plan.json",
    "model-evaluations/slice01/upstream_pins_2026-09-24.json",
    "model-evaluations/slice01/PINNING_2026-09-24.md",
    "model-evaluations/slice01/CPU_TTS_FEASIBILITY_2026-09-24.md",
    "model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json",
    "model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.md",
    "run-evidence/CPU_TTS_SMOKE_20260924.json",
]
LANGS = {"en","zh-CN","vi"}


def main() -> int:
    root=Path(__file__).resolve().parents[1]
    errors=[]
    state=(root/"PROJECT_STATE.md").read_text(encoding="utf-8")
    if "STATE_VERSION: PRODUCT_V2_" not in state:
        errors.append("state-not-product-v2")
    if "ACTIVE_ROUTER: CONTINUE_PROTOCOL.md" not in state:
        errors.append("router-not-v2")
    if "archive/p00-governance-2026-09-24" not in state:
        errors.append("legacy-baseline-not-declared")
    for rel in REQUIRED_ROOT + REQUIRED_PRODUCT_FILES:
        if not (root/rel).is_file():
            errors.append("missing:"+rel)
    if (root/"RESUME.md").stat().st_size > 4096:
        errors.append("resume-too-large")
    if (root/"CONTINUE_PROTOCOL.md").stat().st_size > 6144:
        errors.append("continue-protocol-too-large")

    backlog=(root/"BACKLOG.yaml").read_text(encoding="utf-8")
    ids=re.findall(r"^- id: (T-[0-9]+)$",backlog,re.M)
    if len(ids)!=len(set(ids)) or len(ids)<4:
        errors.append("backlog-ids")
    if "status: READY" not in backlog:
        errors.append("backlog-no-ready")

    p=root/"projects"/"slice01"
    project=json.loads((p/"project.json").read_text(encoding="utf-8"))
    ledger=json.loads((p/"continuity.json").read_text(encoding="utf-8"))
    casting=json.loads((p/"casting.json").read_text(encoding="utf-8"))
    shots=json.loads((p/"shots"/"benchmark_shots.json").read_text(encoding="utf-8"))
    if project.get("rights",{}).get("source")!="original_generated_for_project":
        errors.append("slice-rights-source")
    if set(project.get("languages",[])) != LANGS:
        errors.append("slice-languages")
    if len(shots)!=8 or len({s.get("shot_id") for s in shots})!=8 or len({s.get("seed") for s in shots})!=8:
        errors.append("benchmark-identity")
    shot_ids={s.get("shot_id") for s in shots}
    times={x.get("t") for x in ledger.get("timeline",[])}
    for shot in shots:
        if shot.get("story_time") not in times:
            errors.append("unknown-story-time:"+str(shot.get("shot_id")))
        dialogue=shot.get("dialogue")
        if dialogue is not None:
            if set(dialogue)!=LANGS or not shot.get("dialogue_id"):
                errors.append("dialogue-contract:"+str(shot.get("shot_id")))
        for cid in shot.get("characters",[]):
            if cid not in ledger.get("characters",{}) or cid not in casting.get("characters",{}):
                errors.append("character-reference:"+cid)

    timing=json.loads((p/"timing"/"timing.json").read_text(encoding="utf-8"))
    timing_rows=timing.get("shots",[])
    timing_ids={row.get("shot_id") for row in timing_rows}
    total=sum(float(row.get("duration_sec",0)) for row in timing_rows)
    if timing_ids != shot_ids or len(timing_rows)!=8:
        errors.append("timing-population")
    if not 60.0 <= total <= 90.0:
        errors.append("timing-duration")
    cue_ids={row.get("dialogue_id") for row in timing.get("dialogue_cues",[])}
    expected_cues={shot.get("dialogue_id") for shot in shots if shot.get("dialogue_id")}
    if cue_ids != expected_cues:
        errors.append("timing-dialogue-cues")

    matrix=json.loads((root/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
    models=matrix.get("models",[])
    model_ids=[model.get("model_id") for model in models]
    if not models or len(model_ids)!=len(set(model_ids)) or any(not model_id for model_id in model_ids):
        errors.append("model-matrix-identity")
    if not any(model.get("enabled") and model.get("stage")=="image" for model in models):
        errors.append("model-matrix-no-image")
    if not any(model.get("enabled") and model.get("stage")=="video" for model in models):
        errors.append("model-matrix-no-video")
    for model in models:
        if not model.get("license_gate"):
            errors.append("model-license-gate:"+str(model.get("model_id")))
        if model.get("execution_ready"):
            checkpoint=str(model.get("checkpoint","")).lower()
            if "tbd" in checkpoint or model.get("license_gate")!="PASS":
                errors.append("model-execution-ready-without-pin:"+str(model.get("model_id")))

    plan=json.loads((root/"model-evaluations/slice01/benchmark_plan.json").read_text(encoding="utf-8"))
    profiles=plan.get("profiles",{})
    for required in ("smoke","keyframe_core","video_core"):
        if required not in profiles:
            errors.append("benchmark-profile-missing:"+required)
    for name,profile in profiles.items():
        unknown=set(profile.get("shot_ids",[]))-shot_ids
        if unknown:
            errors.append("benchmark-profile-unknown-shot:"+name)


    pins=json.loads((root/"model-evaluations/slice01/upstream_pins_2026-09-24.json").read_text(encoding="utf-8"))
    pin_rows=pins.get("models",[])
    pin_ids=[row.get("model_id") for row in pin_rows]
    if len(pin_ids)!=len(set(pin_ids)) or len(pin_rows)!=len(models):
        errors.append("model-pins-identity")
    pin_by_id={row.get("model_id"):row for row in pin_rows}
    for model in models:
        if model.get("pin_status")!="PINNED":
            errors.append("model-not-pinned:"+str(model.get("model_id")))
            continue
        model_id=model.get("model_id")
        pin=pin_by_id.get(model_id)
        if pin is None:
            errors.append("matrix-pin-missing:"+str(model_id))
            continue
        revision=str(model.get("source_revision",""))
        if not re.fullmatch(r"[0-9a-f]{40}",revision):
            errors.append("matrix-pin-revision:"+str(model_id))
        if revision != pin.get("source_revision"):
            errors.append("matrix-pin-drift:"+str(model_id))
        if "tbd" in str(model.get("checkpoint","")).lower():
            errors.append("matrix-pin-tbd:"+str(model_id))
        if model.get("execution_ready"):
            errors.append("model-execution-must-remain-gated:"+str(model_id))

    qwen=next((model for model in models if model.get("model_id")=="qwen-image-2.1"),None)
    if qwen is None or qwen.get("enabled") or qwen.get("commercial_production_allowed") is not False:
        errors.append("qwen-commercial-gate")

    latent=next((model for model in models if model.get("model_id")=="latent-sync"),None)
    if latent is None or latent.get("license_hint")!="openrail++" or "LEGAL_REVIEW" not in latent.get("license_gate",""):
        errors.append("latentsync-license-gate")

    tts=json.loads((root/"run-evidence/CPU_TTS_SMOKE_20260924.json").read_text(encoding="utf-8"))
    if tts.get("status")!="PASS":
        errors.append("cpu-tts-not-pass")
    if set(tts.get("languages_tested",[]))!={"en","vi"}:
        errors.append("cpu-tts-language-scope")
    if tts.get("language_not_tested",{}).get("zh-CN")!="ROUTE_TO_VOXCPM2_MODEL_EVAL":
        errors.append("cpu-tts-zh-route")
    samples=tts.get("samples",[])
    if len(samples)!=4 or not all(row.get("fits_cue_budget") for row in samples):
        errors.append("cpu-tts-cue-fit")
    if not isinstance(tts.get("rtf_mean"),(int,float)) or tts["rtf_mean"]>=1.0:
        errors.append("cpu-tts-rtf")

    voice_plan=json.loads((p/"timing"/"voice_plan.json").read_text(encoding="utf-8"))
    if voice_plan.get("zh_route",{}).get("model_id")!="voxcpm2":
        errors.append("voice-plan-zh")
    if voice_plan.get("cpu_previs_candidate",{}).get("model_id")!="vieneu-v3-turbo":
        errors.append("voice-plan-cpu")

    runtime=json.loads((root/"model-evaluations/slice01/gpu-worker/runtime_lock.json").read_text(encoding="utf-8"))
    if runtime.get("status")!="PINNED_BASE_DRY_RUN_ONLY" or runtime.get("execution_ready") is not False:
        errors.append("gpu-runtime-authority")
    package_values=list((runtime.get("packages") or {}).values())
    if not package_values or any("tbd" in str(value).lower() for value in package_values):
        errors.append("gpu-runtime-package-pins")
    worker_plan=json.loads((root/"run-evidence/GPU_WORKER_DRYRUN_20260925.json").read_text(encoding="utf-8"))
    if worker_plan.get("mode")!="DRY_RUN" or worker_plan.get("execution_ready") is not False:
        errors.append("gpu-worker-dryrun")

    previs=json.loads((root/"run-evidence/PREVIS_AUDIO_20260925.json").read_text(encoding="utf-8"))
    if previs.get("status")!="PASS" or set(previs.get("languages",[]))!={"en","vi"}:
        errors.append("previs-audio-status")
    clips=previs.get("clips",[])
    if len(clips)!=8 or not all(row.get("fits_cue_budget") for row in clips):
        errors.append("previs-audio-clips")
    if previs.get("voice_source")!="built_in_presets_no_cloning":
        errors.append("previs-audio-cloning")
    tracks=previs.get("tracks",{})
    for language in ("en","vi"):
        track=tracks.get(language,{})
        if track.get("duration_sec")!=75.0 or len(str(track.get("sha256","")))!=64:
            errors.append("previs-audio-track:"+language)

    for language in ("EN","VI"):
        anim=json.loads((root/f"run-evidence/PREVIS_ANIMATIC_{language}_20260925.json").read_text(encoding="utf-8"))
        if anim.get("status")!="PASS" or len(anim.get("outputs",[]))!=2:
            errors.append("previs-animatic:"+language)
            continue
        if anim.get("audio_source",{}).get("sha256") != tracks[language.lower()]["sha256"]:
            errors.append("previs-animatic-audio:"+language)
        for output in anim["outputs"]:
            probe=output.get("probe",{})
            if probe.get("duration_sec")!=75.0 or probe.get("has_audio") is not True:
                errors.append("previs-animatic-probe:"+language)

    rental=json.loads((root/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))
    stage_compute=sum(float(row.get("compute_ceiling_usd",0)) for row in rental.get("stages",[]))
    if round(stage_compute,2) != round(float(rental.get("compute_ceiling_usd",-1)),2):
        errors.append("rental-compute-sum")
    if float(rental.get("compute_ceiling_usd",9999)) > float(rental.get("hard_all_in_authorization_cap_usd",0)):
        errors.append("rental-cap-undercompute")
    if rental.get("launch_authorized") or rental.get("spend_authorized"):
        errors.append("rental-unexpected-authority")
    if float(rental.get("hard_all_in_authorization_cap_usd",0)) != 150.0:
        errors.append("rental-cap-drift")
    if float(rental.get("initial_execution_subcap_usd",0)) != 60.0:
        errors.append("rental-initial-subcap-drift")
    if float(rental.get("initial_execution_subcap_usd",9999)) >= float(rental.get("hard_all_in_authorization_cap_usd",0)):
        errors.append("rental-subcap-order")

    designs=list((root/"film"/"design").glob("*.md"))
    if len(designs)!=7:
        errors.append("film-design-count")
    if errors:
        print("PRODUCT_V2_CHECK_FAIL")
        print("\n".join(errors))
        return 1
    print(
        "PRODUCT_V2_CHECK_PASS "
        f"shots=8 designs=7 languages=en,zh-CN,vi timing={total:.1f}s models={len(models)}"
    )
    return 0


if __name__=="__main__":
    sys.exit(main())
