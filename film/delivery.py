from __future__ import annotations

from typing import Any


class DeliveryError(ValueError):
    pass


def expected_variants() -> list[dict[str, str]]:
    return [
        {"aspect": aspect, "language": language}
        for aspect in ("9:16", "16:9")
        for language in ("en", "zh-CN", "vi")
    ]


def build_delivery_manifest(
    deliverables: list[dict[str, Any]],
    *,
    publication_gate_status: str,
    creative_qc_ref: str,
    rights_gate_ref: str,
) -> dict[str, Any]:
    if not creative_qc_ref or not rights_gate_ref:
        raise DeliveryError("creative_qc_ref and rights_gate_ref are required")
    expected = {(x["aspect"], x["language"]) for x in expected_variants()}
    by_variant: dict[tuple[str, str], dict[str, Any]] = {}
    blockers: list[str] = []

    for row in deliverables:
        key = (row.get("aspect"), row.get("language"))
        if key not in expected:
            raise DeliveryError(f"unexpected delivery variant: {key}")
        if key in by_variant:
            raise DeliveryError(f"duplicate delivery variant: {key}")
        by_variant[key] = row

    missing = sorted(expected - set(by_variant))
    for aspect, language in missing:
        blockers.append(f"missing-variant:{aspect}:{language}")

    for key, row in sorted(by_variant.items()):
        label = f"{key[0]}:{key[1]}"
        if row.get("technical_qc_status") != "PASS":
            blockers.append(f"technical-qc-not-pass:{label}")
        for field in ("media_asset_id", "media_sha256", "media_manifest_sha256", "subtitle_path", "subtitle_sha256", "technical_qc_id"):
            if not row.get(field):
                blockers.append(f"missing-field:{label}:{field}")
        for field in ("media_sha256", "media_manifest_sha256", "subtitle_sha256"):
            value = row.get(field)
            if value and (len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
                blockers.append(f"invalid-sha:{label}:{field}")

    package_complete = not blockers
    if not package_complete:
        status = "INCOMPLETE"
    elif publication_gate_status == "BLOCKED":
        status = "PACKAGE_COMPLETE_PUBLICATION_BLOCKED"
    elif publication_gate_status == "READY_FOR_OWNER_APPROVAL":
        status = "PACKAGE_READY_FOR_OWNER_APPROVAL"
    elif publication_gate_status == "AUTHORIZED_TO_PUBLISH":
        status = "PACKAGE_AUTHORIZED_NOT_PUBLISHED"
    else:
        raise DeliveryError("invalid publication gate status")

    return {
        "schema_version": 1,
        "status": status,
        "expected_variants": expected_variants(),
        "deliverables": [by_variant[k] for k in sorted(by_variant)],
        "blockers": blockers,
        "creative_qc_ref": creative_qc_ref,
        "rights_gate_ref": rights_gate_ref,
        "publication_gate_status": publication_gate_status,
        "published": False,
        "publish_action_performed": False,
    }
