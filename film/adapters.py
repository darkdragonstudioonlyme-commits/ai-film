from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class AdapterError(ValueError):
    pass


BACKENDS = {
    "z-image": {"backend":"diffusers","pipeline":"ZImagePipeline"},
    "flux2-klein-4b": {"backend":"diffusers","pipeline":"Flux2KleinPipeline"},
    "wan22-ti2v-5b": {"backend":"wan2.2","pipeline":"TI2V-5B"},
    "wan22-i2v-14b": {"backend":"wan2.2","pipeline":"I2V-A14B"},
    "ltx-2.5": {"backend":"ltx-2.x","pipeline":"LTX-2.5"},
}


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_digest(value: Any) -> str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _model_index(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["model_id"]:row for row in matrix.get("models",[])}


def compile_backend_request(
    job: dict[str, Any],
    matrix: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    model_id=job.get("model",{}).get("model_id")
    models=_model_index(matrix)
    if model_id not in models:
        raise AdapterError(f"unknown model: {model_id}")
    model=models[model_id]
    if not model.get("enabled"):
        raise AdapterError(f"model disabled by evaluation/commercial gate: {model_id}")
    if model.get("pin_status")!="PINNED":
        raise AdapterError(f"model is not exactly pinned: {model_id}")
    if model_id not in BACKENDS:
        raise AdapterError(f"adapter not implemented: {model_id}")

    prompt_rel=job.get("prompt_source")
    if not isinstance(prompt_rel,str) or not prompt_rel:
        raise AdapterError("missing prompt_source")
    prompt_path=(root/prompt_rel).resolve()
    try:
        prompt_path.relative_to(root.resolve())
    except ValueError:
        raise AdapterError("prompt_source escapes repository root")
    if not prompt_path.is_file():
        raise AdapterError(f"prompt source not found: {prompt_rel}")
    expected_hash=job.get("prompt_sha256")
    actual_hash=file_sha256(prompt_path)
    if expected_hash != actual_hash:
        raise AdapterError("prompt source digest mismatch")

    compiled=json.loads(prompt_path.read_text(encoding="utf-8"))
    if compiled.get("shot_id") != job.get("shot_id"):
        raise AdapterError("compiled prompt shot identity mismatch")

    requirements=list(job.get("requirements") or [])
    refs=dict(job.get("resolved_references") or {})
    missing=[name for name in requirements if not refs.get(name)]
    missing=sorted(set(missing + list(job.get("blocked_requirements") or [])))
    if missing:
        raise AdapterError("missing requirements: "+",".join(missing))

    resolution=job.get("resolution") or {}
    width=int(resolution.get("width",0))
    height=int(resolution.get("height",0))
    if width<=0 or height<=0:
        raise AdapterError("invalid resolution")

    request={
        "schema_version":1,
        "adapter_version":"film-adapter-v1",
        "benchmark_id":job["benchmark_id"],
        "job_id":job["job_id"],
        "job_digest":job["job_digest"],
        "model":{
            "model_id":model_id,
            "source_repo":model["source_repo"],
            "source_revision":model["source_revision"],
            "backend":BACKENDS[model_id]["backend"],
            "pipeline":BACKENDS[model_id]["pipeline"],
            "license_gate":model["license_gate"],
            "production_gate":model.get("production_gate"),
        },
        "shot_id":job["shot_id"],
        "style":job["style"],
        "aspect":job["aspect"],
        "width":width,
        "height":height,
        "seed":int(job["seed"]),
        "prompt":compiled["prompt"],
        "negative_prompt":compiled.get("negative_prompt",""),
        "prompt_source":prompt_rel,
        "prompt_sha256":actual_hash,
        "references":refs,
        "execution_permitted":bool(model.get("execution_ready",False)),
    }
    request["request_digest"]=canonical_digest(request)
    return request
