import json
from pathlib import Path
import unittest

from film.batch_orchestrator import build_argv, validate_config
from film.voxcpm2_live import build_cost_entry
from tools.run_voxcpm2_live import pick_request

ROOT=Path(__file__).resolve().parents[2]
RETRY_FILE=ROOT/"model-evaluations/auto-eval/voice_retry_plan_20260926.json"
BATCH=json.loads((ROOT/"model-evaluations/auto-eval/batches/voxcpm2_retry_zh_20260926.json").read_text())


class VoiceRetryBatchTests(unittest.TestCase):
    def test_retry_file_requests_are_resolvable_by_live_runner(self):
        plan=json.loads(RETRY_FILE.read_text())
        for row in plan["requests"]:
            picked=pick_request(row["request_id"],request_file=RETRY_FILE)
            self.assertEqual(picked["request_digest"],row["request_digest"])
            self.assertEqual(picked["retry_reason"],"CUE_OVERFLOW")
            self.assertIsNone(picked["reference_audio"])

    def test_batch_routes_same_voxcpm2_adapter_with_explicit_request_file(self):
        jobs=validate_config(BATCH)
        self.assertEqual(len(jobs),2)
        for job in jobs:
            self.assertEqual(job["adapter"],"voxcpm2-live")
            argv=build_argv(job,root=ROOT,execute=True)
            self.assertIn("--request-file",argv)
            self.assertIn("model-evaluations/auto-eval/voice_retry_plan_20260926.json",argv)
            self.assertIn("--execute",argv)
            self.assertEqual(job["model_dir"],"/workspace/models/voxcpm2")
            self.assertTrue(job["receipt_path"].startswith("/workspace/runs/voxcpm2-retry/"))

    def test_retry_cost_entries_use_retry_logical_key(self):
        request=pick_request(json.loads(RETRY_FILE.read_text())["requests"][0]["request_id"],request_file=RETRY_FILE)
        qual={"request":request,"rate_usd_per_hour":0.49}
        row=build_cost_entry(qualification=qual,elapsed_sec=10.0,passed=True)
        self.assertEqual(row["logical_key"],"T-064-VOXCPM2-AUTO-EVAL-RETRY")
        self.assertEqual(row["category"],"COMPUTE_ACCEPTED")


if __name__=="__main__":
    unittest.main()
