from __future__ import annotations

from copy import deepcopy
from typing import Any

from .admission import evaluate_admission


class QueueControlError(ValueError):
    pass


def new_queue(*, max_depth: int, per_project_concurrency: int) -> dict[str, Any]:
    if max_depth < 1 or per_project_concurrency < 1:
        raise QueueControlError("queue limits must be positive")
    return {
        "schema_version": 1,
        "max_depth": int(max_depth),
        "per_project_concurrency": int(per_project_concurrency),
        "next_sequence": 1,
        "jobs": [],
    }


def enqueue_job(
    state: dict[str, Any],
    *,
    job_id: str,
    project_id: str,
    admission_profile_id: str,
) -> dict[str, Any]:
    if not job_id or not project_id or not admission_profile_id:
        raise QueueControlError("job/project/profile identity required")
    if any(row.get("job_id") == job_id for row in state.get("jobs", [])):
        raise QueueControlError("duplicate job_id")
    queued = [row for row in state.get("jobs", []) if row.get("state") == "QUEUED"]
    if len(queued) >= int(state["max_depth"]):
        raise QueueControlError("QUEUE_BACKPRESSURE_MAX_DEPTH")
    out = deepcopy(state)
    seq = int(out["next_sequence"])
    out["next_sequence"] = seq + 1
    out["jobs"].append({
        "job_id": job_id,
        "project_id": project_id,
        "admission_profile_id": admission_profile_id,
        "sequence": seq,
        "state": "QUEUED",
        "cancel_requested": False,
        "dispatch_worker_id": None,
    })
    return out


def cancel_job(state: dict[str, Any], job_id: str) -> dict[str, Any]:
    out = deepcopy(state)
    for row in out.get("jobs", []):
        if row.get("job_id") != job_id:
            continue
        if row["state"] == "QUEUED":
            row["state"] = "CANCELLED"
            row["cancel_requested"] = True
            return out
        if row["state"] == "DISPATCHED":
            row["cancel_requested"] = True
            return out
        raise QueueControlError(f"cannot cancel job in state {row['state']}")
    raise QueueControlError("unknown job_id")


def dispatch_next(
    state: dict[str, Any],
    *,
    worker: dict[str, Any],
    admission_profiles: dict[str, dict[str, Any]],
    active_by_project: dict[str, int],
) -> tuple[dict[str, Any], dict[str, Any] | None, list[dict[str, Any]]]:
    out = deepcopy(state)
    blocked: list[dict[str, Any]] = []
    ordered = sorted(
        (row for row in out.get("jobs", []) if row.get("state") == "QUEUED"),
        key=lambda row: int(row["sequence"]),
    )
    for row in ordered:
        project_id = row["project_id"]
        if int(active_by_project.get(project_id, 0)) >= int(out["per_project_concurrency"]):
            blocked.append({
                "job_id": row["job_id"],
                "reason": "PROJECT_CONCURRENCY_LIMIT",
            })
            continue
        profile = admission_profiles.get(row["admission_profile_id"])
        if profile is None:
            blocked.append({
                "job_id": row["job_id"],
                "reason": "UNKNOWN_ADMISSION_PROFILE",
            })
            continue
        decision = evaluate_admission(profile, worker)
        if not decision["admitted"]:
            blocked.append({
                "job_id": row["job_id"],
                "reason": "ADMISSION_REJECTED",
                "details": decision["reasons"],
            })
            continue
        target = next(x for x in out["jobs"] if x["job_id"] == row["job_id"])
        target["state"] = "DISPATCHED"
        target["dispatch_worker_id"] = worker["worker_id"]
        return out, deepcopy(target), blocked
    return out, None, blocked


def queue_status(state: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in state.get("jobs", []):
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    return {
        "schema_version": 1,
        "max_depth": state["max_depth"],
        "per_project_concurrency": state["per_project_concurrency"],
        "counts": counts,
        "queued_job_ids": [
            row["job_id"]
            for row in sorted(state.get("jobs", []), key=lambda r: int(r["sequence"]))
            if row["state"] == "QUEUED"
        ],
    }
