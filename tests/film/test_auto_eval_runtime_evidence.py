import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
VOICE_V1=json.loads((ROOT/"run-evidence/AUTO_EVAL_VOICE_WHISPER_20260926.json").read_text())
VOICE=json.loads((ROOT/"run-evidence/AUTO_EVAL_VOICE_WHISPER_V2_20260926.json").read_text())
OCR=json.loads((ROOT/"run-evidence/AUTO_EVAL_VIDEO_PADDLEOCR_20260926.json").read_text())
QWEN=json.loads((ROOT/"run-evidence/AUTO_EVAL_VIDEO_QWEN3VL_20260926.json").read_text())
VIDEO=json.loads((ROOT/"run-evidence/AUTO_EVAL_VIDEO_PARTIAL_ENSEMBLE_20260926.json").read_text())
REG=json.loads((ROOT/"model-evaluations/auto-eval/evaluator_registry.json").read_text())
RUNTIME=json.loads((ROOT/"model-evaluations/auto-eval/runtime_profiles.json").read_text())


class AutoEvalRuntimeEvidenceTests(unittest.TestCase):
    def test_voice_whisper_v1_is_retained_and_v2_is_canonical(self):
        self.assertEqual(VOICE_V1["status"],"PASS_AUTO_EVAL_COMPLETE")
        self.assertEqual(VOICE_V1["sample_count"],12)
        self.assertEqual(VOICE["status"],"PASS_AUTO_EVAL_RECOMPUTE_COMPLETE")
        self.assertEqual(VOICE["sample_count"],12)
        self.assertEqual(VOICE["status_counts"],{
            "AUTO_SHORTLIST":10,
            "AUTO_RETRY":2,
        })
        self.assertEqual(VOICE["rejected_asset_ids"],[])
        self.assertEqual(VOICE["normalizer_revision"],"whisper-text-normalizer-v2")
        self.assertTrue(VOICE["recomputed_without_inference"])
        self.assertFalse(VOICE["human_review_required"])
        self.assertFalse(VOICE["production_acceptance"])
        self.assertEqual(len(VOICE["results"]),12)

    def test_qwen_and_paddle_have_four_runtime_receipts_each(self):
        self.assertEqual(QWEN["status"],"PASS_AUTO_EVAL_COMPLETE")
        self.assertEqual(QWEN["sample_count"],4)
        self.assertEqual(OCR["status"],"PASS_AUTO_EVAL_COMPLETE")
        self.assertEqual(OCR["sample_count"],4)
        self.assertFalse(QWEN["production_acceptance"])
        self.assertFalse(OCR["production_acceptance"])
        qwen_ids={r["asset_id"] for r in QWEN["results"]}
        ocr_ids={r["asset_id"] for r in OCR["results"]}
        self.assertEqual(qwen_ids,ocr_ids)

    def test_ocr_hard_fail_is_preserved_for_zimage_motion(self):
        by_id={r["asset_id"]:r for r in OCR["results"]}
        self.assertIn("UNMOTIVATED_READABLE_TEXT",by_id["wan22-sc01-sh04-zimage-ref-v1"]["hard_fail_tags"])
        for asset_id in (
            "wan22-sc01-sh04-flux2-ref-v1",
            "world-tang-changan-motion-v1",
            "world-paris-belle-epoque-motion-v1",
        ):
            self.assertEqual(by_id[asset_id]["hard_fail_tags"],[])

    def test_video_ensemble_is_partial_only_because_vbench_is_missing(self):
        self.assertEqual(VIDEO["status"],"PARTIAL_EVALUATOR_RECEIPTS")
        self.assertEqual(set(VIDEO["completed_evaluators"]),{
            "qwen3-vl-2b-semantic",
            "paddleocr-text-artifact",
        })
        self.assertEqual(VIDEO["missing_evaluator"],"vbench-video-v0.1.5")
        self.assertEqual(VIDEO["blocker"],"EXISTING_A40_HOST_CAPACITY")
        self.assertFalse(VIDEO["human_review_required"])
        self.assertFalse(VIDEO["production_acceptance"])

    def test_registry_runtime_readiness_matches_actual_qualification(self):
        by_id={r["evaluator_id"]:r for r in REG["evaluators"]}
        self.assertTrue(by_id["whisper-turbo-asr"]["execution_ready"])
        self.assertTrue(by_id["qwen3-vl-2b-semantic"]["execution_ready"])
        self.assertTrue(by_id["paddleocr-text-artifact"]["execution_ready"])
        self.assertFalse(by_id["vbench-video-v0.1.5"]["execution_ready"])
        self.assertFalse(by_id["dover-video-quality"]["enabled"])
        self.assertEqual(by_id["dover-video-quality"]["license_gate"],"BLOCKED_NONCOMMERCIAL")
        profiles={r["runtime_profile"]:r for r in RUNTIME["profiles"]}
        self.assertEqual(profiles["whisper-cpu-local"]["setup_status"],"QUALIFIED_LOCAL_CPU_PASS")
        self.assertEqual(profiles["qwen3vl-cpu-local"]["setup_status"],"QUALIFIED_LOCAL_CPU_PASS")
        self.assertEqual(profiles["paddleocr-cpu"]["setup_status"],"QUALIFIED_LOCAL_CPU_PASS")
        self.assertEqual(profiles["vbench-cu121"]["setup_status"],"BUNDLE_READY_GPU_EXECUTION_BLOCKED")


if __name__=="__main__":
    unittest.main()
