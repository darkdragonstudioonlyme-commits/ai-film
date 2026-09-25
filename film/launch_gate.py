from __future__ import annotations

import hashlib
import json
from typing import Any


class LaunchGateError(ValueError):
    pass


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def make_rate_snapshot(provider: str, rates: dict[str, float], observed_at: str, source_url: str) -> dict[str, Any]:
    if not provider or not observed_at or not source_url:
        raise LaunchGateError("rate snapshot missing identity")
    if not rates or any(float(v) <= 0 for v in rates.values()):
        raise LaunchGateError("invalid rate snapshot")
    payload = {
        "schema_version": 1,
        "provider": provider,
        "observed_at": observed_at,
        "source_url": source_url,
        "rates_usd_per_hour": {k: float(v) for k, v in sorted(rates.items())},
    }
    payload["snapshot_digest"] = digest(payload)
    return payload


def validate_launch_authorization(
    receipt: dict[str, Any],
    *,
    proposal_digest: str,
    rate_snapshot: dict[str, Any],
    requested_gpu: str,
    requested_max_usd: float,
) -> dict[str, Any]:
    required = {
        "schema_version","authorization_id","status","authorized_by",
        "authorized_at","expires_at","proposal_digest","rate_snapshot_digest",
        "provider","allowed_gpus","max_total_usd","scope","receipt_digest",
    }
    missing = sorted(required - set(receipt))
    if missing:
        raise LaunchGateError(f"authorization receipt missing fields: {missing}")
    body = {k:v for k,v in receipt.items() if k!="receipt_digest"}
    if receipt["receipt_digest"] != digest(body):
        raise LaunchGateError("authorization receipt digest mismatch")
    if receipt["status"] != "AUTHORIZED":
        raise LaunchGateError("paid launch is not explicitly authorized")
    if receipt["proposal_digest"] != proposal_digest:
        raise LaunchGateError("proposal digest mismatch")
    if receipt["rate_snapshot_digest"] != rate_snapshot.get("snapshot_digest"):
        raise LaunchGateError("rate snapshot digest mismatch")
    if receipt["provider"] != rate_snapshot.get("provider"):
        raise LaunchGateError("provider mismatch")
    if requested_gpu not in set(receipt["allowed_gpus"]):
        raise LaunchGateError("GPU not authorized")
    if float(requested_max_usd) > float(receipt["max_total_usd"]):
        raise LaunchGateError("requested budget exceeds authorization")
    live_rate = rate_snapshot.get("rates_usd_per_hour",{}).get(requested_gpu)
    if live_rate is None:
        raise LaunchGateError("requested GPU missing from live rate snapshot")
    return {
        "authorization_id": receipt["authorization_id"],
        "provider": receipt["provider"],
        "gpu": requested_gpu,
        "max_total_usd": float(receipt["max_total_usd"]),
        "requested_max_usd": float(requested_max_usd),
        "rate_usd_per_hour": float(live_rate),
        "scope": receipt["scope"],
        "launch_permitted": True,
    }


def make_unauthorized_placeholder(proposal_digest: str, rate_snapshot_digest: str) -> dict[str, Any]:
    body = {
        "schema_version": 1,
        "authorization_id": "NOT_AUTHORIZED",
        "status": "NOT_AUTHORIZED",
        "authorized_by": None,
        "authorized_at": None,
        "expires_at": None,
        "proposal_digest": proposal_digest,
        "rate_snapshot_digest": rate_snapshot_digest,
        "provider": "RunPod",
        "allowed_gpus": [],
        "max_total_usd": 0.0,
        "scope": "NO_PAID_LAUNCH_AUTHORITY",
    }
    return {**body, "receipt_digest": digest(body)}
