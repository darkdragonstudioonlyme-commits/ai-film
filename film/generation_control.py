from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any


class GenerationControlError(ValueError):
    pass


ATTEMPT_TRANSITIONS = {
    "PENDING": {"SUBMITTED", "CANCELLED"},
    "SUBMITTED": {"RUNNING", "SUCCEEDED", "FAILED_RETRYABLE", "FAILED_FINAL", "UNKNOWN_OUTCOME", "CANCEL_REQUESTED"},
    "RUNNING": {"SUCCEEDED", "FAILED_RETRYABLE", "FAILED_FINAL", "UNKNOWN_OUTCOME", "CANCEL_REQUESTED"},
    "UNKNOWN_OUTCOME": {"SUCCEEDED", "FAILED_RETRYABLE", "FAILED_FINAL", "CANCELLED"},
    "CANCEL_REQUESTED": {"CANCELLED", "SUCCEEDED", "UNKNOWN_OUTCOME"},
    "SUCCEEDED": set(),
    "FAILED_RETRYABLE": set(),
    "FAILED_FINAL": set(),
    "CANCELLED": set(),
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def logical_generation_key(
    *,
    shot_spec: dict[str, Any],
    model_identity: dict[str, Any],
    compiled_prompt: dict[str, Any],
    reference_digests: list[str],
    seed_policy: dict[str, Any],
    workflow_config: dict[str, Any],
    creative_revision: int,
) -> str:
    payload = {
        "shot_spec": shot_spec,
        "model_identity": model_identity,
        "compiled_prompt": compiled_prompt,
        "reference_digests": sorted(reference_digests),
        "seed_policy": seed_policy,
        "workflow_config": workflow_config,
        "creative_revision": int(creative_revision),
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def new_logical_job(
    *,
    logical_key: str,
    max_attempts: int,
    cost_ceiling_usd: float,
) -> dict[str, Any]:
    if len(logical_key) != 64:
        raise GenerationControlError("invalid logical key")
    if int(max_attempts) < 1:
        raise GenerationControlError("max_attempts must be >=1")
    if float(cost_ceiling_usd) < 0:
        raise GenerationControlError("negative cost ceiling")
    return {
        "logical_key": logical_key,
        "max_attempts": int(max_attempts),
        "cost_ceiling_usd": float(cost_ceiling_usd),
        "attempt_count": 0,
        "cost_spent_usd": 0.0,
        "status": "READY",
        "cancelled": False,
        "result_asset_id": None,
        "applied_attempt_ids": [],
    }


def begin_attempt(job: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if job.get("cancelled"):
        raise GenerationControlError("job cancelled")
    if job.get("status") == "UNKNOWN_OUTCOME":
        raise GenerationControlError("must reconcile UNKNOWN_OUTCOME before retry")
    if job.get("status") == "SUCCEEDED":
        raise GenerationControlError("job already succeeded")
    if int(job.get("attempt_count", 0)) >= int(job.get("max_attempts", 0)):
        raise GenerationControlError("attempt ceiling reached")
    if float(job.get("cost_spent_usd", 0)) >= float(job.get("cost_ceiling_usd", 0)):
        raise GenerationControlError("cost ceiling reached")
    attempt_number = int(job.get("attempt_count", 0)) + 1
    attempt = {
        "attempt_id": f"{job['logical_key'][:16]}:{attempt_number}",
        "logical_key": job["logical_key"],
        "attempt_number": attempt_number,
        "state": "PENDING",
        "version": 1,
        "provider_request_id": None,
        "provider_submission_recorded": False,
        "cost_usd": 0.0,
        "result_asset_id": None,
    }
    updated = deepcopy(job)
    updated["attempt_count"] = attempt_number
    updated["status"] = "ATTEMPT_ACTIVE"
    return updated, attempt


def record_provider_submission(
    attempt: dict[str, Any],
    *,
    expected_version: int,
    provider_request_id: str,
) -> dict[str, Any]:
    if int(attempt.get("version", 0)) != int(expected_version):
        raise GenerationControlError("stale attempt version")
    if attempt.get("state") != "PENDING":
        raise GenerationControlError("provider submission can only be recorded from PENDING")
    if not provider_request_id:
        raise GenerationControlError("provider_request_id required")
    out = deepcopy(attempt)
    out["provider_request_id"] = provider_request_id
    out["provider_submission_recorded"] = True
    out["state"] = "SUBMITTED"
    out["version"] = int(attempt["version"]) + 1
    return out


def transition_attempt(
    attempt: dict[str, Any],
    *,
    expected_version: int,
    to_state: str,
    cost_usd: float | None = None,
    result_asset_id: str | None = None,
) -> dict[str, Any]:
    if int(attempt.get("version", 0)) != int(expected_version):
        raise GenerationControlError("stale attempt version")
    current = attempt.get("state")
    if to_state not in ATTEMPT_TRANSITIONS.get(current, set()):
        raise GenerationControlError(f"invalid attempt transition: {current}->{to_state}")
    if current in {"SUBMITTED", "RUNNING"} and not attempt.get("provider_submission_recorded"):
        raise GenerationControlError("provider submission identity missing")
    out = deepcopy(attempt)
    out["state"] = to_state
    out["version"] = int(attempt["version"]) + 1
    if cost_usd is not None:
        if float(cost_usd) < 0:
            raise GenerationControlError("negative attempt cost")
        out["cost_usd"] = float(cost_usd)
    if to_state == "SUCCEEDED":
        if not result_asset_id:
            raise GenerationControlError("successful attempt requires result asset")
        out["result_asset_id"] = result_asset_id
    return out


def apply_attempt_outcome(
    job: dict[str, Any],
    attempt: dict[str, Any],
) -> dict[str, Any]:
    if attempt.get("logical_key") != job.get("logical_key"):
        raise GenerationControlError("attempt belongs to different logical job")
    state = attempt.get("state")
    if state not in {"SUCCEEDED", "FAILED_RETRYABLE", "FAILED_FINAL", "UNKNOWN_OUTCOME", "CANCELLED"}:
        raise GenerationControlError("attempt is not terminal/reconcilable")
    attempt_id = attempt.get("attempt_id")
    if not attempt_id:
        raise GenerationControlError("attempt_id missing")
    if attempt_id in set(job.get("applied_attempt_ids", [])):
        raise GenerationControlError("attempt outcome already applied")
    new_total = float(job.get("cost_spent_usd", 0)) + float(attempt.get("cost_usd", 0))
    if new_total > float(job.get("cost_ceiling_usd", 0)) + 1e-9:
        raise GenerationControlError("attempt outcome exceeds cost ceiling")
    out = deepcopy(job)
    out["cost_spent_usd"] = round(new_total, 6)
    out.setdefault("applied_attempt_ids", []).append(attempt_id)
    if state == "SUCCEEDED":
        out["status"] = "SUCCEEDED"
        out["result_asset_id"] = attempt["result_asset_id"]
    elif state == "FAILED_RETRYABLE":
        out["status"] = "READY"
    elif state == "FAILED_FINAL":
        out["status"] = "FAILED_FINAL"
    elif state == "UNKNOWN_OUTCOME":
        out["status"] = "UNKNOWN_OUTCOME"
    elif state == "CANCELLED":
        out["status"] = "CANCELLED"
        out["cancelled"] = True
    return out


def request_cancel(job: dict[str, Any]) -> dict[str, Any]:
    if job.get("status") == "SUCCEEDED":
        raise GenerationControlError("cannot cancel succeeded job")
    out = deepcopy(job)
    out["cancelled"] = True
    if out.get("status") == "READY":
        out["status"] = "CANCELLED"
    return out

def reconcile_unknown_outcome(
    job: dict[str, Any],
    attempt: dict[str, Any],
    *,
    expected_attempt_version: int,
    resolved_state: str,
    provider_evidence: str,
    result_asset_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if job.get("status") != "UNKNOWN_OUTCOME":
        raise GenerationControlError("logical job is not awaiting UNKNOWN_OUTCOME reconciliation")
    if attempt.get("state") != "UNKNOWN_OUTCOME":
        raise GenerationControlError("attempt is not UNKNOWN_OUTCOME")
    if attempt.get("attempt_id") not in set(job.get("applied_attempt_ids", [])):
        raise GenerationControlError("unknown attempt outcome was not previously accounted")
    if not provider_evidence:
        raise GenerationControlError("provider reconciliation evidence required")
    if resolved_state not in {"SUCCEEDED", "FAILED_RETRYABLE", "FAILED_FINAL", "CANCELLED"}:
        raise GenerationControlError("invalid unknown-outcome resolution")
    resolved = transition_attempt(
        attempt,
        expected_version=expected_attempt_version,
        to_state=resolved_state,
        result_asset_id=result_asset_id,
    )
    updated = deepcopy(job)
    if resolved_state == "SUCCEEDED":
        updated["status"] = "SUCCEEDED"
        updated["result_asset_id"] = resolved["result_asset_id"]
    elif resolved_state == "FAILED_RETRYABLE":
        updated["status"] = "READY"
    elif resolved_state == "FAILED_FINAL":
        updated["status"] = "FAILED_FINAL"
    elif resolved_state == "CANCELLED":
        updated["status"] = "CANCELLED"
        updated["cancelled"] = True
    updated["last_reconciliation_evidence"] = provider_evidence
    return updated, resolved
