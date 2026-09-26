from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BatchOrchestratorError(ValueError):
    pass


@dataclass(frozen=True)
class Adapter:
    runner: str
    id_arg: str
    pass_statuses: tuple[str, ...]


ADAPTERS = {
    "flux2-klein-live": Adapter("tools/run_flux2_klein_live.py", "--job-id", ("PASS_RUNTIME",)),
    "z-image-live": Adapter("tools/run_z_image_live.py", "--job-id", ("PASS_RUNTIME",)),
    "voxcpm2-live": Adapter("tools/run_voxcpm2_live.py", "--request-id", ("PASS_RUNTIME",)),
    "wan22-ti2v-live": Adapter("tools/run_wan22_ti2v_live.py", "--smoke-id", ("PASS_RUNTIME_SMOKE",)),
    "image-keyframe-live": Adapter("tools/run_image_keyframe_live.py", "--probe-job-id", ("PASS_RUNTIME",)),
}


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def validate_config(config: dict[str,Any]) -> list[dict[str,Any]]:
    if config.get("schema_version")!=1:
        raise BatchOrchestratorError("unsupported batch schema")
    if not isinstance(config.get("batch_id"),str) or not config["batch_id"].strip():
        raise BatchOrchestratorError("batch_id required")
    jobs=config.get("jobs")
    if not isinstance(jobs,list) or not jobs:
        raise BatchOrchestratorError("jobs required")
    ids=[]
    for job in jobs:
        for field in ("job_id","adapter","work_id","receipt_path"):
            if not isinstance(job.get(field),str) or not job[field].strip():
                raise BatchOrchestratorError(f"job missing {field}")
        if job["adapter"] not in ADAPTERS:
            raise BatchOrchestratorError(f"unknown adapter: {job['adapter']}")
        timeout=float(job.get("max_runtime_sec",900.0))
        if timeout<=0 or timeout>7200:
            raise BatchOrchestratorError("invalid max_runtime_sec")
        ids.append(job["job_id"])
    if len(ids)!=len(set(ids)):
        raise BatchOrchestratorError("duplicate job_id")
    return jobs


def build_argv(job: dict[str,Any], *, root: Path, execute: bool) -> list[str]:
    adapter=ADAPTERS[job["adapter"]]
    argv=[sys.executable,str(root/adapter.runner),adapter.id_arg,job["work_id"],
          "--max-runtime-sec",str(float(job.get("max_runtime_sec",900.0)))]
    if job.get("model_dir"):
        argv += ["--model-dir",str(job["model_dir"])]
    if job.get("out_root"):
        argv += ["--out-root",str(job["out_root"])]
    if job.get("code_dir"):
        argv += ["--wan-repo-dir",str(job["code_dir"])]
    if job.get("reference_image"):
        argv += ["--reference-image",str(job["reference_image"])]
    if execute:
        argv.append("--execute")
    return argv


def _receipt(path: Path) -> dict[str,Any] | None:
    if not path.is_file():
        return None
    try:
        value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError):
        return None
    return value if isinstance(value,dict) else None


def plan_batch(config: dict[str,Any], *, root: Path) -> dict[str,Any]:
    jobs=validate_config(config)
    planned=[]
    for job in jobs:
        adapter=ADAPTERS[job["adapter"]]
        receipt_path=Path(job["receipt_path"])
        receipt=_receipt(receipt_path)
        passed=bool(receipt and receipt.get("status") in adapter.pass_statuses)
        action="SKIP_EXISTING_PASS" if passed and job.get("skip_if_pass",True) else "RUN"
        planned.append({
            "job_id":job["job_id"],"adapter":job["adapter"],"work_id":job["work_id"],
            "action":action,"receipt_path":str(receipt_path),
            "argv":build_argv(job,root=root,execute=True),
        })
    return {
        "schema_version":1,"batch_id":config["batch_id"],"status":"PLANNED",
        "job_count":len(planned),"jobs":planned,
        "new_resource_creation_authorized":False,"publish_authority":False,
    }


def run_batch(config: dict[str,Any], *, root: Path, batch_root: Path, execute: bool) -> dict[str,Any]:
    plan=plan_batch(config,root=root)
    if not execute:
        return plan
    out_dir=batch_root/config["batch_id"]
    out_dir.mkdir(parents=True,exist_ok=True)
    results=[]
    for planned,job in zip(plan["jobs"],config["jobs"]):
        receipt_path=Path(job["receipt_path"])
        if planned["action"]=="SKIP_EXISTING_PASS":
            receipt=_receipt(receipt_path) or {}
            results.append({"job_id":job["job_id"],"status":"SKIPPED_EXISTING_PASS",
                            "receipt_path":str(receipt_path),"receipt_sha256":_sha256(receipt_path)})
            continue
        argv=build_argv(job,root=root,execute=True)
        completed=subprocess.run(argv,cwd=root,text=True,capture_output=True,
                                 timeout=float(job.get("max_runtime_sec",900.0))+60.0,check=False)
        (out_dir/f"{job['job_id']}.stdout.log").write_text(completed.stdout,encoding="utf-8")
        (out_dir/f"{job['job_id']}.stderr.log").write_text(completed.stderr,encoding="utf-8")
        receipt=_receipt(receipt_path)
        adapter=ADAPTERS[job["adapter"]]
        ok=completed.returncode==0 and receipt and receipt.get("status") in adapter.pass_statuses
        results.append({"job_id":job["job_id"],"status":"PASS" if ok else "FAILED",
                        "returncode":completed.returncode,"receipt_path":str(receipt_path),
                        "receipt_sha256":_sha256(receipt_path) if receipt_path.is_file() else None})
        if not ok and config.get("stop_on_failure",True):
            break
    success=len(results)==len(config["jobs"]) and all(r["status"] in {"PASS","SKIPPED_EXISTING_PASS"} for r in results)
    summary={
        "schema_version":1,"batch_id":config["batch_id"],
        "status":"PASS" if success else "FAILED","job_count":len(config["jobs"]),
        "completed_count":len(results),"results":results,
        "new_resource_creation_authorized":False,"publish_authority":False,
    }
    (out_dir/"batch_receipt.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return summary
