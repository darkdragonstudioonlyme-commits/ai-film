#!/usr/bin/env python3
"""Structural contract for the active product-first control plane."""
from __future__ import annotations
import csv
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
    "model-evaluations/slice01/upstream_pins_2026-09-24.json",
    "model-evaluations/slice01/PINNING_2026-09-24.md",
    "model-evaluations/slice01/CPU_TTS_FEASIBILITY_2026-09-24.md",
    "model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json",
    "model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.md",
    "run-evidence/CPU_TTS_SMOKE_20260924.json",
    "run-evidence/GPU_PRELAUNCH_BUNDLE_20260925.json",
    "projects/slice01/casting/reference_contract.json",
    "projects/slice01/casting/CASTING_REFERENCE_ACCEPTANCE.md",
    "projects/slice01/casting/eval/blind_items.json",
    "projects/slice01/casting/eval/blind_map_private.json",
    "projects/slice01/casting/eval/scores.csv",
    "model-evaluations/slice01/voice/voxcpm2_eval_config.json",
    "model-evaluations/slice01/voice/requirements-voxcpm2-eval.txt",
    "model-evaluations/slice01/voice/VOXCPM2_EVAL.md",
    "model-evaluations/slice01/voice/packet/eval_packet.json",
    "model-evaluations/slice01/voice/packet/blind_map_private.json",
    "model-evaluations/slice01/voice/packet/scores.csv",
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
        next_work=(root/"NEXT_WORK_ITEM.md").read_text(encoding="utf-8")
        if "STATUS: BLOCKED" not in next_work or "CURRENT_WORK_STATUS: BLOCKED" not in state:
            errors.append("backlog-no-ready-without-canonical-block")

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

    prelaunch=json.loads((root/"run-evidence/GPU_PRELAUNCH_BUNDLE_20260925.json").read_text(encoding="utf-8"))
    enabled_visual={
        model["model_id"] for model in models
        if model.get("enabled") and model.get("stage") in {"image","video"}
    }
    if prelaunch.get("mode")!="PRELAUNCH_DRY_RUN_ONLY" or prelaunch.get("execution_ready") is not False or prelaunch.get("provider_resource_created") is not False:
        errors.append("gpu-prelaunch-authority")
    pre_rows=prelaunch.get("models",[])
    if {row.get("model_id") for row in pre_rows} != enabled_visual:
        errors.append("gpu-prelaunch-population")
    for row in pre_rows:
        if row.get("execution_ready") is not False or row.get("runner_contract",{}).get("paid_authority_inherited") is not False:
            errors.append("gpu-prelaunch-model-authority:"+str(row.get("model_id")))

    cast_contract=json.loads((root/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
    if cast_contract.get("status")!="CONTRACT_READY_REFERENCES_NOT_GENERATED":
        errors.append("casting-reference-status")
    if cast_contract.get("generated_reference_paths") != []:
        errors.append("casting-reference-fake-assets")
    if set(cast_contract.get("characters",{})) != set(casting.get("characters",{})):
        errors.append("casting-reference-population")
    for char in cast_contract.get("characters",{}).values():
        for style in cast_contract.get("styles",[]):
            slots=char.get("styles",{}).get(style,{}).get("slots",[])
            if len(slots)!=4 or any(slot.get("asset_id") is not None or slot.get("manifest_sha256") is not None for slot in slots):
                errors.append("casting-reference-slot-state")

    voice_packet=json.loads((root/"model-evaluations/slice01/voice/packet/eval_packet.json").read_text(encoding="utf-8"))
    samples=voice_packet.get("samples",[])
    if voice_packet.get("mode")!="voice_design" or len(samples)!=12:
        errors.append("voxcpm2-packet-shape")
    if {row.get("language") for row in samples} != LANGS:
        errors.append("voxcpm2-packet-languages")
    if any(row.get("reference_audio") is not None or row.get("mode")!="voice_design" for row in samples):
        errors.append("voxcpm2-cloning-boundary")
    if voice_packet.get("model",{}).get("package")!="voxcpm==2.0.3":
        errors.append("voxcpm2-package-pin")
    vox_matrix=next((m for m in models if m.get("model_id")=="voxcpm2"),None)
    if vox_matrix is None or "voxcpm==2.0.3" not in vox_matrix.get("runtime_requirements",[]):
        errors.append("voxcpm2-runtime-pin")


    cast_gen=root/"projects/slice01/casting/generation"
    cast_jobs=json.loads((cast_gen/"casting_jobs.json").read_text(encoding="utf-8"))
    cast_public=json.loads((cast_gen/"blind_items.json").read_text(encoding="utf-8"))
    cast_private=json.loads((cast_gen/"blind_map_private.json").read_text(encoding="utf-8"))
    jobs=cast_jobs.get("jobs",[])
    enabled_images={
        m["model_id"] for m in models
        if m.get("enabled") and m.get("stage")=="image"
    }
    if cast_jobs.get("status")!="COMPILED_NOT_EXECUTED" or len(jobs)!=32:
        errors.append("casting-generation-shape")
    if {row.get("model_id") for row in jobs} != enabled_images:
        errors.append("casting-generation-models")
    if any(row.get("execution_permitted") is not False for row in jobs):
        errors.append("casting-generation-authority")
    if len({row.get("job_id") for row in jobs})!=32 or len({row.get("blind_id") for row in jobs})!=32:
        errors.append("casting-generation-identity")
    public_items=cast_public.get("items",[])
    private_map=cast_private.get("mapping",[])
    if len(public_items)!=32 or len(private_map)!=32:
        errors.append("casting-blind-population")
    if any("character_id" in row or "model_id" in row for row in public_items):
        errors.append("casting-public-leak")
    if {row.get("blind_id") for row in public_items}!={row.get("blind_id") for row in private_map}:
        errors.append("casting-private-map-drift")
    with (cast_gen/"scores.csv").open(encoding="utf-8",newline="") as fh:
        cast_score_rows=list(csv.DictReader(fh))
    if len(cast_score_rows)!=32:
        errors.append("casting-score-template-population")
    else:
        score_fields=("identity_match","within_character_consistency","between_character_separation","style_quality","anatomy_artifact_free","overall")
        if any(any((row.get(field) or "").strip() for field in score_fields) for row in cast_score_rows):
            errors.append("casting-score-template-must-remain-blank-before-assets")

    vox_requests=json.loads((root/"model-evaluations/slice01/voice/requests/requests.json").read_text(encoding="utf-8"))
    requests=vox_requests.get("requests",[])
    if vox_requests.get("status")!="COMPILED_NOT_EXECUTED" or len(requests)!=12:
        errors.append("voxcpm2-request-shape")
    if any(row.get("execution_permitted") is not False or row.get("reference_audio") is not None for row in requests):
        errors.append("voxcpm2-request-authority")
    if any(row.get("model",{}).get("revision")!="32279effe8c19989596f05d353d1447f51d9e915" for row in requests):
        errors.append("voxcpm2-request-revision")
    if any(row.get("model",{}).get("package")!="voxcpm==2.0.3" for row in requests):
        errors.append("voxcpm2-request-package")
    if len({row.get("request_id") for row in requests})!=12 or len({row.get("request_digest") for row in requests})!=12:
        errors.append("voxcpm2-request-identity")
    output_contract=json.loads((root/"model-evaluations/slice01/voice/requests/output_manifest_contract.json").read_text(encoding="utf-8"))
    if output_contract.get("status")!="SCHEMA_ONLY_NO_AUDIO" or output_contract.get("sample_rate_hz")!=48000:
        errors.append("voxcpm2-output-contract")


    cast_jobs_bundle=json.loads((root/"projects/slice01/casting/generation/casting_jobs.json").read_text(encoding="utf-8"))
    cast_jobs=cast_jobs_bundle.get("jobs",[])
    if len(cast_jobs)!=32 or any(row.get("execution_permitted") is not False for row in cast_jobs):
        errors.append("batch007-casting-job-source")

    # Batch007 contracts remain code-only until real GPU outputs exist.
    required_batch007=[
        "model-evaluations/slice01/BATCH007_CONTRACT.md",
        "film/image_runner.py",
        "film/casting_ingest.py",
        "film/decision_ledger.py",
        "tools/compile_image_worker_request.py",
        "tools/ingest_casting_assets.py",
        "tools/build_benchmark_decision_report.py",
    ]
    for rel in required_batch007:
        if not (root/rel).is_file():
            errors.append("batch007-missing:"+rel)


    rate_snap=json.loads((root/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
    if rate_snap.get("provider")!="RunPod" or rate_snap.get("observed_at")!="2026-09-25":
        errors.append("paid-gate-rate-snapshot")
    rates=rate_snap.get("rates_usd_per_hour",{})
    if rates.get("RTX 5090")!=0.99 or rates.get("RTX Pro 6000")!=2.09:
        errors.append("paid-gate-rate-drift")
    auth=json.loads((root/"model-evaluations/slice01/launch_authorization.placeholder.json").read_text(encoding="utf-8"))
    if auth.get("status")!="NOT_AUTHORIZED" or auth.get("max_total_usd")!=0.0 or auth.get("allowed_gpus")!=[]:
        errors.append("paid-gate-placeholder-authority")
    if not (root/"model-evaluations/slice01/decision_templates.json").is_file():
        errors.append("decision-templates-missing")
    required_batch008=[
        "model-evaluations/slice01/BATCH008_CONTRACT.md",
        "film/launch_gate.py",
        "film/synthetic_fixtures.py",
        "film/decision_templates.py",
        "tools/check_paid_launch_gate.py",
        "tools/build_synthetic_casting_fixture.py",
        "tools/build_stage_decision_report.py",
    ]
    for rel in required_batch008:
        if not (root/rel).is_file():
            errors.append("batch008-missing:"+rel)


    asset_graph=json.loads((root/"projects/slice01/asset_graph.json").read_text(encoding="utf-8"))
    if asset_graph.get("status")!="SPEC_GRAPH_NO_GENERATED_MEDIA" or len(asset_graph.get("assets",[]))<10:
        errors.append("asset-graph-shape")
    if len({row.get("asset_id") for row in asset_graph.get("assets",[])}) != len(asset_graph.get("assets",[])):
        errors.append("asset-graph-identity")
    qc_policy=json.loads((root/"projects/slice01/qc_policy.json").read_text(encoding="utf-8"))
    if qc_policy.get("status")!="POLICY_READY_NO_MEDIA_QC":
        errors.append("qc-policy-status")
    if float(qc_policy.get("required_scores",{}).get("character_consistency",0))<4.0:
        errors.append("qc-policy-character-threshold")
    pub_policy=json.loads((root/"projects/slice01/rights/publication_policy.json").read_text(encoding="utf-8"))
    rights_register=json.loads((root/"projects/slice01/rights/rights_register.json").read_text(encoding="utf-8"))
    selected_assets=json.loads((root/"projects/slice01/rights/selected_assets.json").read_text(encoding="utf-8"))
    if pub_policy.get("publication_action_requires_owner_approval") is not True:
        errors.append("publication-owner-gate")
    if rights_register.get("status")!="INCOMPLETE_BLOCK_PUBLICATION":
        errors.append("publication-rights-register-status")
    if selected_assets.get("status")!="NO_FINAL_MEDIA_SELECTED" or selected_assets.get("assets")!=[]:
        errors.append("publication-selected-assets-state")
    rights_status={row.get("status") for row in rights_register.get("records",[])}
    if "UNKNOWN" not in rights_status:
        errors.append("publication-rights-must-remain-incomplete")
    required_batch009=[
        "film/BATCH009_CONTRACT.md",
        "film/asset_graph.py",
        "film/qc.py",
        "film/rights.py",
        "tools/plan_asset_invalidation.py",
        "tools/evaluate_qc_record.py",
        "tools/check_publication_gate.py",
    ]
    for rel in required_batch009:
        if not (root/rel).is_file():
            errors.append("batch009-missing:"+rel)


    prod_state=json.loads((root/"projects/slice01/production_state.json").read_text(encoding="utf-8"))
    prod_shots=prod_state.get("shots",[])
    if prod_state.get("status")!="READY_NO_GENERATED_TAKES" or len(prod_shots)!=8:
        errors.append("production-state-shape")
    if any(row.get("state")!="READY" or row.get("selected_take_id") is not None for row in prod_shots):
        errors.append("production-state-unexpected-selection")
    if prod_state.get("selection_history")!=[]:
        errors.append("production-state-selection-history")
    selected_takes=json.loads((root/"projects/slice01/edit/selected_takes.json").read_text(encoding="utf-8"))
    dialogue_tracks=json.loads((root/"projects/slice01/edit/dialogue_tracks.json").read_text(encoding="utf-8"))
    edit_placeholder=json.loads((root/"projects/slice01/edit/edit_plan.placeholder.json").read_text(encoding="utf-8"))
    if selected_takes.get("status")!="NO_TAKES_SELECTED" or selected_takes.get("selected_takes")!={}:
        errors.append("edit-selected-takes-state")
    if dialogue_tracks.get("status")!="NO_FINAL_DIALOGUE_AUDIO" or dialogue_tracks.get("tracks")!={}:
        errors.append("edit-dialogue-tracks-state")
    if edit_placeholder.get("status")!="BLOCKED_MISSING_MEDIA" or edit_placeholder.get("duration_sec")!=75.0 or edit_placeholder.get("render_authorized") is not False:
        errors.append("edit-placeholder-state")
    if len(edit_placeholder.get("blockers",[]))!=12:
        errors.append("edit-placeholder-blockers")
    required_batch010=[
        "film/BATCH010_CONTRACT.md",
        "film/production_state.py",
        "film/generation_control.py",
        "film/edit_plan.py",
        "tools/build_logical_generation_job.py",
        "tools/compile_edit_plan.py",
        "tools/create_selection_revision.py",
    ]
    for rel in required_batch010:
        if not (root/rel).is_file():
            errors.append("batch010-missing:"+rel)


    asset_catalog=json.loads((root/"projects/slice01/edit/asset_catalog.json").read_text(encoding="utf-8"))
    if asset_catalog.get("status")!="NO_FINAL_MEDIA_ASSETS" or asset_catalog.get("assets")!={}:
        errors.append("render-asset-catalog-state")
    tech_policy=json.loads((root/"projects/slice01/technical_qc_policy.json").read_text(encoding="utf-8"))
    if tech_policy.get("status")!="POLICY_READY_NO_FINAL_MEDIA" or tech_policy.get("duration_sec")!=75.0:
        errors.append("technical-qc-policy-state")
    delivery_inputs=json.loads((root/"projects/slice01/delivery/delivery_inputs.json").read_text(encoding="utf-8"))
    if delivery_inputs.get("status")!="WAITING_FINAL_MEDIA" or delivery_inputs.get("deliverables")!=[]:
        errors.append("delivery-input-state")
    expected_delivery={(row.get("aspect"),row.get("language")) for row in delivery_inputs.get("expected_variants",[])}
    if expected_delivery!={(a,l) for a in ("9:16","16:9") for l in ("en","zh-CN","vi")}:
        errors.append("delivery-variant-matrix")
    required_batch011=[
        "film/BATCH011_CONTRACT.md",
        "film/render_compile.py",
        "film/technical_qc.py",
        "film/delivery.py",
        "tools/compile_ffmpeg_render_spec.py",
        "tools/evaluate_technical_media_qc.py",
        "tools/build_delivery_manifest.py",
    ]
    for rel in required_batch011:
        if not (root/rel).is_file():
            errors.append("batch011-missing:"+rel)

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
