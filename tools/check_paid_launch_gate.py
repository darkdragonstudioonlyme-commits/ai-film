#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from film.launch_gate import LaunchGateError, validate_launch_authorization

def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipt",default="model-evaluations/slice01/launch_authorization.placeholder.json")
    ap.add_argument("--gpu",default="RTX 5090")
    ap.add_argument("--max-usd",type=float,default=60.0)
    args=ap.parse_args()
    proposal=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))
    rates=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
    receipt_path=Path(args.receipt)
    if not receipt_path.is_absolute(): receipt_path=ROOT/receipt_path
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    try:
        result=validate_launch_authorization(receipt,proposal_digest=canonical_digest(proposal),rate_snapshot=rates,requested_gpu=args.gpu,requested_max_usd=args.max_usd)
    except LaunchGateError as exc:
        print("LAUNCH_GATE_BLOCKED: "+str(exc),file=sys.stderr)
        return 2
    print(json.dumps(result,sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
