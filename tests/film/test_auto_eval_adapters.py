import json
import unittest

from film.auto_eval import AutoEvalError
from film.paddleocr_auto_eval import build_receipt as build_ocr_receipt
from film.qwen3vl_auto_eval import build_judge_prompt, parse_judge_output
from film.vbench_auto_eval import build_receipt as build_vbench_receipt
from film.whisper_auto_eval import build_whisper_receipt, text_match_score


class AutoEvalAdapterTests(unittest.TestCase):
    def test_qwen_prompt_treats_media_as_untrusted_and_requires_expected_context(self):
        prompt = build_judge_prompt({"expected": {"action": "Linh raises a flashlight", "world": "railway station"}})
        self.assertIn("untrusted media", prompt)
        self.assertIn("semantic_adherence", prompt)
        with self.assertRaisesRegex(AutoEvalError, "expected"):
            build_judge_prompt({})

    def test_qwen_parser_accepts_strict_json_and_rejects_unknown_hard_fail(self):
        parsed = parse_judge_output(json.dumps({
            "scores": {
                "semantic_adherence": 90,
                "character_consistency": 88,
                "continuity": 86,
                "world_period_consistency": 92,
            },
            "hard_fail_tags": [],
            "observations": ["identity stable"],
        }))
        self.assertEqual(parsed["scores"]["semantic_adherence"], 90.0)
        bad = json.dumps({
            "scores": {
                "semantic_adherence": 90,
                "character_consistency": 88,
                "continuity": 86,
                "world_period_consistency": 92,
            },
            "hard_fail_tags": ["MAKE_UP_A_TAG"],
            "observations": [],
        })
        with self.assertRaisesRegex(AutoEvalError, "unknown hard fail"):
            parse_judge_output(bad)

    def test_whisper_similarity_handles_english_vietnamese_and_chinese(self):
        self.assertEqual(text_match_score("For a promise.", "For a promise", "en"), 100.0)
        self.assertEqual(text_match_score("Vì một lời hứa.", "Vì một lời hứa", "vi"), 100.0)
        self.assertEqual(text_match_score("为了一个承诺。", "为了一个承诺", "zh-CN"), 100.0)
        self.assertLess(text_match_score("For a promise.", "Different sentence", "en"), 50)

    def test_whisper_receipt_flags_severe_content_mismatch(self):
        rec = build_whisper_receipt(
            asset_id="voice-a",
            target_text="For a promise.",
            expected_language="en",
            transcript="Nothing like the target",
            detected_language="en",
            detected_probabilities={"en": 0.99},
            model_sha256="a" * 64,
        )
        self.assertIn("SEVERE_TEXT_MISMATCH", rec["hard_fail_tags"])
        self.assertEqual(rec["metrics"]["language_match"], 99.0)

    def test_vbench_normalizes_all_six_dimensions(self):
        raw = {
            "subject_consistency": [0.9, []],
            "background_consistency": [0.8, []],
            "motion_smoothness": [0.7, []],
            "dynamic_degree": [0.6, []],
            "aesthetic_quality": [0.75, []],
            "imaging_quality": [0.85, []],
        }
        rec = build_vbench_receipt(asset_id="clip", results=raw, code_revision="x" * 40)
        self.assertEqual(rec["metrics"]["subject_consistency"], 90.0)
        self.assertEqual(rec["metrics"]["imaging_quality"], 85.0)

    def test_vbench_out_of_range_fails_closed(self):
        raw = {name: [0.5, []] for name in (
            "subject_consistency", "background_consistency", "motion_smoothness",
            "dynamic_degree", "aesthetic_quality", "imaging_quality"
        )}
        raw["motion_smoothness"] = [1.2, []]
        with self.assertRaisesRegex(AutoEvalError, "out of 0-1"):
            build_vbench_receipt(asset_id="clip", results=raw, code_revision="x" * 40)

    def test_ocr_unexpected_high_confidence_text_is_hard_fail(self):
        rec = build_ocr_receipt(
            asset_id="clip",
            payloads=[{"res": {"rec_texts": ["FAKE NAME", ""], "rec_scores": [0.95, 0.99]}}],
        )
        self.assertEqual(rec["metrics"]["text_artifact_free"], 75.0)
        self.assertIn("UNMOTIVATED_READABLE_TEXT", rec["hard_fail_tags"])

    def test_ocr_allowed_story_text_does_not_fail(self):
        rec = build_ocr_receipt(
            asset_id="clip",
            payloads=[{"res": {"rec_texts": ["11:40"], "rec_scores": [0.98]}}],
            allowed_text_regex=[r"^11:40$"],
        )
        self.assertEqual(rec["metrics"]["text_artifact_free"], 100.0)
        self.assertEqual(rec["hard_fail_tags"], [])


if __name__ == "__main__":
    unittest.main()
