#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shlex,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load():
    return json.loads((ROOT/"model-evaluations/auto-eval/vbench_runtime_lock.json").read_text(encoding="utf-8"))

def build_commands(lock: dict)->list[list[str]]:
    venv=lock["venv"]
    py=f"{venv}/bin/python"
    pip=f"{venv}/bin/pip"
    return [
        ["python3.11","-m","venv",venv],
        [pip,"install","-U","pip","setuptools","wheel"],
        [pip,"install",f"torch=={lock['torch']}",f"torchvision=={lock['torchvision']}","--index-url",lock["torch_index_url"]],
        ["git","clone","https://github.com/Vchitect/VBench.git",lock["code_dir"]],
        ["git","-C",lock["code_dir"],"checkout","--detach",lock["code_revision"]],
        [pip,"install","-r",str(ROOT/lock["requirements_ref"])],
        [pip,"install","--no-deps","-e",lock["code_dir"]],
        [py,str(ROOT/"tools/validate_vbench_runtime.py")],
    ]

def main()->int:
    ap=argparse.ArgumentParser(description="Plan or execute pinned VBench CUDA 12.1 runtime setup.")
    ap.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    lock=load()
    commands=build_commands(lock)
    plan={
      "schema_version":1,
      "status":"PLANNED" if not args.execute else "EXECUTING",
      "runtime_id":lock["runtime_id"],
      "commands":[[str(x) for x in cmd] for cmd in commands],
      "new_resource_creation_authorized":False,
    }
    if not args.execute:
        print(json.dumps(plan,indent=2))
        return 0
    code_dir=Path(lock["code_dir"])
    if code_dir.exists():
        head=subprocess.check_output(["git","-C",str(code_dir),"rev-parse","HEAD"],text=True).strip()
        if head!=lock["code_revision"]:
            raise SystemExit(f"existing VBench checkout revision drift: {head}")
        commands=[cmd for cmd in commands if cmd[0]!="git" or "clone" not in cmd]
    for cmd in commands:
        completed=subprocess.run(cmd,cwd=ROOT,text=True,check=False)
        if completed.returncode!=0:
            raise SystemExit(f"VBench setup command failed ({completed.returncode}): {shlex.join(cmd)}")
    print(json.dumps({"status":"VBENCH_RUNTIME_SETUP_PASS","runtime_id":lock["runtime_id"]},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
