from __future__ import annotations

from copy import deepcopy
from typing import Any


class SchemaCompatibilityError(ValueError):
    pass


CURRENT_VERSION=1
LEGACY_ZERO_TYPES={"project","casting","continuity","shots"}


def detect_schema_version(document_type: str, value: Any) -> int:
    if document_type=="shots":
        if isinstance(value,list):
            return 0
        if isinstance(value,dict) and isinstance(value.get("schema_version"),int):
            return int(value["schema_version"])
        raise SchemaCompatibilityError("unrecognized shots schema")
    if not isinstance(value,dict):
        raise SchemaCompatibilityError(f"{document_type} must be mapping")
    version=value.get("schema_version")
    if version is None:
        if document_type in LEGACY_ZERO_TYPES:
            return 0
        raise SchemaCompatibilityError(f"{document_type} missing schema_version")
    if not isinstance(version,int):
        raise SchemaCompatibilityError(f"{document_type} invalid schema_version")
    return version


def plan_schema_compatibility(documents: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows=[]
    unsupported=[]
    upgrades=[]
    for name in sorted(documents):
        item=documents[name]
        doc_type=item["document_type"]
        version=detect_schema_version(doc_type,item["value"])
        if version==CURRENT_VERSION:
            status="COMPATIBLE"
            strategy=None
        elif version==0 and doc_type in LEGACY_ZERO_TYPES:
            status="UPGRADE_REQUIRED"
            strategy="WRAP_OR_ADD_SCHEMA_VERSION_1"
            upgrades.append(name)
        else:
            status="UNSUPPORTED"
            strategy=None
            unsupported.append(name)
        rows.append({
            "name":name,
            "document_type":doc_type,
            "detected_version":version,
            "target_version":CURRENT_VERSION,
            "status":status,
            "upgrade_strategy":strategy,
            "apply_authorized":False,
        })
    overall="UNSUPPORTED" if unsupported else ("UPGRADE_REQUIRED" if upgrades else "COMPATIBLE")
    return {
        "schema_version":1,
        "status":overall,
        "documents":rows,
        "upgrade_required":upgrades,
        "unsupported":unsupported,
        "mutations_applied":False,
    }


def apply_upgrade_plan(value: Any, *, document_type: str, from_version: int, authorized: bool=False) -> Any:
    if not authorized:
        raise SchemaCompatibilityError("schema upgrade is dry-run unless explicitly authorized")
    if from_version!=0 or document_type not in LEGACY_ZERO_TYPES:
        raise SchemaCompatibilityError("unsupported upgrade path")
    if document_type=="shots":
        if not isinstance(value,list):
            raise SchemaCompatibilityError("legacy shots must be list")
        return {"schema_version":1,"shots":deepcopy(value)}
    if not isinstance(value,dict):
        raise SchemaCompatibilityError("legacy document must be mapping")
    out=deepcopy(value)
    out["schema_version"]=1
    return out
