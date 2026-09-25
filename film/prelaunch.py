from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

VISUAL_STAGES = {"image", "video"}


def canonical_digest(value: Any) -> str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def build_prelaunch_bundle(root: Path) -> dict[str, Any]:
    matrix_path=root/"model-evaluations/slice01/model_matrix.json"
    runtime_path=root/"model-evaluations/slice01/gpu-worker/runtime_lock.json"
    req_path=root/"model-evaluations/slice01/gpu-worker/requirements-base.lock.txt"
    matrix=json.loads(matrix_path.read_text(encoding="utf-8"))
    runtime=json.loads(runtime_path.read_text(encoding="utf-8"))
    rows=[]
    for model in sorted(matrix["models"],key=lambda m:m["model_id"]):
        if not model.get("enabled") or model.get("stage") not in VISUAL_STAGES:
            continue
        if model.get("pin_status")!="PINNED":
            raise ValueError(f"enabled visual model is not pinned: {model['model_id']}")
        if model.get("execution_ready"):
            raise ValueError(f"prelaunch builder refuses execution-ready model: {model['model_id']}")
        repo=model["source_repo"]
        revision=model["source_revision"]
        model_dir=f"/opt/aifilm/models/{model['model_id']}"
        row={
            "schema_version":1,
            "model_id":model["model_id"],
            "stage":model["stage"],
            "source_repo":repo,
            "source_revision":revision,
            "checkpoint":model["checkpoint"],
            "license_gate":model["license_gate"],
            "production_gate":model.get("production_gate"),
            "runner_profile":model["runner_profile"],
            "requirements":list(model.get("requires",[])),
            "execution_ready":False,
            "install_plan":[
                {
                    "kind":"weights",
                    "command":[
                        "/opt/aifilm/venv/bin/hf","download",repo,
                        "--revision",revision,
                        "--local-dir",model_dir,
                    ],
                },
            ],
            "preflight":[
                "nvidia-smi",
                f"test -d {model_dir}",
                f"test -n \"$(find {model_dir} -type f -print -quit)\"",
            ],
            "runner_contract":{
                "input":"backend_request.json",
                "output_dir":"artifacts/",
                "must_preserve":["job_id","job_digest","model.source_revision","prompt_sha256","seed","references"],
                "no_publish":True,
                "paid_authority_inherited":False,
            },
        }
        row["bundle_digest"]=canonical_digest(row)
        rows.append(row)
    if not rows:
        raise ValueError("no enabled visual models")
    return {
        "schema_version":1,
        "mode":"PRELAUNCH_DRY_RUN_ONLY",
        "execution_ready":False,
        "provider_resource_created":False,
        "base_runtime":{
            "runtime_lock_sha256":file_sha256(runtime_path),
            "requirements_lock_sha256":file_sha256(req_path),
            "packages":runtime["packages"],
            "cuda":runtime["target"]["cuda"],
        },
        "models":rows,
    }
