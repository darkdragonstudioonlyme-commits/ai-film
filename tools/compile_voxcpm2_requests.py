#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.voice_eval import compile_voxcpm2_requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile VoxCPM2 Voice Design requests without synthesis.")
    parser.add_argument("--out-dir", default="model-evaluations/slice01/voice/requests")
    args = parser.parse_args()

    config = json.loads((ROOT / "model-evaluations/slice01/voice/voxcpm2_eval_config.json").read_text(encoding="utf-8"))
    packet = json.loads((ROOT / "model-evaluations/slice01/voice/packet/eval_packet.json").read_text(encoding="utf-8"))
    requests = compile_voxcpm2_requests(config, packet)

    out = Path(args.out_dir)
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)
    (out / "requests.json").write_text(
        json.dumps({
            "schema_version": 1,
            "status": "COMPILED_NOT_EXECUTED",
            "request_count": len(requests),
            "requests": requests,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for request in requests:
        (out / f"{request['request_id']}.json").write_text(
            json.dumps(request, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    output_contract = {
        "schema_version": 1,
        "status": "SCHEMA_ONLY_NO_AUDIO",
        "required_fields": [
            "request_digest",
            "blind_id",
            "audio_sha256",
            "sample_rate_hz",
            "duration_sec",
            "bytes",
        ],
        "sample_rate_hz": config["model"]["sample_rate_hz"],
        "note": "One output manifest is required per request after synthesis. No output is accepted unless it binds the exact request_digest.",
    }
    (out / "output_manifest_contract.json").write_text(
        json.dumps(output_contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "COMPILED_NOT_EXECUTED",
        "requests": len(requests),
        "reference_audio_count": sum(request["reference_audio"] is not None for request in requests),
        "out_dir": str(out),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
