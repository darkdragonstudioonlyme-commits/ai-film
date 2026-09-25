from __future__ import annotations

from typing import Any


class ReadinessError(ValueError):
    pass


def evaluate_stage_readiness(
    stages: list[dict[str, Any]],
    evidence: dict[str, bool],
) -> dict[str, Any]:
    ids=[row.get("stage_id") for row in stages]
    if any(not x for x in ids) or len(ids)!=len(set(ids)):
        raise ReadinessError("invalid/duplicate stage_id")
    by_id={row["stage_id"]:row for row in stages}
    order=[]
    remaining=set(ids)
    while remaining:
        progressed=False
        for stage_id in sorted(remaining):
            deps=set(by_id[stage_id].get("depends_on",[]))
            unknown=deps-set(by_id)
            if unknown:
                raise ReadinessError(f"unknown dependency for {stage_id}: {sorted(unknown)}")
            if deps.issubset(set(order)):
                order.append(stage_id)
                remaining.remove(stage_id)
                progressed=True
                break
        if not progressed:
            raise ReadinessError("stage dependency cycle")

    results={}
    for stage_id in order:
        stage=by_id[stage_id]
        completion=list(stage.get("completion_evidence",[]))
        requirements=list(stage.get("requires_evidence",[]))
        deps=list(stage.get("depends_on",[]))
        deps_complete=all(results[dep]["status"]=="COMPLETE" for dep in deps)
        if completion and all(evidence.get(key,False) for key in completion) and deps_complete:
            status="COMPLETE"
            blockers=[]
        else:
            blockers=[]
            for dep in deps:
                if results[dep]["status"]!="COMPLETE":
                    blockers.append(f"upstream-not-complete:{dep}")
            for key in requirements:
                if not evidence.get(key,False):
                    blockers.append(f"missing-evidence:{key}")
            status="READY" if not blockers else "BLOCKED"
        results[stage_id]={
            "stage_id":stage_id,
            "status":status,
            "depends_on":deps,
            "requires_evidence":requirements,
            "completion_evidence":completion,
            "blockers":blockers,
            "execution_permitted":False,
        }

    ready=[stage_id for stage_id in order if results[stage_id]["status"]=="READY"]
    frontier=[]
    for stage_id in order:
        row=results[stage_id]
        if row["status"]!="BLOCKED":
            continue
        if all(results[dep]["status"]=="COMPLETE" for dep in row["depends_on"]):
            frontier.append({
                "stage_id":stage_id,
                "blockers":[b for b in row["blockers"] if b.startswith("missing-evidence:")],
            })
    return {
        "schema_version":1,
        "status":"HAS_RUNNABLE_STAGE" if ready else "NO_RUNNABLE_STAGE",
        "stages":[results[x] for x in order],
        "ready_stages":ready,
        "blocking_frontier":frontier,
        "execution_permitted":False,
    }


SLICE01_STAGE_DAG=[
    {"stage_id":"source_ingestion","depends_on":[],"requires_evidence":[],"completion_evidence":["source_packet_ready"]},
    {"stage_id":"screenplay_localization","depends_on":["source_ingestion"],"requires_evidence":[],"completion_evidence":["screenplay_ready","localization_text_ready"]},
    {"stage_id":"continuity_shot_spec","depends_on":["screenplay_localization"],"requires_evidence":[],"completion_evidence":["continuity_ready","shots_ready","timing_ready"]},
    {"stage_id":"casting_reference_generation","depends_on":["continuity_shot_spec"],"requires_evidence":["paid_gpu_authorized"],"completion_evidence":["generated_casting_assets"]},
    {"stage_id":"voice_eval","depends_on":["screenplay_localization"],"requires_evidence":["paid_gpu_authorized"],"completion_evidence":["final_voice_eval_complete"]},
    {"stage_id":"visual_model_eval","depends_on":["casting_reference_generation"],"requires_evidence":["paid_gpu_authorized"],"completion_evidence":["visual_model_selected"]},
    {"stage_id":"video_generation","depends_on":["visual_model_eval"],"requires_evidence":["paid_gpu_authorized"],"completion_evidence":["selected_video_takes"]},
    {"stage_id":"audio_finalization","depends_on":["voice_eval"],"requires_evidence":["final_music_asset","music_rights_ready"],"completion_evidence":["final_audio_mix"]},
    {"stage_id":"lipsync","depends_on":["video_generation","audio_finalization"],"requires_evidence":[],"completion_evidence":["final_lipsync_assets"]},
    {"stage_id":"edit_render","depends_on":["video_generation","audio_finalization"],"requires_evidence":[],"completion_evidence":["rendered_final_media"]},
    {"stage_id":"delivery_qc","depends_on":["edit_render"],"requires_evidence":["publication_rights_ready","technical_qc_pass","creative_qc_pass"],"completion_evidence":["delivery_package_ready"]},
]
