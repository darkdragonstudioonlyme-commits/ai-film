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
