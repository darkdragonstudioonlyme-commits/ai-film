import json
from pathlib import Path
import unittest

from film.video_technical_auto_eval import build_receipt

ROOT=Path(__file__).resolve().parents[2]
EV=json.loads((ROOT/"run-evidence/AUTO_EVAL_VIDEO_TECHNICAL_QC_20260926.json").read_text())
REG=json.loads((ROOT/"model-evaluations/auto-eval/evaluator_registry.json").read_text())


class VideoTechnicalAutoEvalTests(unittest.TestCase):
    def test_current_four_videos_decode_without_black_hard_fail(self):
        self.assertEqual(EV["status"],"PASS_TECHNICAL_QC_COMPLETE")
        self.assertEqual(EV["sample_count"],4)
        self.assertTrue(EV["supplemental_only"])
        self.assertFalse(EV["counts_toward_min_model_evaluators"])
        self.assertFalse(EV["production_acceptance"])
        self.assertEqual(len(EV["results"]),4)
        for row in EV["results"]:
            self.assertGreater(row["frame_count"],0)
            self.assertEqual(row["black_frame_ratio"],0.0)
            self.assertEqual(row["hard_fail_tags"],[])
            self.assertEqual(row["metrics"]["decode_integrity"],100.0)
            self.assertEqual(row["metrics"]["non_black_frames"],100.0)

    def test_black_video_threshold_produces_existing_policy_hard_fail(self):
        receipt=build_receipt(
            asset_id="black",
            frame_count=10,
            black_frame_count=9,
            freeze_transition_count=9,
            mean_frame_delta=0.0,
            max_frame_delta=0.0,
            mean_luma=0.2,
            ffmpeg_path="/tmp/ffmpeg",
        )
        self.assertIn("BLACK_OR_EMPTY_VIDEO",receipt["hard_fail_tags"])
        self.assertEqual(receipt["metrics"]["non_black_frames"],10.0)
        self.assertTrue(receipt["supplemental_only"])
        self.assertFalse(receipt["counts_toward_min_model_evaluators"])

    def test_registry_marks_technical_qc_supplemental_not_required(self):
        row=next(r for r in REG["evaluators"] if r["evaluator_id"]=="deterministic-video-qc")
        self.assertTrue(row["enabled"])
        self.assertTrue(row["execution_ready"])
        self.assertTrue(row["supplemental_only"])
        self.assertFalse(row["counts_toward_min_model_evaluators"])
        self.assertEqual(row["required_for"],[])


if __name__=="__main__":
    unittest.main()
