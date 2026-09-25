from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


class CastingIngestError(ValueError):
    pass


def _job_index(jobs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for job in jobs:
        job_id = job.get("job_id")
        if not job_id or job_id in result:
            raise CastingIngestError("invalid/duplicate casting job id")
        result[job_id] = job
    return result


def ingest_casting_outputs(
    contract: dict[str, Any],
    casting_jobs: list[dict[str, Any]],
    output_manifests: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if contract.get("status") not in {
        "CONTRACT_READY_REFERENCES_NOT_GENERATED",
        "PARTIAL_REFERENCES_GENERATED",
        "REFERENCES_GENERATED_AWAITING_SCORE",
    }:
        raise CastingIngestError("casting contract status cannot accept generated references")
    jobs = _job_index(casting_jobs)
    manifests_by_job: dict[str, dict[str, Any]] = {}
    for manifest in output_manifests:
        job_id = manifest.get("job_id")
        if job_id not in jobs:
            raise CastingIngestError(f"output references unknown job: {job_id}")
        if job_id in manifests_by_job:
            raise CastingIngestError(f"duplicate output manifest for job: {job_id}")
        job = jobs[job_id]
        exact = {
            "job_digest": job["job_digest"],
            "blind_id": job["blind_id"],
            "model_id": job["model_id"],
            "model_revision": job["model_revision"],
            "seed": job["seed"],
        }
        for key, expected in exact.items():
            if manifest.get(key) != expected:
                raise CastingIngestError(f"output identity mismatch {job_id}:{key}")
        for field in ("asset_sha256", "manifest_sha256"):
            value = manifest.get(field)
            if not isinstance(value, str) or len(value) != 64:
                raise CastingIngestError(f"invalid {field}: {job_id}")
        if not manifest.get("asset_id") or not manifest.get("asset_path"):
            raise CastingIngestError(f"missing asset identity/path: {job_id}")
        manifests_by_job[job_id] = manifest

    updated = deepcopy(contract)
    ref_index = {
        "schema_version": 1,
        "project_id": contract["project_id"],
        "status": "PARTIAL" if len(manifests_by_job) < len(jobs) else "COMPLETE",
        "assets": [],
    }
    blind_public = {
        "schema_version": 1,
        "status": "PARTIAL_ASSETS" if len(manifests_by_job) < len(jobs) else "ASSETS_BOUND_AWAITING_SCORE",
        "items": [],
    }

    # Slot contract carries the currently selected/accepted reference. During model eval,
    # multiple model outputs remain in reference_index and blind packet; no winner is selected here.
    for job in casting_jobs:
        manifest = manifests_by_job.get(job["job_id"])
        public = {
            "blind_id": job["blind_id"],
            "style": job["style"],
            "slot": job["slot"],
            "asset_id": None,
            "asset_sha256": None,
        }
        if manifest:
            public["asset_id"] = manifest["asset_id"]
            public["asset_sha256"] = manifest["asset_sha256"]
            ref_index["assets"].append({
                "asset_id": manifest["asset_id"],
                "asset_path": manifest["asset_path"],
                "asset_sha256": manifest["asset_sha256"],
                "manifest_sha256": manifest["manifest_sha256"],
                "job_id": job["job_id"],
                "job_digest": job["job_digest"],
                "blind_id": job["blind_id"],
                "character_id": job["character_id"],
                "style": job["style"],
                "slot": job["slot"],
                "model_id": job["model_id"],
                "model_revision": job["model_revision"],
                "seed": job["seed"],
            })
        blind_public["items"].append(public)

    generated = len(manifests_by_job)
    if generated == 0:
        updated["status"] = "CONTRACT_READY_REFERENCES_NOT_GENERATED"
    elif generated < len(jobs):
        updated["status"] = "PARTIAL_REFERENCES_GENERATED"
    else:
        updated["status"] = "REFERENCES_GENERATED_AWAITING_SCORE"
    updated["generated_reference_paths"] = sorted(
        row["asset_path"] for row in ref_index["assets"]
    )
    return updated, ref_index, blind_public
