import json
from pathlib import Path
import tempfile
import unittest

from film.longform_review import LongformReviewError, build_review_packet, calibration_status, ingest_owner_review, validate_policy

ROOT=Path(__file__).resolve().parents[2]
POLICY=json.loads((ROOT/"model-evaluations/auto-eval/longform_review_policy.json").read_text())


def packet():
    return build_review_packet(
        POLICY,
        stage="longform_rough_cut",
        project_id="slice01",
        media_qc={"sha256":"a"*64,"duration_sec":75.0},
        auto_eval_summary_refs=["run-evidence/example.json"],
    )


class LongformReviewTests(unittest.TestCase):
    def test_policy_defers_human_review_to_longform_and_disables_auto_mutation(self):
        p=validate_policy(POLICY)
        self.assertTrue(p["stages"]["longform_rough_cut"]["human_review_required"])
        self.assertTrue(p["stages"]["final_cut"]["human_review_required"])
        self.assertFalse(p["calibration"]["automatic_policy_mutation"])

    def test_packet_is_hash_bound_and_non_accepting(self):
        p=packet()
        self.assertTrue(p["human_review_required"])
        self.assertEqual(p["scale"],{"min":0,"max":8})
        self.assertEqual(len(p["criteria"]),10)
        self.assertTrue(all(v is None for v in p["scores"].values()))
        self.assertFalse(p["production_acceptance"])
        self.assertFalse(p["publish_authority"])

    def test_completed_review_requires_all_integer_scores(self):
        p=packet()
        completed={
            "review_id":p["review_id"],
            "media_sha256":p["media_sha256"],
            "scale":{"min":0,"max":8},
            "scores":{name:6 for name in p["criteria"]},
            "notes":"rough cut label",
        }
        result=ingest_owner_review(POLICY,p,completed)
        self.assertEqual(result["overall_score"],6)
        self.assertEqual(result["mean_score"],6.0)
        self.assertTrue(result["calibration_label"])
        self.assertFalse(result["production_acceptance"])
        bad=dict(completed); bad["scores"]=dict(completed["scores"]); bad["scores"].pop("pacing")
        with self.assertRaisesRegex(LongformReviewError,"population mismatch"):
            ingest_owner_review(POLICY,p,bad)

    def test_calibration_requires_three_unique_longform_labels(self):
        self.assertEqual(calibration_status(POLICY,[])["status"],"COLLECT_MORE_LONGFORM_LABELS")
        rows=[{"review_id":f"r{i}","calibration_label":True} for i in range(3)]
        status=calibration_status(POLICY,rows)
        self.assertEqual(status["status"],"READY_FOR_WEIGHT_SUGGESTION")
        self.assertFalse(status["automatic_policy_mutation"])


if __name__=="__main__":
    unittest.main()
