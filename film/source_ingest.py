from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from typing import Any


class SourceIngestError(ValueError):
    pass


SOURCE_KINDS = {"ORIGINAL_PROJECT", "LICENSED_ADAPTATION", "PUBLIC_DOMAIN"}
RIGHTS_BY_KIND = {
    "ORIGINAL_PROJECT": {"ORIGINAL"},
    "LICENSED_ADAPTATION": {"LICENSED", "CONSENTED"},
    "PUBLIC_DOMAIN": {"PUBLIC_DOMAIN"},
}

INSTRUCTION_PATTERNS = (
    re.compile(r"\b(ignore|disregard)\b.{0,40}\b(previous|above|system|developer)\b", re.I),
    re.compile(r"\b(run|execute|call|invoke)\b.{0,40}\b(tool|command|shell|api)\b", re.I),
    re.compile(r"\b(secret|password|token|credential)\b", re.I),
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_digest(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def normalize_source_packet(packet: dict[str, Any]) -> dict[str, Any]:
    required={"source_id","kind","title","source_text","rights","evidence"}
    missing=sorted(required-set(packet))
    if missing:
        raise SourceIngestError(f"source packet missing fields: {missing}")
    kind=packet["kind"]
    if kind not in SOURCE_KINDS:
        raise SourceIngestError("unsupported source kind")
    source_text=packet["source_text"]
    if not isinstance(source_text,str) or not source_text.strip():
        raise SourceIngestError("source_text must be non-empty text")
    rights=packet["rights"]
    if rights.get("status") not in RIGHTS_BY_KIND[kind]:
        raise SourceIngestError(f"rights status not valid for source kind: {kind}")
    if "COMMERCIAL_PUBLICATION" not in rights.get("allowed_uses",[]):
        raise SourceIngestError("source rights do not permit commercial publication")
    evidence=packet["evidence"]
    if not evidence.get("ref"):
        raise SourceIngestError("rights/source evidence ref required")
    evidence_sha=evidence.get("sha256")
    if not isinstance(evidence_sha,str) or len(evidence_sha)!=64 or any(c not in "0123456789abcdef" for c in evidence_sha):
        raise SourceIngestError("invalid evidence sha256")
    flags=[]
    for pattern in INSTRUCTION_PATTERNS:
        if pattern.search(source_text):
            flags.append(pattern.pattern)
    body={
        "schema_version":1,
        "source_id":packet["source_id"],
        "kind":kind,
        "title":packet["title"],
        "source_text":source_text,
        "source_text_sha256":sha256_text(source_text),
        "rights":deepcopy(rights),
        "evidence":deepcopy(evidence),
        "source_text_treatment":"INERT_DATA_NEVER_INSTRUCTIONS",
        "embedded_instruction_flags":flags,
        "tool_authority":False,
        "publish_authority":False,
    }
    body["packet_digest"]=canonical_digest(body)
    return body
