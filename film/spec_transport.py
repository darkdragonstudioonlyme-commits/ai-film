from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from .production_package import ProductionPackageError, verify_production_spec_package


class SpecTransportError(ValueError):
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


def _ensure_clean_dir(path: Path) -> None:
    if path.exists():
        if path.is_symlink() or not path.is_dir():
            raise SpecTransportError("destination must be a real directory")
        if any(path.iterdir()):
            raise SpecTransportError("destination directory must be empty")
    else:
        path.mkdir(parents=True,exist_ok=False)


def export_spec_bundle(root: Path, package: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    verified=verify_production_spec_package(root,package)
    if verified["status"]!="PASS":
        raise SpecTransportError("source production package failed verification")
    _ensure_clean_dir(out_dir)
    payload=out_dir/"payload"
    payload.mkdir()
    entries=[]
    for entry in package["entries"]:
        rel=Path(entry["path"])
        src=root/rel
        dst=payload/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dst)
        entries.append({
            "path":entry["path"],
            "sha256":entry["sha256"],
            "bytes":entry["bytes"],
        })
    body={
        "schema_version":1,
        "status":"EXPORTED_SPEC_ONLY",
        "project_id":package["project_id"],
        "package_digest":package["package_digest"],
        "entries":entries,
        "entry_count":len(entries),
        "execution_authority":False,
        "publish_authority":False,
    }
    body["bundle_digest"]=canonical_digest(body)
    (out_dir/"BUNDLE_MANIFEST.json").write_text(
        json.dumps(body,ensure_ascii=False,indent=2,sort_keys=True)+"\n",
        encoding="utf-8",
    )
    return body


def verify_spec_bundle(bundle_dir: Path) -> dict[str, Any]:
    if bundle_dir.is_symlink() or not bundle_dir.is_dir():
        raise SpecTransportError("bundle_dir must be real directory")
    manifest_path=bundle_dir/"BUNDLE_MANIFEST.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise SpecTransportError("bundle manifest missing or symlinked")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    body={k:v for k,v in manifest.items() if k!="bundle_digest"}
    if manifest.get("bundle_digest")!=canonical_digest(body):
        raise SpecTransportError("bundle digest mismatch")
    if manifest.get("execution_authority") is not False or manifest.get("publish_authority") is not False:
        raise SpecTransportError("bundle authority must be false")
    entries=manifest.get("entries",[])
    if len(entries)!=manifest.get("entry_count"):
        raise SpecTransportError("bundle entry count mismatch")

    expected={"BUNDLE_MANIFEST.json"}
    mismatches=[]
    for entry in entries:
        rel=Path(entry["path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise SpecTransportError(f"unsafe bundle path: {entry['path']}")
        if set(rel.parts) & FORBIDDEN_PARTS:
            raise SpecTransportError(f"forbidden bundle path: {entry['path']}")
        if rel.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise SpecTransportError(f"generated/binary payload rejected: {entry['path']}")
        bundle_rel=(Path("payload")/rel).as_posix()
        expected.add(bundle_rel)
        path=bundle_dir/bundle_rel
        if path.is_symlink():
            raise SpecTransportError(f"symlink payload rejected: {entry['path']}")
        if not path.is_file():
            mismatches.append({"path":entry["path"],"reason":"MISSING"})
            continue
        if file_sha256(path)!=entry["sha256"] or path.stat().st_size!=int(entry["bytes"]):
            mismatches.append({"path":entry["path"],"reason":"IDENTITY_MISMATCH"})

    actual=set()
    for path in bundle_dir.rglob("*"):
        if path.is_symlink():
            raise SpecTransportError(f"symlink in bundle rejected: {path.relative_to(bundle_dir)}")
        if path.is_file():
            actual.add(path.relative_to(bundle_dir).as_posix())
    extras=sorted(actual-expected)
    missing_files=sorted(expected-actual)
    if extras:
        mismatches.extend({"path":p,"reason":"EXTRA_FILE"} for p in extras)
    if missing_files:
        mismatches.extend({"path":p,"reason":"MISSING_FILE"} for p in missing_files)
    return {
        "schema_version":1,
        "status":"PASS" if not mismatches else "FAIL",
        "mismatches":mismatches,
        "project_id":manifest.get("project_id"),
        "package_digest":manifest.get("package_digest"),
        "bundle_digest":manifest.get("bundle_digest"),
    }


def import_spec_bundle(bundle_dir: Path, dest_root: Path) -> dict[str, Any]:
    verified=verify_spec_bundle(bundle_dir)
    if verified["status"]!="PASS":
        raise SpecTransportError("bundle verification failed")
    _ensure_clean_dir(dest_root)
    manifest=json.loads((bundle_dir/"BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    copied=[]
    try:
        for entry in manifest["entries"]:
            rel=Path(entry["path"])
            src=bundle_dir/"payload"/rel
            dst=dest_root/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(src,dst)
            copied.append(entry["path"])
    except Exception:
        shutil.rmtree(dest_root,ignore_errors=True)
        raise
    return {
        "schema_version":1,
        "status":"IMPORTED_SPEC_ONLY",
        "project_id":manifest["project_id"],
        "copied_files":copied,
        "entry_count":len(copied),
        "execution_authority":False,
        "publish_authority":False,
    }
