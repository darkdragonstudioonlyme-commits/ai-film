from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any


class RightsError(ValueError):
    pass


ALLOWED_RIGHTS_STATUS = {
    "ORIGINAL",
    "LICENSED",
    "CONSENTED",
    "PUBLIC_DOMAIN",
    "MODEL_LICENSE_CLEARED",
    "BLOCKED",
    "REVOKED",
    "UNKNOWN",
}


def validate_rights_record(record: dict[str, Any]) -> dict[str, Any]:
    required = {
        "rights_id",
        "subject_type",
        "subject_id",
        "status",
        "allowed_uses",
        "evidence_ref",
    }
    missing = sorted(required - set(record))
    if missing:
        raise RightsError(f"rights record missing fields: {missing}")
    if record["status"] not in ALLOWED_RIGHTS_STATUS:
        raise RightsError("invalid rights status")
    if not isinstance(record["allowed_uses"], list):
        raise RightsError("allowed_uses must be a list")
    out = deepcopy(record)
    out.setdefault("expires_on", None)
    out.setdefault("territories", ["GLOBAL"])
    out.setdefault("revoked", record["status"] == "REVOKED")
    return out


def _date_not_expired(expires_on: str | None, as_of: str) -> bool:
    if not expires_on:
        return True
    return date.fromisoformat(expires_on) >= date.fromisoformat(as_of)


def publication_gate(
    *,
    selected_assets: list[dict[str, Any]],
    rights_records: list[dict[str, Any]],
    creative_qc_pass: bool,
    technical_qc_pass: bool,
    provenance_complete: bool,
    distribution_rules_checked_on: str | None,
    as_of: str,
    required_subjects: list[dict[str, str]],
    owner_approved: bool = False,
) -> dict[str, Any]:
    blockers: list[str] = []
    normalized_rights = [validate_rights_record(r) for r in rights_records]
    by_subject = {(r["subject_type"], r["subject_id"]): r for r in normalized_rights}

    if not creative_qc_pass:
        blockers.append("creative-qc-not-pass")
    if not technical_qc_pass:
        blockers.append("technical-qc-not-pass")
    if not provenance_complete:
        blockers.append("provenance-incomplete")
    if not distribution_rules_checked_on:
        blockers.append("distribution-rules-not-checked")
    elif date.fromisoformat(distribution_rules_checked_on) > date.fromisoformat(as_of):
        blockers.append("distribution-rule-date-invalid")

    for asset in selected_assets:
        asset_id = asset.get("asset_id")
        if not asset_id:
            blockers.append("selected-asset-missing-id")
            continue
        if asset.get("revoked"):
            blockers.append(f"asset-revoked:{asset_id}")
        if not asset.get("publishable"):
            blockers.append(f"asset-not-publishable:{asset_id}")
        if not asset.get("content_sha256") or not asset.get("manifest_sha256"):
            blockers.append(f"asset-provenance-missing:{asset_id}")

    normalized_required: set[tuple[str, str]] = set()
    for subject in required_subjects:
        subject_type = subject.get("subject_type")
        subject_id = subject.get("subject_id")
        if not subject_type or not subject_id:
            raise RightsError("required rights subject missing type/id")
        normalized_required.add((subject_type, subject_id))
    for subject in sorted(normalized_required):
        record = by_subject.get(subject)
        label = f"{subject[0]}:{subject[1]}"
        if record is None:
            blockers.append(f"rights-missing:{label}")
            continue
        if record["status"] in {"BLOCKED", "REVOKED", "UNKNOWN"} or record.get("revoked"):
            blockers.append(f"rights-blocked:{label}:{record['status']}")
            continue
        if "COMMERCIAL_PUBLICATION" not in record["allowed_uses"]:
            blockers.append(f"rights-use-missing:{label}")
        if not _date_not_expired(record.get("expires_on"), as_of):
            blockers.append(f"rights-expired:{label}")

    if blockers:
        status = "BLOCKED"
    elif owner_approved:
        status = "AUTHORIZED_TO_PUBLISH"
    else:
        status = "READY_FOR_OWNER_APPROVAL"

    return {
        "schema_version": 1,
        "status": status,
        "blockers": blockers,
        "owner_approved": bool(owner_approved),
        "publish_action_performed": False,
    }
