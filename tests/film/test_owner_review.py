import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.owner_review import (
    OwnerReviewError,
    summarize_voice,
    unblind_and_summarize_motion,
    validate_owner_review,
)

ROOT=Path(__file__).resolve().parents[2]
PACKET=json.loads((ROOT/"model-evaluations/slice01/voice/packet/eval_packet.json").read_text())
PRIVATE=json.loads((ROOT/"model-evaluations/slice01/voice/packet/blind_map_private.json").read_text())
VOICE_IDS={row["blind_id"] for row in PACKET["samples"]}


def payload(score=4):
    return {
        "schema_version":1,
        "review_id":"test-owner-review",
        "scale":{"min":0,"max":8},
        "voice":[{"kind":"voice","id":x,"score":score,"notes":""} for x in sorted(VOICE_IDS)],
        "motion":[
            {"kind":"motion","id":"motion_A","score":5,"notes":""},
            {"kind":"motion","id":"motion_B","score":3,"notes":""},
        ],
    }


class OwnerReviewTests(unittest.TestCase):
    def test_complete_0_8_score_set_validates(self):
        out=validate_owner_review(payload(),expected_voice_ids=VOICE_IDS)
        self.assertTrue(out["score_set_complete"])
        self.assertEqual(len(out["voice"]),12)
        self.assertEqual(len(out["motion"]),2)

    def test_incomplete_or_out_of_range_scores_fail_closed(self):
        bad=payload(); bad["voice"].pop()
        with self.assertRaisesRegex(OwnerReviewError,"population mismatch"):
            validate_owner_review(bad,expected_voice_ids=VOICE_IDS)
        bad=payload(); bad["motion"][0]["score"]=9
        with self.assertRaisesRegex(OwnerReviewError,"0-8"):
            validate_owner_review(bad,expected_voice_ids=VOICE_IDS)

    def test_motion_unblinds_only_after_complete_validation(self):
        normalized=validate_owner_review(payload(),expected_voice_ids=VOICE_IDS)
        summary=unblind_and_summarize_motion(
            normalized,
            motion_mapping={"motion_A":"flux2-klein-4b","motion_B":"z-image"},
        )
        self.assertEqual(summary["rows"][0]["reference_model_id"],"flux2-klein-4b")
        self.assertFalse(summary["selection_authorized"])
        self.assertFalse(summary["production_acceptance"])

    def test_voice_summary_groups_character_and_language(self):
        normalized=validate_owner_review(payload(),expected_voice_ids=VOICE_IDS)
        char_by_id={row["blind_id"]:row["character_id"] for row in PRIVATE["mapping"]}
        meta={
            row["blind_id"]:{
                "character_id":char_by_id[row["blind_id"]],
                "language":row["language"],
                "dialogue_id":row["dialogue_id"],
                "target_text":row["target_text"],
            }
            for row in PACKET["samples"]
        }
        summary=summarize_voice(normalized,voice_metadata=meta)
        self.assertEqual(summary["sample_count"],12)
        self.assertEqual(set(summary["by_character"]),{"an","linh"})
        self.assertEqual(set(summary["by_language"]),{"en","zh-CN","vi"})
        self.assertEqual(summary["overall_mean"],4.0)

    def test_cli_writes_non_accepting_summary(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            scores=td/"scores.json"; scores.write_text(json.dumps(payload()))
            mapping=td/"map.json"; mapping.write_text(json.dumps({
                "motion_mapping":{"motion_A":"flux2-klein-4b","motion_B":"z-image"}
            }))
            out=td/"summary.json"
            proc=subprocess.run([
                sys.executable,str(ROOT/"tools/ingest_owner_review_scores.py"),
                "--scores",str(scores),"--motion-map",str(mapping),"--out",str(out)
            ],cwd=ROOT,text=True,capture_output=True,check=False)
            self.assertEqual(proc.returncode,0,proc.stderr)
            summary=json.loads(out.read_text())
            self.assertEqual(summary["quality_status"],"OWNER_SCORED_NOT_PRODUCTION_ACCEPTED")
            self.assertFalse(summary["selection_authorized"])
            self.assertFalse(summary["production_acceptance"])


if __name__=="__main__":
    unittest.main()