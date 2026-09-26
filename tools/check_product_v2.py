#!/usr/bin/env python3
"""Structural contract for the active product-first control plane."""
from __future__ import annotations
import csv
import hashlib
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

    runtime_path=root/"model-evaluations/slice01/gpu-worker/runtime_lock.json"
    req_path=root/"model-evaluations/slice01/gpu-worker/requirements-base.lock.txt"
    runtime=json.loads(runtime_path.read_text(encoding="utf-8"))
    if runtime.get("status")!="PINNED_BASE_DRY_RUN_ONLY" or runtime.get("execution_ready") is not False:
        errors.append("gpu-runtime-authority")
    package_values=list((runtime.get("packages") or {}).values())
    if not package_values or any("tbd" in str(value).lower() for value in package_values):
        errors.append("gpu-runtime-package-pins")
    if runtime.get("packages",{}).get("huggingface-hub")!="1.33.0":
        errors.append("gpu-runtime-hfhub-pin")
    if "huggingface-hub==1.33.0" not in req_path.read_text(encoding="utf-8"):
        errors.append("gpu-requirements-hfhub-pin")
    resolver=json.loads((root/"run-evidence/RUNPOD_A40_RUNTIME_RESOLVER_20260925.json").read_text(encoding="utf-8"))
    if resolver.get("status")!="PASS" or resolver.get("successful_dry_run",{}).get("resolver_selected_huggingface_hub")!="1.33.0":
        errors.append("gpu-runtime-resolver-evidence")
    live_runtime=json.loads((root/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
    if live_runtime.get("status")!="RUNPOD_A40_HOST_BOUND_RUNTIME" or live_runtime.get("execution_ready") is not False:
        errors.append("gpu-runtime-a40-authority")
    if live_runtime.get("target",{}).get("torch")!="2.8.0+cu128" or live_runtime.get("packages",{}).get("huggingface-hub")!="1.33.0":
        errors.append("gpu-runtime-a40-binding")
    flux_qual=live_runtime.get("flux2_qualification") or {}
    if flux_qual.get("status")!="PASS_FORMAL_1024_FOUR_JOB" or flux_qual.get("peak_vram_mib")!=20415 or flux_qual.get("formal_1024_smoke_pending") is not False:
        errors.append("gpu-runtime-a40-flux2-formal-smoke")
    if flux_qual.get("admission_ready") is not True or flux_qual.get("required_vram_gb")!=20.0 or flux_qual.get("vram_reserve_gb")!=4.0:
        errors.append("gpu-runtime-a40-flux2-admission")
    worker_plan=json.loads((root/"run-evidence/GPU_WORKER_DRYRUN_20260925.json").read_text(encoding="utf-8"))
    if worker_plan.get("mode")!="DRY_RUN" or worker_plan.get("execution_ready") is not False:
        errors.append("gpu-worker-dryrun")
    if worker_plan.get("requirements_lock_sha256")!=hashlib.sha256(req_path.read_bytes()).hexdigest():
        errors.append("gpu-worker-requirements-hash")
    if worker_plan.get("runtime_lock_sha256")!=hashlib.sha256(runtime_path.read_bytes()).hexdigest():
        errors.append("gpu-worker-runtime-hash")

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
    if rates.get("RTX 5090")!=0.99 or rates.get("RTX Pro 6000")!=2.09 or rates.get("NVIDIA A40")!=0.49:
        errors.append("paid-gate-rate-drift")
    rate_body={k:v for k,v in rate_snap.items() if k!="snapshot_digest"}
    rate_digest=hashlib.sha256(json.dumps(rate_body,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if rate_snap.get("snapshot_digest")!=rate_digest:
        errors.append("paid-gate-rate-digest")

    placeholder=json.loads((root/"model-evaluations/slice01/launch_authorization.placeholder.json").read_text(encoding="utf-8"))
    if placeholder.get("status")!="NOT_AUTHORIZED" or placeholder.get("max_total_usd")!=0.0 or placeholder.get("allowed_gpus")!=[]:
        errors.append("paid-gate-placeholder-authority")

    active_auth=json.loads((root/"model-evaluations/slice01/launch_authorization.active.json").read_text(encoding="utf-8"))
    execution_plan=json.loads((root/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json").read_text(encoding="utf-8"))
    proposal=json.loads((root/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))
    proposal_digest=hashlib.sha256(json.dumps(proposal,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    plan_body={k:v for k,v in execution_plan.items() if k!="plan_digest"}
    plan_digest=hashlib.sha256(json.dumps(plan_body,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    auth_body={k:v for k,v in active_auth.items() if k!="receipt_digest"}
    auth_digest=hashlib.sha256(json.dumps(auth_body,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if execution_plan.get("plan_digest")!=plan_digest or execution_plan.get("gpu")!="NVIDIA A40" or execution_plan.get("max_total_usd")!=60.0:
        errors.append("paid-gate-execution-plan")
    if active_auth.get("status")!="AUTHORIZED" or active_auth.get("max_total_usd")!=60.0 or active_auth.get("allowed_gpus")!=["NVIDIA A40"]:
        errors.append("paid-gate-active-authority")
    if active_auth.get("new_resource_creation_authorized") is not False or active_auth.get("publish_authority") is not False:
        errors.append("paid-gate-active-scope")
    if active_auth.get("proposal_digest")!=proposal_digest or active_auth.get("execution_plan_digest")!=plan_digest or active_auth.get("rate_snapshot_digest")!=rate_digest:
        errors.append("paid-gate-active-binding")
    if active_auth.get("receipt_digest")!=auth_digest:
        errors.append("paid-gate-active-receipt-digest")
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


    resources=json.loads((root/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
    profiles=resources.get("profiles",[])
    if resources.get("status")!="PARTIAL_MEASUREMENTS_FLUX2_ZIMAGE_1024_READY_OTHERS_UNMEASURED" or len(profiles)!=5:
        errors.append("resource-profile-state")
    flux_profile=next((row for row in profiles if row.get("model_id")=="flux2-klein-4b"),None)
    if flux_profile is None:
        errors.append("resource-profile-flux2-missing")
    else:
        if flux_profile.get("admission_ready") is not True or flux_profile.get("vram_status")!="MEASURED":
            errors.append("resource-profile-flux2-admission-state")
        if flux_profile.get("required_vram_gb")!=20.0 or flux_profile.get("vram_reserve_gb")!=4.0:
            errors.append("resource-profile-flux2-vram-policy")
        if flux_profile.get("throughput_status")!="MEASURED_1024_FORMAL_SMOKE":
            errors.append("resource-profile-flux2-throughput-state")
        if flux_profile.get("formal_smoke_peak_nvidia_mib")!=20415 or flux_profile.get("formal_smoke_peak_torch_mib")!=20080.0:
            errors.append("resource-profile-flux2-formal-measurements")
        if flux_profile.get("production_resolution_vram_status")!="MEASURED_1024_FOUR_JOB_SMOKE":
            errors.append("resource-profile-flux2-production-boundary")
        if flux_profile.get("vram_policy")!="CEIL_MEASURED_PEAK_GIB_PLUS_4_GIB_RESERVE":
            errors.append("resource-profile-flux2-vram-policy-name")
    z_profile=next((row for row in profiles if row.get("model_id")=="z-image"),None)
    if z_profile is None:
        errors.append("resource-profile-zimage-missing")
    else:
        if z_profile.get("admission_ready") is not True or z_profile.get("vram_status")!="MEASURED":
            errors.append("resource-profile-zimage-admission-state")
        if z_profile.get("required_vram_gb")!=26.0 or z_profile.get("vram_reserve_gb")!=4.0:
            errors.append("resource-profile-zimage-vram-policy")
        if z_profile.get("throughput_status")!="MEASURED_1024_FORMAL_SMOKE":
            errors.append("resource-profile-zimage-throughput-state")
        if z_profile.get("qualification_peak_vram_mib")!=21913.0 or z_profile.get("qualification_inference_sec")!=21.623722:
            errors.append("resource-profile-zimage-qualification-measurements")
        if z_profile.get("formal_smoke_peak_nvidia_mib")!=26227 or z_profile.get("formal_smoke_peak_torch_mib")!=25892.0:
            errors.append("resource-profile-zimage-formal-measurements")
        if z_profile.get("production_resolution_vram_status")!="MEASURED_1024_FOUR_JOB_SMOKE":
            errors.append("resource-profile-zimage-production-boundary")
        if z_profile.get("vram_policy")!="CEIL_MEASURED_PEAK_GIB_PLUS_4_GIB_RESERVE":
            errors.append("resource-profile-zimage-vram-policy-name")
    other_profiles=[row for row in profiles if row.get("model_id") not in {"flux2-klein-4b","z-image"}]
    if any(row.get("admission_ready") is not False or row.get("vram_status")!="UNMEASURED" or row.get("required_vram_gb") is not None for row in other_profiles):
        errors.append("resource-profile-other-unmeasured-boundary")
    if any(row.get("throughput_status")!="UNMEASURED" for row in other_profiles):
        errors.append("resource-profile-other-throughput-claim")
    a40_tier=next((row for row in resources.get("worker_tiers",[]) if row.get("tier")=="RUNPOD_A40_48GB"),None)
    if a40_tier is None or a40_tier.get("measured_vram_mib")!=46068 or a40_tier.get("measurement_status")!="HOST_MEASURED_MODEL_STACK_UNMEASURED":
        errors.append("resource-profile-a40-host-measurement")

    host_evidence_path=root/"run-evidence/RUNPOD_A40_HOST_20260925.json"
    host_evidence=json.loads(host_evidence_path.read_text(encoding="utf-8"))
    if host_evidence.get("pod_id")!="0h1twwxqw6yx0k" or host_evidence.get("gpu",{}).get("name")!="NVIDIA A40" or host_evidence.get("gpu",{}).get("memory_total_mib")!=46068:
        errors.append("runpod-a40-host-evidence")
    if host_evidence.get("torch_version")!="2.8.0+cu128" or host_evidence.get("torch_cuda_available") is not True:
        errors.append("runpod-a40-torch-evidence")
    host_sha=hashlib.sha256(host_evidence_path.read_bytes()).hexdigest()
    worker=json.loads((root/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
    if worker.get("vram_status")!="MEASURED" or worker.get("available_vram_gb")!=44.988281 or worker.get("quarantined") is not False:
        errors.append("runpod-a40-worker-measurement")
    if worker.get("host_evidence_sha256")!=host_sha or worker.get("runtime_status")!="BASE_RUNTIME_MEASURED_FLUX2_ZIMAGE_1024_PASS_OTHER_ADAPTERS_PENDING":
        errors.append("runpod-a40-worker-binding")
    flux_worker=(worker.get("qualified_models") or {}).get("flux2-klein-4b",{})
    if flux_worker.get("status")!="PASS_FORMAL_1024_FOUR_JOB" or flux_worker.get("peak_vram_mib")!=20415 or flux_worker.get("formal_1024_smoke_pending") is not False:
        errors.append("runpod-a40-worker-flux2-formal-smoke")
    if flux_worker.get("admission_ready") is not True or flux_worker.get("required_vram_gb")!=20.0 or flux_worker.get("vram_reserve_gb")!=4.0:
        errors.append("runpod-a40-worker-flux2-admission")
    z_worker=(worker.get("qualified_models") or {}).get("z-image",{})
    if z_worker.get("status")!="PASS_FORMAL_1024_FOUR_JOB" or z_worker.get("peak_vram_mib")!=26227 or z_worker.get("formal_1024_smoke_pending") is not False:
        errors.append("runpod-a40-worker-zimage-formal-smoke")
    if z_worker.get("admission_ready") is not True or z_worker.get("required_vram_gb")!=26.0 or z_worker.get("vram_reserve_gb")!=4.0:
        errors.append("runpod-a40-worker-zimage-admission")

    queue_policy=json.loads((root/"projects/slice01/runtime/queue_policy.json").read_text(encoding="utf-8"))
    queue_state=json.loads((root/"projects/slice01/runtime/queue_state.json").read_text(encoding="utf-8"))
    if queue_policy.get("max_depth")!=16 or queue_policy.get("per_project_concurrency")!=2:
        errors.append("queue-policy-limits")
    if queue_state.get("status")!="NO_RUNTIME_QUEUE_STARTED" or queue_state.get("jobs")!=[]:
        errors.append("queue-state-not-empty")
    if queue_state.get("max_depth")!=16 or queue_state.get("per_project_concurrency")!=2:
        errors.append("queue-state-policy-drift")
    cost_policy=json.loads((root/"projects/slice01/runtime/cost_policy.json").read_text(encoding="utf-8"))
    cost_ledger=json.loads((root/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
    if cost_policy.get("status")!="AUTHORIZED_BOUNDED" or cost_policy.get("current_authorized_budget_usd")!=60.0:
        errors.append("cost-policy-authority")
    if cost_policy.get("authorization_id")!="T019-RUNPOD-A40-20260925" or cost_policy.get("rate_usd_per_hour")!=0.49:
        errors.append("cost-policy-binding")
    entries=cost_ledger.get("entries",[])
    by_cost_id={row.get("cost_id"):row for row in entries}
    expected_cost_ids={"runpod-a40-bootstrap-estimate-20260925","flux2-castjob_d3ec86da4ca6b1fc-pass","flux2-formal-smoke-20260925","zimage-castjob_8e02916e0db64eb6-pass","zimage-formal-smoke-20260926","voxcpm2-voxreq_7f50b3325b6132e8-pass"}
    if len(entries)!=6 or set(by_cost_id)!=expected_cost_ids:
        errors.append("cost-ledger-entry-population")
    else:
        if by_cost_id["runpod-a40-bootstrap-estimate-20260925"].get("category")!="OTHER" or abs(float(by_cost_id["runpod-a40-bootstrap-estimate-20260925"].get("amount_usd",0))-0.11027)>1e-9:
            errors.append("cost-ledger-bootstrap-entry")
        if by_cost_id["flux2-castjob_d3ec86da4ca6b1fc-pass"].get("category")!="COMPUTE_ACCEPTED" or abs(float(by_cost_id["flux2-castjob_d3ec86da4ca6b1fc-pass"].get("amount_usd",0))-0.00138)>1e-9:
            errors.append("cost-ledger-flux2-qualification-entry")
        if by_cost_id["flux2-formal-smoke-20260925"].get("category")!="COMPUTE_ACCEPTED" or abs(float(by_cost_id["flux2-formal-smoke-20260925"].get("amount_usd",0))-0.0021)>1e-9:
            errors.append("cost-ledger-flux2-formal-smoke-entry")
        if by_cost_id["zimage-castjob_8e02916e0db64eb6-pass"].get("category")!="COMPUTE_ACCEPTED" or abs(float(by_cost_id["zimage-castjob_8e02916e0db64eb6-pass"].get("amount_usd",0))-0.004647)>1e-9:
            errors.append("cost-ledger-zimage-qualification-entry")
        if by_cost_id["zimage-formal-smoke-20260926"].get("category")!="COMPUTE_ACCEPTED" or abs(float(by_cost_id["zimage-formal-smoke-20260926"].get("amount_usd",0))-0.048111)>1e-9:
            errors.append("cost-ledger-zimage-formal-smoke-entry")
        if by_cost_id["voxcpm2-voxreq_7f50b3325b6132e8-pass"].get("category")!="COMPUTE_ACCEPTED" or abs(float(by_cost_id["voxcpm2-voxreq_7f50b3325b6132e8-pass"].get("amount_usd",0))-0.004291)>1e-9:
            errors.append("cost-ledger-voxcpm2-qualification-entry")
        if abs(sum(float(row.get("amount_usd",0)) for row in entries)-0.170799)>1e-9:
            errors.append("cost-ledger-total-after-voxcpm2-qualification")
    required_batch012=[
        "film/BATCH012_CONTRACT.md",
        "film/admission.py",
        "film/queue_control.py",
        "film/cost_ledger.py",
        "tools/check_worker_admission.py",
        "tools/dispatch_queue_once.py",
        "tools/check_project_budget.py",
    ]
    for rel in required_batch012:
        if not (root/rel).is_file():
            errors.append("batch012-missing:"+rel)


    lip_policy=json.loads((root/"projects/slice01/lipsync/policy.json").read_text(encoding="utf-8"))
    lip_rows=lip_policy.get("dialogue_shots",[])
    if lip_policy.get("status")!="POLICY_READY_NO_FINAL_MEDIA" or len(lip_rows)!=4:
        errors.append("lipsync-policy-shape")
    if sum(bool(row.get("mouth_visible")) for row in lip_rows)!=3:
        errors.append("lipsync-visible-mouth-count")
    if {row.get("dialogue_id") for row in lip_rows}!={shot.get("dialogue_id") for shot in shots if shot.get("dialogue_id")}:
        errors.append("lipsync-dialogue-population")
    if set(lip_policy.get("backend_candidates",[]))!={"latentsync-1.6","musetalk"}:
        errors.append("lipsync-backend-candidates")
    for language in ("en","zh-CN","vi"):
        plan=json.loads((root/f"projects/slice01/lipsync/plan_{language}.json").read_text(encoding="utf-8"))
        if plan.get("status")!="BLOCKED_MISSING_MEDIA" or plan.get("execution_permitted") is not False:
            errors.append("lipsync-current-plan:"+language)
        if len(plan.get("requests",[]))!=3 or len(plan.get("skipped",[]))!=1:
            errors.append("lipsync-current-plan-shape:"+language)
        if plan.get("skipped",[{}])[0].get("dialogue_id")!="dlg_004":
            errors.append("lipsync-skip-policy:"+language)

    cue_sheet=json.loads((root/"projects/slice01/audio/cue_sheet.json").read_text(encoding="utf-8"))
    if cue_sheet.get("status")!="DESIGN_CUES_ASSETS_AND_RIGHTS_PENDING" or len(cue_sheet.get("cues",[]))!=7:
        errors.append("audio-cue-sheet-shape")
    if any(cue.get("source_status")!="PENDING_ASSET" or cue.get("rights_status")!="UNKNOWN" for cue in cue_sheet.get("cues",[])):
        errors.append("audio-cue-sheet-fake-clearance")
    mix_policy=json.loads((root/"projects/slice01/audio/mix_policy.json").read_text(encoding="utf-8"))
    if mix_policy.get("execution_permitted") is not False or mix_policy.get("target",{}).get("sample_rate_hz")!=48000:
        errors.append("audio-mix-policy")
    for language in ("en","zh-CN","vi"):
        plan=json.loads((root/f"projects/slice01/audio/mix_plan_{language}.json").read_text(encoding="utf-8"))
        if plan.get("status")!="BLOCKED_MISSING_ASSETS_OR_RIGHTS" or plan.get("execution_permitted") is not False:
            errors.append("audio-current-mix:"+language)
        if float(plan.get("duration_sec",0))!=75.0:
            errors.append("audio-current-mix-duration:"+language)

    required_batch013=[
        "film/BATCH013_CONTRACT.md",
        "film/lipsync_plan.py",
        "film/audio_cues.py",
        "film/audio_mix_plan.py",
        "tools/compile_lipsync_plan.py",
        "tools/validate_audio_cues.py",
        "tools/compile_audio_mix_plan.py",
    ]
    for rel in required_batch013:
        if not (root/rel).is_file():
            errors.append("batch013-missing:"+rel)


    screenplay=json.loads((root/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
    scenes=screenplay.get("scenes",[])
    if screenplay.get("master_language")!="en" or float(screenplay.get("target_duration_sec",0))!=75.0:
        errors.append("screenplay-core")
    if len(scenes)!=1 or len(scenes[0].get("beats",[]))!=6 or len(scenes[0].get("dialogue",[]))!=4:
        errors.append("screenplay-shape")
    source=screenplay.get("source",{})
    project_sha=hashlib.sha256((root/"projects/slice01/project.json").read_bytes()).hexdigest()
    if source.get("kind")!="ORIGINAL_PROJECT" or source.get("rights_id")!="source-original" or source.get("rights_status")!="ORIGINAL":
        errors.append("screenplay-source-rights")
    if source.get("source_identity_sha256")!=project_sha:
        errors.append("screenplay-source-identity")
    if {row.get("dialogue_id") for row in scenes[0].get("dialogue",[])} != {shot.get("dialogue_id") for shot in shots if shot.get("dialogue_id")}:
        errors.append("screenplay-dialogue-shot-drift")

    bundle=json.loads((root/"projects/slice01/localization/dialogue_bundle.json").read_text(encoding="utf-8"))
    if bundle.get("status")!="PARTIAL_TIMING_ZH_PENDING" or bundle.get("languages")!=["en","zh-CN","vi"] or len(bundle.get("lines",[]))!=4:
        errors.append("localization-bundle-shape")
    previs_sha=hashlib.sha256((root/"run-evidence/PREVIS_AUDIO_20260925.json").read_bytes()).hexdigest()
    for line in bundle.get("lines",[]):
        if set(line.get("texts",{})) != LANGS or any(not str(v).strip() for v in line.get("texts",{}).values()):
            errors.append("localization-text-coverage:"+str(line.get("dialogue_id")))
        measurements=line.get("timing_measurements",{})
        for language in ("en","vi"):
            row=measurements.get(language,{})
            if row.get("status")!="PREVIS_MEASURED" or row.get("evidence_sha256")!=previs_sha or row.get("duration_sec") is None:
                errors.append("localization-previs-evidence:"+str(line.get("dialogue_id"))+":"+language)
        zh=measurements.get("zh-CN",{})
        if zh.get("status")!="NOT_MEASURED" or zh.get("duration_sec") is not None or zh.get("evidence_sha256") is not None:
            errors.append("localization-zh-must-remain-unmeasured:"+str(line.get("dialogue_id")))

    reframe_policy=json.loads((root/"projects/slice01/framing/reframe_policy.json").read_text(encoding="utf-8"))
    reframe_plan=json.loads((root/"projects/slice01/framing/reframe_plan_16x9.json").read_text(encoding="utf-8"))
    if reframe_policy.get("master_aspect")!="9:16" or reframe_policy.get("target_aspect")!="16:9" or reframe_policy.get("crop_only_allowed") is not False:
        errors.append("reframe-policy")
    if len(reframe_policy.get("shots",[]))!=8 or {row.get("shot_id") for row in reframe_policy.get("shots",[])} != shot_ids:
        errors.append("reframe-policy-population")
    if reframe_plan.get("status")!="READY_FOR_RENDER_BACKEND" or reframe_plan.get("render_authorized") is not False:
        errors.append("reframe-current-plan")
    if len(reframe_plan.get("shots",[]))!=8 or reframe_plan.get("fallback_to_rerender_count")!=3:
        errors.append("reframe-current-plan-shape")
    if any(row.get("effective_strategy")!="RERENDER_FROM_SPEC" for row in reframe_plan.get("shots",[])):
        errors.append("reframe-current-plan-strategy")

    required_batch014=[
        "film/BATCH014_CONTRACT.md",
        "film/script_engine.py",
        "film/localization.py",
        "film/reframe.py",
        "tools/validate_screenplay.py",
        "tools/validate_localization_bundle.py",
        "tools/compile_reframe_plan.py",
    ]
    for rel in required_batch014:
        if not (root/rel).is_file():
            errors.append("batch014-missing:"+rel)


    coverage=json.loads((root/"projects/slice01/story/shot_coverage.json").read_text(encoding="utf-8"))
    if coverage.get("status")!="COMPLETE" or float(coverage.get("duration_sec",0))!=75.0:
        errors.append("story-coverage-status")
    if len(coverage.get("beat_coverage",[]))!=6 or len(coverage.get("shots",[]))!=8 or coverage.get("blockers")!=[]:
        errors.append("story-coverage-shape")
    if any(row.get("covered") is not True or not row.get("shot_ids") for row in coverage.get("beat_coverage",[])):
        errors.append("story-coverage-orphan-beat")
    if {row.get("shot_id") for row in coverage.get("shots",[])} != shot_ids:
        errors.append("story-coverage-shot-population")

    continuity_expectations=json.loads((root/"projects/slice01/continuity_expectations.json").read_text(encoding="utf-8"))
    exp_rows=continuity_expectations.get("shots",[])
    if continuity_expectations.get("status")!="EXPECTATIONS_READY_NO_VISUAL_OBSERVATIONS" or len(exp_rows)!=8:
        errors.append("continuity-expectations-status")
    if {row.get("shot_id") for row in exp_rows} != shot_ids:
        errors.append("continuity-expectations-population")
    if len({row.get("expectation_digest") for row in exp_rows})!=8 or any(len(str(row.get("expectation_digest","")))!=64 for row in exp_rows):
        errors.append("continuity-expectations-digest")
    sh06=next((row for row in exp_rows if row.get("shot_id")=="sc01_sh06"),None)
    if sh06 is None:
        errors.append("continuity-expectations-sh06-missing")
    else:
        if sh06.get("characters",{}).get("an",{}).get("injuries",{}).get("left_forearm")!="wrapped in clean white gauze":
            errors.append("continuity-expectations-sh06-injury")
        if sh06.get("characters",{}).get("linh",{}).get("props",{}).get("red_paper_crane")!="held in left hand":
            errors.append("continuity-expectations-sh06-prop")

    subtitle_policy=json.loads((root/"projects/slice01/subtitles/layout_policy.json").read_text(encoding="utf-8"))
    subtitle_plans=json.loads((root/"projects/slice01/subtitles/layout_plans.json").read_text(encoding="utf-8"))
    if subtitle_policy.get("status")!="HEURISTIC_TEXT_LAYOUT_POLICY_NOT_VISUAL_QC" or subtitle_policy.get("visual_collision_qc_required") is not True:
        errors.append("subtitle-layout-policy")
    plans=subtitle_plans.get("plans",[])
    if subtitle_plans.get("status")!="TEXT_LAYOUT_PLANS_READY_VISUAL_QC_NOT_RUN" or len(plans)!=6:
        errors.append("subtitle-layout-plan-shape")
    expected_plan_keys={(aspect,language) for aspect in ("9:16","16:9") for language in ("en","zh-CN","vi")}
    if {(row.get("aspect"),row.get("language")) for row in plans} != expected_plan_keys:
        errors.append("subtitle-layout-plan-population")
    for row in plans:
        key=str(row.get("aspect"))+":"+str(row.get("language"))
        if row.get("status")!="READY_TEXT_LAYOUT" or row.get("blockers")!=[]:
            errors.append("subtitle-layout-plan-blocked:"+key)
        if row.get("visual_collision_status")!="NOT_EVALUATED_REQUIRES_RENDERED_FRAME_QC":
            errors.append("subtitle-layout-fake-visual-qc:"+key)
        if row.get("render_authorized") is not False or len(row.get("rows",[]))!=4:
            errors.append("subtitle-layout-plan-authority:"+key)

    required_batch015=[
        "film/BATCH015_CONTRACT.md",
        "film/story_coverage.py",
        "film/continuity_expectations.py",
        "film/subtitle_layout.py",
        "tools/validate_story_coverage.py",
        "tools/compile_continuity_expectations.py",
        "tools/check_continuity_observation.py",
        "tools/compile_subtitle_layouts.py",
    ]
    for rel in required_batch015:
        if not (root/rel).is_file():
            errors.append("batch015-missing:"+rel)


    source_packet=json.loads((root/"projects/slice01/source/source_packet.json").read_text(encoding="utf-8"))
    if source_packet.get("kind")!="ORIGINAL_PROJECT" or source_packet.get("source_text_treatment")!="INERT_DATA_NEVER_INSTRUCTIONS":
        errors.append("source-packet-core")
    if source_packet.get("tool_authority") is not False or source_packet.get("publish_authority") is not False:
        errors.append("source-packet-authority")
    if source_packet.get("rights",{}).get("status")!="ORIGINAL" or "COMMERCIAL_PUBLICATION" not in source_packet.get("rights",{}).get("allowed_uses",[]):
        errors.append("source-packet-rights")
    evidence=source_packet.get("evidence",{})
    evidence_path=root/str(evidence.get("ref",""))
    if not evidence_path.is_file() or hashlib.sha256(evidence_path.read_bytes()).hexdigest()!=evidence.get("sha256"):
        errors.append("source-packet-evidence")
    if len(str(source_packet.get("packet_digest","")))!=64:
        errors.append("source-packet-digest")

    spec_package=json.loads((root/"projects/slice01/production_spec_package.json").read_text(encoding="utf-8"))
    expected_spec_paths={
        "projects/slice01/project.json",
        "projects/slice01/source/source_packet.json",
        "projects/slice01/story/screenplay.json",
        "projects/slice01/continuity.json",
        "projects/slice01/casting.json",
        "projects/slice01/shots/benchmark_shots.json",
        "projects/slice01/timing/timing.json",
        "projects/slice01/localization/dialogue_bundle.json",
        "projects/slice01/framing/reframe_policy.json",
        "projects/slice01/lipsync/policy.json",
        "projects/slice01/audio/cue_sheet.json",
        "projects/slice01/audio/mix_policy.json",
        "projects/slice01/qc_policy.json",
        "projects/slice01/rights/publication_policy.json",
        "projects/slice01/subtitles/layout_policy.json",
    }
    package_entries=spec_package.get("entries",[])
    if spec_package.get("status")!="SPEC_ONLY_NO_GENERATED_MEDIA" or spec_package.get("entry_count")!=15:
        errors.append("production-spec-package-shape")
    if {row.get("path") for row in package_entries}!=expected_spec_paths:
        errors.append("production-spec-package-population")
    if any(spec_package.get(key) is not False for key in ("contains_generated_media","contains_runtime_receipts","contains_secrets","execution_authority","publish_authority")):
        errors.append("production-spec-package-authority")
    forbidden_parts={"runtime","compiled","delivery","artifacts","run-evidence","secrets","credentials"}
    for entry in package_entries:
        rel=str(entry.get("path",""))
        if set(rel.split("/")) & forbidden_parts:
            errors.append("production-spec-package-forbidden:"+rel)
            continue
        full=root/rel
        if not full.is_file():
            errors.append("production-spec-package-missing:"+rel)
            continue
        if hashlib.sha256(full.read_bytes()).hexdigest()!=entry.get("sha256") or full.stat().st_size!=entry.get("bytes"):
            errors.append("production-spec-package-identity:"+rel)

    required_batch016=[
        "film/BATCH016_CONTRACT.md",
        "film/source_ingest.py",
        "film/project_scaffold.py",
        "film/production_package.py",
        "tools/ingest_source_packet.py",
        "tools/scaffold_project.py",
        "tools/build_production_spec_package.py",
    ]
    for rel in required_batch016:
        if not (root/rel).is_file():
            errors.append("batch016-missing:"+rel)


    schema_report=json.loads((root/"projects/slice01/schema_compatibility.json").read_text(encoding="utf-8"))
    expected_legacy={
        "projects/slice01/project.json",
        "projects/slice01/casting.json",
        "projects/slice01/continuity.json",
        "projects/slice01/shots/benchmark_shots.json",
    }
    if schema_report.get("status")!="UPGRADE_REQUIRED" or set(schema_report.get("upgrade_required",[]))!=expected_legacy:
        errors.append("schema-compatibility-current-report")
    if schema_report.get("unsupported")!=[] or schema_report.get("mutations_applied") is not False:
        errors.append("schema-compatibility-mutation-or-unsupported")
    for row in schema_report.get("documents",[]):
        if row.get("apply_authorized") is not False:
            errors.append("schema-compatibility-authority:"+str(row.get("name")))

    readiness=json.loads((root/"projects/slice01/readiness/stage_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("status")!="HAS_RUNNABLE_STAGE" or set(readiness.get("ready_stages",[]))!={"casting_reference_generation","voice_eval"} or readiness.get("execution_permitted") is not False:
        errors.append("stage-readiness-current-status")
    if readiness.get("blocking_frontier")!=[]:
        errors.append("stage-readiness-frontier")
    if readiness.get("evidence",{}).get("paid_gpu_authorized") is not True:
        errors.append("stage-readiness-paid-authority")
    readiness_by={row.get("stage_id"):row for row in readiness.get("stages",[])}
    for stage_id in ("casting_reference_generation","voice_eval"):
        row=readiness_by.get(stage_id,{})
        if row.get("status")!="READY" or row.get("execution_permitted") is not False or row.get("blockers")!=[]:
            errors.append("stage-readiness-ready-stage:"+stage_id)

    required_batch017=[
        "film/BATCH017_CONTRACT.md",
        "film/spec_transport.py",
        "film/schema_compat.py",
        "film/stage_readiness.py",
        "tools/export_spec_bundle.py",
        "tools/import_spec_bundle.py",
        "tools/plan_schema_compatibility.py",
        "tools/build_stage_readiness.py",
    ]
    for rel in required_batch017:
        if not (root/rel).is_file():
            errors.append("batch017-missing:"+rel)


    flux_qual_evidence=json.loads((root/"run-evidence/FLUX2_KLEIN_A40_QUALIFICATION_20260925.json").read_text(encoding="utf-8"))
    if flux_qual_evidence.get("status")!="PASS_512_QUALIFICATION" or flux_qual_evidence.get("model_revision")!="e7b7dc27f91deacad38e78976d1f2b499d76a294":
        errors.append("flux2-qualification-evidence-status")
    if flux_qual_evidence.get("measurements",{}).get("gpu_peak_memory_mb")!=16577.0 or flux_qual_evidence.get("measurements",{}).get("inference_sec")!=1.285966:
        errors.append("flux2-qualification-evidence-measurement")
    if flux_qual_evidence.get("artifact",{}).get("sha256")!="f1af28a78a13be0bc8f3cb82f591f6c2bfa7046658b51b142c67532dc2871bf9" or flux_qual_evidence.get("artifact",{}).get("persistence_status")!="POD_LOCAL_ONLY_PENDING_SYNC":
        errors.append("flux2-qualification-artifact-identity")
    if flux_qual_evidence.get("admission_ready_after_qualification") is not False or flux_qual_evidence.get("next_gate")!="FORMAL_1024X1024_FOUR_JOB_SMOKE":
        errors.append("flux2-qualification-boundary")

    flux_formal=json.loads((root/"run-evidence/FLUX2_KLEIN_A40_FORMAL_SMOKE_20260925.json").read_text(encoding="utf-8"))
    if flux_formal.get("status")!="PASS_FORMAL_1024_FOUR_JOB_SMOKE" or flux_formal.get("passed_jobs")!=4 or flux_formal.get("failed_jobs")!=0:
        errors.append("flux2-formal-smoke-status")
    if flux_formal.get("measurements",{}).get("max_nvidia_smi_memory_mib")!=20415 or flux_formal.get("measurements",{}).get("max_torch_peak_memory_mb")!=20080.0:
        errors.append("flux2-formal-smoke-vram")
    if flux_formal.get("measurements",{}).get("estimated_compute_cost_usd")!=0.0021 or flux_formal.get("post_run_budget",{}).get("projected_total_usd")!=0.11375:
        errors.append("flux2-formal-smoke-cost")
    if len(flux_formal.get("outputs",[]))!=4 or any(row.get("width")!=1024 or row.get("height")!=1024 for row in flux_formal.get("outputs",[])):
        errors.append("flux2-formal-smoke-output-population")
    if flux_formal.get("post_run_model_dir_validation",{}).get("required_file_count")!=18 or flux_formal.get("post_run_model_dir_validation",{}).get("required_bytes")!=15980131745:
        errors.append("flux2-formal-smoke-model-dir-validation")
    if flux_formal.get("production_acceptance") is not False or flux_formal.get("selection_authorized") is not False or flux_formal.get("publish_authority") is not False:
        errors.append("flux2-formal-smoke-authority")

    # Live FLUX.2 klein runner contract must remain plan-first and exact-authority bound.
    if not (root/"film/flux2_klein_live.py").is_file() or not (root/"tools/run_flux2_klein_live.py").is_file():
        errors.append("flux2-live-runner-missing")
    else:
        flux_job=next((row for row in cast_jobs if row.get("model_id")=="flux2-klein-4b" and row.get("job_id")=="castjob_d3ec86da4ca6b1fc"),None)
        if flux_job is None:
            errors.append("flux2-live-runner-canonical-job-missing")
        flux_model=next((row for row in models if row.get("model_id")=="flux2-klein-4b"),None)
        if flux_model is None or flux_model.get("source_revision")!="e7b7dc27f91deacad38e78976d1f2b499d76a294":
            errors.append("flux2-live-runner-model-revision")
        if flux_model is not None and flux_model.get("execution_ready") is not False:
            errors.append("flux2-live-runner-model-must-remain-unmeasured")
        if active_auth.get("status")!="AUTHORIZED" or active_auth.get("max_total_usd")!=60.0:
            errors.append("flux2-live-runner-active-authority")
        if execution_plan.get("gpu")!="NVIDIA A40" or execution_plan.get("new_resource_creation_authorized") is not False:
            errors.append("flux2-live-runner-execution-plan")

    flux_casting_profile=json.loads((root/"model-evaluations/slice01/flux2_casting_profile.json").read_text(encoding="utf-8"))
    if flux_casting_profile.get("profile_id")!="flux2-klein-4b-casting-a40-v1":
        errors.append("flux2-casting-smoke-profile-id")
    if flux_casting_profile.get("model_id")!="flux2-klein-4b" or flux_casting_profile.get("revision")!="e7b7dc27f91deacad38e78976d1f2b499d76a294":
        errors.append("flux2-casting-smoke-model")
    if flux_casting_profile.get("gpu")!="NVIDIA A40" or flux_casting_profile.get("dtype")!="bfloat16" or flux_casting_profile.get("mode")!="FULL_GPU":
        errors.append("flux2-casting-smoke-runtime")
    if flux_casting_profile.get("width")!=1024 or flux_casting_profile.get("height")!=1024 or flux_casting_profile.get("num_inference_steps")!=4 or float(flux_casting_profile.get("guidance_scale",-1))!=1.0:
        errors.append("flux2-casting-smoke-params")
    if flux_casting_profile.get("smoke_jobs")!=4 or flux_casting_profile.get("execution_authorized_by_profile") is not False:
        errors.append("flux2-casting-smoke-authority")
    if flux_casting_profile.get("runtime_lock_ref")!="model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json":
        errors.append("flux2-casting-smoke-runtime-ref")
    if flux_casting_profile.get("authorization_ref")!="model-evaluations/slice01/launch_authorization.active.json":
        errors.append("flux2-casting-smoke-auth-ref")
    for rel in (
        "film/flux2_casting.py",
        "tools/run_flux2_casting_batch.py",
        "tests/film/test_flux2_casting_smoke_runner.py",
        "reviews/PRODUCT-V2-FLUX2-CASTING-SMOKE-RUNNER-REVIEW.md",
    ):
        if not (root/rel).is_file():
            errors.append("flux2-casting-smoke-missing:"+rel)


    z_qual_evidence=json.loads((root/"run-evidence/Z_IMAGE_A40_QUALIFICATION_20260925.json").read_text(encoding="utf-8"))
    if z_qual_evidence.get("status")!="PASS_512_QUALIFICATION" or z_qual_evidence.get("model_revision")!="04cc4abb7c5069926f75c9bfde9ef43d49423021":
        errors.append("zimage-qualification-evidence-status")
    if z_qual_evidence.get("measurements",{}).get("gpu_peak_memory_mb")!=21913.0 or z_qual_evidence.get("measurements",{}).get("inference_sec")!=21.623722:
        errors.append("zimage-qualification-evidence-measurement")
    if z_qual_evidence.get("artifact",{}).get("sha256")!="682f2ae66cf262004e5487d809e7c840c8a4fc2e86ba8529f98a446294a2f567" or z_qual_evidence.get("artifact",{}).get("persistence_status")!="POD_LOCAL_ONLY_PENDING_SYNC":
        errors.append("zimage-qualification-artifact-identity")
    if z_qual_evidence.get("raw_evidence",{}).get("sha256")!="db0dec072f4c77aff01e5cf97d5145ec376b97e32c0d22086d4c8f2659465af4":
        errors.append("zimage-qualification-raw-evidence")
    if z_qual_evidence.get("admission_ready_after_qualification") is not False or z_qual_evidence.get("next_gate")!="FORMAL_1024X1024_FOUR_JOB_SMOKE":
        errors.append("zimage-qualification-boundary")

    # Live Z-Image qualification runner must remain plan-first, exact-revision and non-authorizing.
    if not (root/"film/z_image_live.py").is_file() or not (root/"tools/run_z_image_live.py").is_file():
        errors.append("z-image-live-runner-missing")
    else:
        z_job=next((row for row in cast_jobs if row.get("model_id")=="z-image" and row.get("job_id")=="castjob_8e02916e0db64eb6"),None)
        if z_job is None:
            errors.append("z-image-live-runner-canonical-job-missing")
        else:
            if z_job.get("model_revision")!="04cc4abb7c5069926f75c9bfde9ef43d49423021":
                errors.append("z-image-live-runner-job-revision")
            if not str(z_job.get("negative_prompt","")).strip():
                errors.append("z-image-live-runner-negative-prompt")
        z_model=next((row for row in models if row.get("model_id")=="z-image"),None)
        if z_model is None or z_model.get("source_revision")!="04cc4abb7c5069926f75c9bfde9ef43d49423021":
            errors.append("z-image-live-runner-model-revision")
        else:
            if z_model.get("license_gate")!="UPSTREAM_APACHE_2_0_PINNED":
                errors.append("z-image-live-runner-license")
            if z_model.get("commercial_production_allowed")!="UPSTREAM_MODEL_LICENSE_PERMITS":
                errors.append("z-image-live-runner-commercial-gate")
            if z_model.get("production_gate")!="PENDING_DEPENDENCY_DATASET_AND_PUBLICATION_REVIEW":
                errors.append("z-image-live-runner-production-gate")
            if z_model.get("execution_ready") is not False:
                errors.append("z-image-live-runner-model-authority")
        if active_auth.get("status")!="AUTHORIZED" or active_auth.get("max_total_usd")!=60.0:
            errors.append("z-image-live-runner-active-authority")
        if execution_plan.get("gpu")!="NVIDIA A40" or execution_plan.get("new_resource_creation_authorized") is not False:
            errors.append("z-image-live-runner-execution-plan")
        live_runtime=json.loads((root/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json").read_text(encoding="utf-8"))
        if live_runtime.get("target",{}).get("torch")!="2.8.0+cu128" or live_runtime.get("packages",{}).get("diffusers")!="0.40.0":
            errors.append("z-image-live-runner-runtime")
        required_z_files=[
            "film/z_image_live.py",
            "tools/run_z_image_live.py",
            "tests/film/test_z_image_live_runner.py",
            "reviews/PRODUCT-V2-Z-IMAGE-LIVE-RUNNER-REVIEW.md",
        ]
        for rel in required_z_files:
            if not (root/rel).is_file():
                errors.append("z-image-live-runner-missing:"+rel)


    z_casting_profile=json.loads((root/"model-evaluations/slice01/z_image_casting_profile.json").read_text(encoding="utf-8"))
    if z_casting_profile.get("profile_id")!="z-image-casting-a40-v1":
        errors.append("zimage-casting-smoke-profile-id")
    if z_casting_profile.get("model_id")!="z-image" or z_casting_profile.get("revision")!="04cc4abb7c5069926f75c9bfde9ef43d49423021":
        errors.append("zimage-casting-smoke-model")
    if z_casting_profile.get("gpu")!="NVIDIA A40" or z_casting_profile.get("dtype")!="bfloat16" or z_casting_profile.get("mode")!="FULL_GPU":
        errors.append("zimage-casting-smoke-runtime")
    if (
        z_casting_profile.get("width")!=1024
        or z_casting_profile.get("height")!=1024
        or z_casting_profile.get("num_inference_steps")!=50
        or float(z_casting_profile.get("guidance_scale",-1))!=4.0
        or z_casting_profile.get("cfg_normalization") is not False
        or z_casting_profile.get("low_cpu_mem_usage") is not False
    ):
        errors.append("zimage-casting-smoke-params")
    if z_casting_profile.get("negative_prompt_mode")!="NATIVE_JOB_NEGATIVE_PROMPT":
        errors.append("zimage-casting-smoke-negative-prompt")
    if z_casting_profile.get("smoke_jobs")!=4 or z_casting_profile.get("execution_authorized_by_profile") is not False:
        errors.append("zimage-casting-smoke-authority")
    if z_casting_profile.get("runtime_lock_ref")!="model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json":
        errors.append("zimage-casting-smoke-runtime-ref")
    if z_casting_profile.get("authorization_ref")!="model-evaluations/slice01/launch_authorization.active.json":
        errors.append("zimage-casting-smoke-auth-ref")
    for rel in (
        "film/z_image_casting.py",
        "tools/run_z_image_casting_batch.py",
        "tests/film/test_z_image_casting_smoke_runner.py",
        "reviews/PRODUCT-V2-Z-IMAGE-CASTING-SMOKE-RUNNER-REVIEW.md",
    ):
        if not (root/rel).is_file():
            errors.append("zimage-casting-smoke-missing:"+rel)


    z_formal=json.loads((root/"run-evidence/Z_IMAGE_A40_FORMAL_SMOKE_20260926.json").read_text(encoding="utf-8"))
    if z_formal.get("status")!="PASS_FORMAL_1024_FOUR_JOB_SMOKE" or z_formal.get("passed_jobs")!=4 or z_formal.get("failed_jobs")!=0:
        errors.append("zimage-formal-smoke-status")
    if z_formal.get("measurements",{}).get("max_nvidia_smi_memory_mib")!=26227 or z_formal.get("measurements",{}).get("max_torch_peak_memory_mb")!=25892.0:
        errors.append("zimage-formal-smoke-vram")
    if z_formal.get("measurements",{}).get("estimated_compute_cost_usd")!=0.048111 or z_formal.get("post_run_budget",{}).get("projected_total_usd")!=0.166508:
        errors.append("zimage-formal-smoke-cost")
    if z_formal.get("raw_evidence",{}).get("sha256")!="ce43303ec34682f843b9b4e16ef39a68d40a51fd9e4ff04bd21fb0fbb2a9b942":
        errors.append("zimage-formal-smoke-raw-evidence")
    if len(z_formal.get("outputs",[]))!=4 or any(row.get("width")!=1024 or row.get("height")!=1024 for row in z_formal.get("outputs",[])):
        errors.append("zimage-formal-smoke-output-population")
    if z_formal.get("model_snapshot_shape",{}).get("required_file_count")!=18 or z_formal.get("model_snapshot_shape",{}).get("required_bytes")!=20538488559:
        errors.append("zimage-formal-smoke-model-dir-validation")
    if z_formal.get("admission_ready_after_smoke") is not True or z_formal.get("selection_authorized") is not False or z_formal.get("production_acceptance") is not False:
        errors.append("zimage-formal-smoke-boundary")

    comparison=json.loads((root/"projects/slice01/casting/formal_comparison/blind_items.json").read_text(encoding="utf-8"))
    comparison_private=json.loads((root/"projects/slice01/casting/formal_comparison/blind_map_private.json").read_text(encoding="utf-8"))
    if comparison.get("status")!="AWAITING_BLIND_SCORES" or comparison.get("sample_count")!=8 or comparison.get("selection_authorized") is not False:
        errors.append("image-model-comparison-status")
    if len(comparison.get("items",[]))!=8 or len(comparison_private.get("mapping",[]))!=8:
        errors.append("image-model-comparison-population")
    if any("model_id" in row or "job_id" in row or "model_revision" in row for row in comparison.get("items",[])):
        errors.append("image-model-comparison-public-leak")
    materialization=comparison.get("neutral_materialization",{})
    if materialization.get("status")!="PASS_8_VERIFIED_POD_LOCAL_NEUTRAL_COPIES" or materialization.get("manifest_sha256")!="2dbc18d0f9ebc56024980b864a7fc27d6633a18ed9741049f851404512fe2728" or materialization.get("model_identity_in_manifest") is not False:
        errors.append("image-model-comparison-neutral-materialization")
    if any(row.get("asset_locator_status")!="POD_LOCAL_NEUTRAL_COPY_VERIFIED" or row.get("pod_neutral_path")!=f"/workspace/artifacts/blind-comparison/{row.get('blind_id')}.png" for row in comparison.get("items",[])):
        errors.append("image-model-comparison-neutral-paths")
    if {row.get("model_id") for row in comparison_private.get("mapping",[])}!={"flux2-klein-4b","z-image"}:
        errors.append("image-model-comparison-private-models")
    score_text=(root/"projects/slice01/casting/formal_comparison/scores.csv").read_text(encoding="utf-8")
    if any(token.strip() for line in score_text.splitlines()[1:] for token in line.split(",")[1:-2]):
        errors.append("image-model-comparison-scores-must-remain-blank")
    for rel in (
        "film/image_model_blind_compare.py",
        "tools/build_image_model_blind_comparison.py",
        "tests/film/test_image_model_blind_comparison.py",
        "tests/film/test_z_image_formal_smoke_evidence.py",
        "reviews/PRODUCT-V2-Z-IMAGE-FORMAL-SMOKE-REVIEW.md",
    ):
        if not (root/rel).is_file():
            errors.append("zimage-formal-comparison-missing:"+rel)

    blind_materialization=json.loads((root/"run-evidence/IMAGE_MODEL_BLIND_MATERIALIZATION_20260926.json").read_text(encoding="utf-8"))
    if blind_materialization.get("status")!="PASS_8_NEUTRAL_COPIES_VERIFIED" or blind_materialization.get("sample_count")!=8 or blind_materialization.get("selection_authorized") is not False:
        errors.append("image-model-blind-materialization-evidence")
    if blind_materialization.get("manifest",{}).get("sha256")!="2dbc18d0f9ebc56024980b864a7fc27d6633a18ed9741049f851404512fe2728" or blind_materialization.get("manifest",{}).get("model_identity_in_manifest") is not False:
        errors.append("image-model-blind-materialization-manifest")
    vox_qual=json.loads((root/"run-evidence/VOXCPM2_A40_QUALIFICATION_20260926.json").read_text(encoding="utf-8"))
    if vox_qual.get("status")!="PASS_SINGLE_SAMPLE_RUNTIME_QUALIFICATION" or vox_qual.get("request",{}).get("request_id")!="voxreq_7f50b3325b6132e8":
        errors.append("voxcpm2-qualification-status")
    if vox_qual.get("measurements",{}).get("gpu_peak_memory_mib")!=5827.0 or vox_qual.get("measurements",{}).get("estimated_compute_cost_usd")!=0.004291:
        errors.append("voxcpm2-qualification-measurements")
    if vox_qual.get("output",{}).get("cue_fit") is not True or vox_qual.get("output",{}).get("sha256")!="f562abbb391460d4cda9f75c0930bfe8ccb603257fd971b6a8a19a33544d3940":
        errors.append("voxcpm2-qualification-output")
    if vox_qual.get("request",{}).get("reference_audio") is not None or vox_qual.get("request",{}).get("voice_cloning") is not False or vox_qual.get("quality_status")!="NOT_EVALUATED":
        errors.append("voxcpm2-qualification-boundary")
    voice_profiles=json.loads((root/"model-evaluations/slice01/voice/resource_profiles.json").read_text(encoding="utf-8"))
    vp=(voice_profiles.get("profiles") or [{}])[0]
    if voice_profiles.get("status")!="VOXCPM2_QUALIFICATION_MEASURED_FORMAL_PACKET_PENDING" or vp.get("model_id")!="voxcpm2":
        errors.append("voxcpm2-resource-profile-status")
    if vp.get("required_vram_gb")!=6.0 or vp.get("vram_reserve_gb")!=4.0 or vp.get("admission_threshold_gb")!=10.0 or vp.get("admission_ready") is not True:
        errors.append("voxcpm2-resource-profile-vram")
    if vp.get("formal_packet_status")!="NOT_RUN_11_REMAINING_SAMPLES" or vp.get("quality_status")!="NOT_EVALUATED" or vp.get("production_acceptance") is not False:
        errors.append("voxcpm2-resource-profile-boundary")

    for rel in (
        "run-evidence/IMAGE_MODEL_BLIND_MATERIALIZATION_20260926.json",
        "run-evidence/VOXCPM2_A40_QUALIFICATION_20260926.json",
        "model-evaluations/slice01/voice/resource_profiles.json",
        "tests/film/test_voxcpm2_qualification_evidence.py",
        "reviews/PRODUCT-V2-VOXCPM2-QUALIFICATION-REVIEW.md",
    ):
        if not (root/rel).is_file():
            errors.append("voxcpm2-qualification-evidence-missing:"+rel)

    for rel in (
        "film/voxcpm2_live.py",
        "tools/run_voxcpm2_live.py",
        "tests/film/test_voxcpm2_live_runner.py",
        "reviews/PRODUCT-V2-VOXCPM2-LIVE-RUNNER-REVIEW.md",
    ):
        if not (root/rel).is_file():
            errors.append("voxcpm2-live-runner-missing:"+rel)

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
