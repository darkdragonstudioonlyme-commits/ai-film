#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from film.blind_scoring import BlindScoreError, parse_score_csv, validate_complete_scores
from film.voice_eval import VOICE_SCORE_SCHEMA, VoiceEvalError, rank_voice_scores, validate_voice_output_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate VoxCPM2 outputs and complete blind scores before unblinding.")
    parser.add_argument("--requests", default="model-evaluations/slice01/voice/requests/requests.json")
    parser.add_argument("--outputs", required=True)
    parser.add_argument("--scores", default="model-evaluations/slice01/voice/packet/scores.csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    requests_path = ROOT / args.requests if not Path(args.requests).is_absolute() else Path(args.requests)
    outputs_path = ROOT / args.outputs if not Path(args.outputs).is_absolute() else Path(args.outputs)
    scores_path = ROOT / args.scores if not Path(args.scores).is_absolute() else Path(args.scores)
    out_path = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)

    request_bundle = json.loads(requests_path.read_text(encoding="utf-8"))
    requests = request_bundle["requests"]
    request_by_blind = {row["blind_id"]: row for row in requests}

    output_bundle = json.loads(outputs_path.read_text(encoding="utf-8"))
    manifests = output_bundle.get("outputs", [])
    output_by_blind = {row.get("blind_id"): row for row in manifests}
    if set(output_by_blind) != set(request_by_blind):
        raise VoiceEvalError("voice output population does not match request population")

    validated_outputs = {
        blind_id: validate_voice_output_manifest(request_by_blind[blind_id], output_by_blind[blind_id])
        for blind_id in sorted(request_by_blind)
    }
    if not all(row["cue_fit"] for row in validated_outputs.values()):
        raise VoiceEvalError("one or more voice outputs exceed cue budget")

    packet = json.loads((ROOT / "model-evaluations/slice01/voice/packet/eval_packet.json").read_text(encoding="utf-8"))
    public_items = [{"blind_id": row["blind_id"]} for row in packet["samples"]]
    score_rows = parse_score_csv(scores_path.read_text(encoding="utf-8"))
    # Completeness is checked before the private identity map is loaded.
    validate_complete_scores(public_items, score_rows, VOICE_SCORE_SCHEMA)

    private = json.loads((ROOT / "model-evaluations/slice01/voice/packet/blind_map_private.json").read_text(encoding="utf-8"))
    ranking = rank_voice_scores(public_items, score_rows, private["mapping"])
    result = {
        "schema_version": 1,
        "status": "UNBLINDED_AFTER_OUTPUT_AND_SCORE_VALIDATION",
        "outputs": validated_outputs,
        "ranking": ranking,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "outputs": len(validated_outputs), "groups": len(ranking)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BlindScoreError, VoiceEvalError) as exc:
        print(f"VOICE_EVAL_FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
