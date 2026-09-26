#!/usr/bin/env python3
from __future__ import annotations
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
lock=json.loads((ROOT/"model-evaluations/auto-eval/vbench_runtime_lock.json").read_text())
import torch,torchvision
if torch.version.cuda!=lock["required_torch_cuda"]:
    raise SystemExit(f"VBench torch CUDA drift: {torch.version.cuda}")
if not torch.cuda.is_available():
    raise SystemExit("VBench CUDA unavailable")
if torch.cuda.get_device_name(0)!=lock["required_gpu"]:
    raise SystemExit(f"VBench GPU drift: {torch.cuda.get_device_name(0)}")
head=subprocess.check_output(["git","-C",lock["code_dir"],"rev-parse","HEAD"],text=True).strip()
if head!=lock["code_revision"]:
    raise SystemExit(f"VBench repo revision drift: {head}")
import vbench
print(json.dumps({
  "status":"VBENCH_RUNTIME_VALID",
  "torch":torch.__version__,
  "torchvision":torchvision.__version__,
  "torch_cuda":torch.version.cuda,
  "gpu":torch.cuda.get_device_name(0),
  "code_revision":head
},sort_keys=True))
