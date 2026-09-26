#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from film.owner_review import (
    summarize_voice,
    unblind_and_summarize_motion,
    validate_owner_review,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main()->int:
    ap=argparse.ArgumentParser(description="Validate complete owner 0-8 voice/motion review and unblind motion only after completion.")
    ap.add_argument("--scores",required=True)
    ap.add_argument("--motion-map",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    packet=load(ROOT/"model-evaluations/slice01/voice/packet/eval_packet.json")
    private=load(ROOT/"model-evaluations/slice01/voice/packet/blind_map_private.json")
    expected_voice={row["blind_id"] for row in packet["samples"]}
    normalized=validate_owner_review(
        load(Path(args.scores)),
        expected_voice_ids=expected_voice,
    )

    char_by_id={row["blind_id"]:row["character_id"] for row in private["mapping"]}
    meta={
        row["blind_id"]:{
            "character_id":char_by_id[row["blind_id"]],
            "language":row["language"],
            "dialogue_id":row["dialogue_id"],
            "target_text":row["target_text"],
        }
        for row in packet["samples"]
    }
    mapping_payload=load(Path(args.motion_map))
    motion_mapping=mapping_payload.get("motion_mapping",mapping_payload)
    summary={
        "schema_version":1,
        "review_id":normalized["review_id"],
        "scale":normalized["scale"],
        "score_set_complete":True,
        "voice":summarize_voice(normalized,voice_metadata=meta),
        "motion":unblind_and_summarize_motion(normalized,motion_mapping=motion_mapping),
        "quality_status":"OWNER_SCORED_NOT_PRODUCTION_ACCEPTED",
        "selection_authorized":False,
        "production_acceptance":False,
    }
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":"PASS_COMPLETE_OWNER_REVIEW",
        "voice_samples":summary["voice"]["sample_count"],
        "motion_samples":summary["motion"]["sample_count"],
        "out":str(out),
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())