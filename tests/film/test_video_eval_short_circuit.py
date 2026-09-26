import json
from pathlib import Path
import tempfile
import unittest

from tools.run_current_video_auto_eval import hard_fail_precheck

ROOT=Path(__file__).resolve().parents[2]
POLICY=json.loads((ROOT/"model-evaluations/auto-eval/policy.json").read_text())
PENDING=json.loads((ROOT/"model-evaluations/auto-eval/vbench_pending_20260926.json").read_text())


class VideoEvalShortCircuitTests(unittest.TestCase):
    def test_vbench_pending_set_skips_existing_hard_fail(self):
        self.assertEqual(PENDING["status"],"READY_GPU_PENDING")
        self.assertEqual(PENDING["eligible_count"],3)
        self.assertNotIn("wan22-sc01-sh04-zimage-ref-v1",PENDING["eligible_asset_ids"])
        self.assertEqual(PENDING["skipped_assets"][0]["asset_id"],"wan22-sc01-sh04-zimage-ref-v1")
        self.assertIn("UNMOTIVATED_READABLE_TEXT",PENDING["skipped_assets"][0]["hard_fail_tags"])
        self.assertFalse(PENDING["new_resource_creation_authorized"])
        self.assertFalse(PENDING["production_acceptance"])

    def test_existing_hard_fail_short_circuits_missing_evaluators(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            receipt=td/"ocr.json"
            receipt.write_text(json.dumps({
                "schema_version":1,
                "evaluator_id":"paddleocr-text-artifact",
                "asset_id":"clip-a",
                "status":"PASS_MODEL_EVAL",
                "metrics":{"text_artifact_free":75.0},
                "hard_fail_tags":["UNMOTIVATED_READABLE_TEXT"],
                "production_acceptance":False,
            }))
            jobs={
                "ocr":{"receipt":receipt},
                "qwen":{"receipt":td/"qwen.json"},
                "vbench":{"receipt":td/"vbench.json"},
            }
            decision=hard_fail_precheck(POLICY,asset_id="clip-a",jobs=jobs)
            self.assertIsNotNone(decision)
            self.assertEqual(decision["status"],"AUTO_REJECT_HARD_FAIL")
            self.assertIn("UNMOTIVATED_READABLE_TEXT",decision["triggered_hard_fail_tags"])


if __name__=="__main__":
    unittest.main()
