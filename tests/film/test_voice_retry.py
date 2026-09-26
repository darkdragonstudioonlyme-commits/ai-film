import json
from pathlib import Path
import unittest

from film.voice_retry import VoiceRetryError, build_retry_plan, build_voice_retry_request

ROOT=Path(__file__).resolve().parents[2]
REQUESTS=json.loads((ROOT/"model-evaluations/slice01/voice/requests/requests.json").read_text())["requests"]
EVIDENCE=json.loads((ROOT/"run-evidence/AUTO_EVAL_VOICE_WHISPER_V2_20260926.json").read_text())


class VoiceRetryTests(unittest.TestCase):
    def test_retry_plan_contains_only_two_zh_cue_overflow_samples(self):
        plan=build_retry_plan(requests=REQUESTS,auto_eval_results=EVIDENCE["results"])
        self.assertEqual(plan["retry_count"],2)
        self.assertEqual({r["blind_id"] for r in plan["requests"]},{"vox_ae6c3e5af03f","vox_6cd531479b73"})
        self.assertEqual({r["language"] for r in plan["requests"]},{"zh-CN"})
        self.assertFalse(plan["human_review_required"])
        self.assertFalse(plan["production_acceptance"])
        self.assertFalse(plan["new_resource_creation_authorized"])

    def test_retry_preserves_text_model_and_no_clone(self):
        by_blind={r["blind_id"]:r for r in REQUESTS}
        plan=build_retry_plan(requests=REQUESTS,auto_eval_results=EVIDENCE["results"])
        for retry in plan["requests"]:
            source=by_blind[retry["blind_id"]]
            self.assertEqual(retry["target_text"],source["target_text"])
            self.assertEqual(retry["model"],source["model"])
            self.assertEqual(retry["voice_group"],source["voice_group"])
            self.assertIsNone(retry["reference_audio"])
            self.assertFalse(retry["execution_permitted"])
            self.assertEqual(retry["retry_reason"],"CUE_OVERFLOW")
            self.assertIn("slightly brisk pace",retry["voice_design_description"])
            self.assertNotEqual(retry["seed"],source["seed"])
            self.assertNotEqual(retry["request_digest"],source["request_digest"])

    def test_non_retry_source_is_rejected(self):
        source=next(r for r in REQUESTS if r["blind_id"]=="vox_52af55f53319")
        with self.assertRaisesRegex(VoiceRetryError,"AUTO_RETRY"):
            build_voice_retry_request(source,source_asset_id=source["blind_id"],source_status="AUTO_SHORTLIST",source_score=100)


if __name__=="__main__":
    unittest.main()
