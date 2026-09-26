from __future__ import annotations

import csv
import hashlib
import json
from io import StringIO
from typing import Any

from .blind_scoring import (
    BlindScoreError,
    ScoreSchema,
    parse_score_csv,
    unblind_and_rank,
    validate_complete_scores,
)


class ImageModelComparisonError(ValueError):
    pass


COMPARISON_ID="slice01-face-front-flux2-vs-zimage-v1"
SCORE_SCHEMA=ScoreSchema(criteria=(
    "identity_match",
    "prompt_adherence",
    "style_quality",
    "anatomy_artifact_free",
    "overall",
))


def _validate_evidence(evidence: dict[str,Any], expected_model_id: str) -> list[dict[str,Any]]:
    if evidence.get("status")!="PASS_FORMAL_1024_FOUR_JOB_SMOKE":
        raise ImageModelComparisonError(f"{expected_model_id} formal smoke not PASS")
    if evidence.get("model_id")!=expected_model_id:
        raise ImageModelComparisonError(f"{expected_model_id} model identity mismatch")
    if evidence.get("planned_jobs")!=4 or evidence.get("passed_jobs")!=4 or evidence.get("failed_jobs")!=0:
        raise ImageModelComparisonError(f"{expected_model_id} formal smoke population mismatch")
    if evidence.get("selection_authorized") is not False or evidence.get("production_acceptance") is not False:
        raise ImageModelComparisonError(f"{expected_model_id} evidence improperly grants selection/acceptance")
    rows=evidence.get("outputs")
    if not isinstance(rows,list) or len(rows)!=4:
        raise ImageModelComparisonError(f"{expected_model_id} output population mismatch")
    expected={
        ("an","photoreal","face_front"),
        ("an","stylized_3d","face_front"),
        ("linh","photoreal","face_front"),
        ("linh","stylized_3d","face_front"),
    }
    actual={(row.get("character_id"),row.get("style"),row.get("slot")) for row in rows}
    if actual!=expected:
        raise ImageModelComparisonError(f"{expected_model_id} comparison population drift")
    for row in rows:
        if row.get("width")!=1024 or row.get("height")!=1024:
            raise ImageModelComparisonError(f"{expected_model_id} output resolution drift")
        for field in ("asset_sha256","manifest_sha256"):
            value=row.get(field)
            if not isinstance(value,str) or len(value)!=64:
                raise ImageModelComparisonError(f"{expected_model_id} invalid {field}")
    return rows


def _blind_id(asset_sha256: str) -> str:
    return "cmp_"+hashlib.sha256(
        (COMPARISON_ID+":"+asset_sha256).encode("utf-8")
    ).hexdigest()[:12]


def build_comparison_packet(
    flux_evidence: dict[str,Any],
    zimage_evidence: dict[str,Any],
    materialization_evidence: dict[str,Any] | None = None,
) -> tuple[dict[str,Any],dict[str,Any]]:
    flux_rows=_validate_evidence(flux_evidence,"flux2-klein-4b")
    z_rows=_validate_evidence(zimage_evidence,"z-image")

    public=[]
    private=[]
    for evidence,rows in ((flux_evidence,flux_rows),(zimage_evidence,z_rows)):
        model_id=evidence["model_id"]
        revision=evidence["model_revision"]
        for row in rows:
            blind_id=_blind_id(row["asset_sha256"])
            public.append({
                "blind_id":blind_id,
                "character_id":row["character_id"],
                "style":row["style"],
                "slot":row["slot"],
                "asset_sha256":row["asset_sha256"],
                "asset_bytes":row["bytes"],
                "width":row["width"],
                "height":row["height"],
                "asset_locator_status":"POD_LOCAL_HASH_ONLY",
            })
            private.append({
                "blind_id":blind_id,
                "model_id":model_id,
                "model_revision":revision,
                "job_id":row["job_id"],
                "source_blind_id":row["blind_id"],
                "asset_id":row["asset_id"],
                "asset_sha256":row["asset_sha256"],
                "character_id":row["character_id"],
                "style":row["style"],
                "slot":row["slot"],
            })

    if len({row["blind_id"] for row in public})!=8:
        raise ImageModelComparisonError("comparison blind IDs are not unique")
    public.sort(key=lambda row:row["blind_id"])
    private.sort(key=lambda row:row["blind_id"])
    public_packet={
        "schema_version":1,
        "comparison_id":COMPARISON_ID,
        "status":"AWAITING_BLIND_SCORES",
        "sample_count":8,
        "criteria":list(SCORE_SCHEMA.criteria),
        "blindness_note":"Process seal only: model identity is excluded from public packet but asset hashes also exist in private/canonical evidence.",
        "items":public,
        "selection_authorized":False,
        "production_acceptance":False,
    }
    if materialization_evidence is not None:
        if materialization_evidence.get("status")!="PASS_8_NEUTRAL_COPIES_VERIFIED":
            raise ImageModelComparisonError("neutral materialization evidence not PASS")
        if materialization_evidence.get("comparison_id")!=COMPARISON_ID or materialization_evidence.get("sample_count")!=8:
            raise ImageModelComparisonError("neutral materialization identity/population mismatch")
        manifest=materialization_evidence.get("manifest",{})
        if manifest.get("model_identity_in_manifest") is not False:
            raise ImageModelComparisonError("neutral materialization manifest leaks model identity")
        evidence_items={row.get("blind_id"):row for row in materialization_evidence.get("items",[])}
        if set(evidence_items)!={row["blind_id"] for row in public}:
            raise ImageModelComparisonError("neutral materialization item population mismatch")
        for row in public:
            ev=evidence_items[row["blind_id"]]
            if ev.get("asset_sha256")!=row["asset_sha256"] or ev.get("asset_bytes")!=row["asset_bytes"] or ev.get("verified") is not True:
                raise ImageModelComparisonError("neutral materialization asset identity mismatch")
            expected_path=f"/workspace/artifacts/blind-comparison/{row['blind_id']}.png"
            if ev.get("pod_neutral_path")!=expected_path:
                raise ImageModelComparisonError("neutral materialization path mismatch")
            row["asset_locator_status"]="POD_LOCAL_NEUTRAL_COPY_VERIFIED"
            row["pod_neutral_path"]=expected_path
        public_packet["neutral_materialization"]={
            "status":"PASS_8_VERIFIED_POD_LOCAL_NEUTRAL_COPIES",
            "manifest_pod_path":manifest.get("pod_path"),
            "manifest_sha256":manifest.get("sha256"),
            "manifest_bytes":manifest.get("bytes"),
            "model_identity_in_manifest":False,
        }
    return (
        public_packet,
        {
            "schema_version":1,
            "comparison_id":COMPARISON_ID,
            "mapping":private,
        },
    )


def score_template_csv(public_packet: dict[str,Any]) -> str:
    items=public_packet.get("items",[])
    out=StringIO()
    writer=csv.writer(out,lineterminator="\n")
    writer.writerow(["blind_id",*SCORE_SCHEMA.criteria,"failure_tags","notes"])
    for row in items:
        writer.writerow([row["blind_id"],*([""]*len(SCORE_SCHEMA.criteria)),"",""])
    return out.getvalue()


def rank_complete_scores(
    public_packet: dict[str,Any],
    private_packet: dict[str,Any],
    score_csv_text: str,
) -> list[dict[str,Any]]:
    rows=parse_score_csv(score_csv_text)
    validated=validate_complete_scores(public_packet["items"],rows,SCORE_SCHEMA)
    ranking=unblind_and_rank(
        validated,
        private_packet["mapping"],
        group_fields=("model_id",),
    )
    return ranking
