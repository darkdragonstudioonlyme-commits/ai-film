from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


class ProductionPackageError(ValueError):
    pass


FORBIDDEN_PARTS={"runtime","compiled","delivery","artifacts","run-evidence","secrets","credentials"}
FORBIDDEN_SUFFIXES={".png",".jpg",".jpeg",".webp",".mp4",".mov",".mkv",".wav",".flac",".bin"}


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_digest(value: Any) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_relpath(rel: str) -> PurePosixPath:
    p=PurePosixPath(rel)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ProductionPackageError(f"unsafe package path: {rel}")
    if set(p.parts) & FORBIDDEN_PARTS:
        raise ProductionPackageError(f"forbidden package path: {rel}")
    if p.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise ProductionPackageError(f"generated/binary media not allowed: {rel}")
    return p


def build_production_spec_package(root: Path, relpaths: list[str], *, project_id: str) -> dict[str, Any]:
    if not relpaths:
        raise ProductionPackageError("empty package")
    seen=set()
    entries=[]
    for rel in sorted(relpaths):
        p=_validate_relpath(rel)
        normalized=p.as_posix()
        if normalized in seen:
            raise ProductionPackageError(f"duplicate package path: {normalized}")
        seen.add(normalized)
        full=(root/p).resolve()
        try:
            full.relative_to(root.resolve())
        except ValueError as exc:
            raise ProductionPackageError(f"path escapes root: {rel}") from exc
        if not full.is_file():
            raise ProductionPackageError(f"package input missing: {rel}")
        entries.append({
            "path":normalized,
            "sha256":file_sha256(full),
            "bytes":full.stat().st_size,
        })
    body={
        "schema_version":1,
        "project_id":project_id,
        "status":"SPEC_ONLY_NO_GENERATED_MEDIA",
        "entries":entries,
        "entry_count":len(entries),
        "contains_generated_media":False,
        "contains_runtime_receipts":False,
        "contains_secrets":False,
        "execution_authority":False,
        "publish_authority":False,
    }
    body["package_digest"]=canonical_digest(body)
    return body


def verify_production_spec_package(root: Path, package: dict[str, Any]) -> dict[str, Any]:
    body={k:v for k,v in package.items() if k!="package_digest"}
    if package.get("package_digest")!=canonical_digest(body):
        raise ProductionPackageError("package digest mismatch")
    mismatches=[]
    for entry in package.get("entries",[]):
        p=_validate_relpath(entry["path"])
        full=(root/p)
        if not full.is_file():
            mismatches.append({"path":entry["path"],"reason":"MISSING"})
            continue
        actual=file_sha256(full)
        if actual!=entry["sha256"] or full.stat().st_size!=int(entry["bytes"]):
            mismatches.append({"path":entry["path"],"reason":"IDENTITY_MISMATCH"})
    return {"schema_version":1,"status":"PASS" if not mismatches else "FAIL","mismatches":mismatches}
