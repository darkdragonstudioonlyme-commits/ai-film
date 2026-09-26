import copy
import json
from pathlib import Path
import tempfile
import unittest

from film.auto_eval import (
    AutoEvalError,
    aggregate_auto_eval,
    build_eval_plan,
    rank_auto_eval_results,
    validate_registry,
)

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=json.loads((ROOT/"model-evaluations/auto-eval/evaluator_registry.json").read_text())
POLICY=json.loads((ROOT/"model-evaluations/auto-eval/policy.json").read_text())


def receipt(evaluator_id,asset_id="clip-a",metrics=None,tags=None,status="PASS_MODEL_EVAL"):
    return {
        "schema_version":1,
        "evaluator_id":evaluator_id,
        "asset_id":asset_id,
        "status":status,
        "metrics":metrics or {},
        "hard_fail_tags":tags or [],
        "evidence":{"test":True},
    }


class AutoEvalTests(unittest.TestCase):
    def test_registry_blocks_noncommercial_dover_from_active_stack(self):
        reg=validate_registry(REGISTRY)
        dover=next(x for x in reg["evaluators"] if x["family"]=="DOVER")
        self.assertFalse(dover["enabled"])
        self.assertEqual(dover["license_gate"],"BLOCKED_NONCOMMERCIAL")
        self.assertIn("NONCOMMERCIAL_LICENSE",dover["blockers"])

    def test_current_video_plan_is_blocked_only_by_model_setup(self):
        plan=build_eval_plan(
            REGISTRY,POLICY,
            stage="short_video_take",
            asset_id="clip-a",
            asset_path="/tmp/clip-a.mp4",
        )
        self.assertEqual(plan["status"],"BLOCKED_EVALUATOR_SETUP")
        self.assertEqual(set(plan["setup_required"]),{
            "vbench-video-v0.1.5",
        })
        self.assertEqual(plan["min_model_evaluators"],3)
        self.assertFalse(plan["production_acceptance"])

    def test_active_evaluator_cannot_have_uncleared_license(self):
        bad=copy.deepcopy(REGISTRY)
        row=next(x for x in bad["evaluators"] if x["family"]=="DOVER")
        row["enabled"]=True
        with self.assertRaisesRegex(AutoEvalError,"uncleared license"):
            validate_registry(bad)

    def test_video_ensemble_shortlists_high_score_without_production_acceptance(self):
        receipts=[
            receipt("vbench-video-v0.1.5",metrics={
                "subject_consistency":92,
                "background_consistency":88,
                "motion_smoothness":82,
                "aesthetic_quality":76,
                "imaging_quality":80,
            }),
            receipt("qwen3-vl-2b-semantic",metrics={
                "semantic_adherence":90,
                "character_consistency":89,
                "continuity":86,
                "world_period_consistency":84,
            }),
            receipt("paddleocr-text-artifact",metrics={"text_artifact_free":100}),
        ]
        result=aggregate_auto_eval(POLICY,stage="short_video_take",asset_id="clip-a",receipts=receipts)
        self.assertEqual(result["status"],"AUTO_SHORTLIST")
        self.assertGreaterEqual(result["score"],70)
        self.assertTrue(result["auto_shortlist"])
        self.assertFalse(result["production_acceptance"])
        self.assertFalse(result["human_review_required"])

    def test_hard_fail_precedes_score(self):
        receipts=[
            receipt("vbench-video-v0.1.5",metrics={
                "subject_consistency":99,
                "background_consistency":99,
                "motion_smoothness":99,
                "aesthetic_quality":99,
                "imaging_quality":99,
            }),
            receipt("qwen3-vl-2b-semantic",metrics={
                "semantic_adherence":99,
                "character_consistency":99,
                "continuity":99,
                "world_period_consistency":99,
            },tags=["SEVERE_IDENTITY_BREAK"]),
            receipt("paddleocr-text-artifact",metrics={"text_artifact_free":100}),
        ]
        result=aggregate_auto_eval(POLICY,stage="short_video_take",asset_id="clip-a",receipts=receipts)
        self.assertEqual(result["status"],"AUTO_REJECT_HARD_FAIL")
        self.assertIsNone(result["score"])
        self.assertFalse(result["auto_shortlist"])

    def test_missing_required_evaluator_blocks(self):
        result=aggregate_auto_eval(
            POLICY,
            stage="short_video_take",
            asset_id="clip-a",
            receipts=[
                receipt("vbench-video-v0.1.5",metrics={}),
                receipt("qwen3-vl-2b-semantic",metrics={}),
            ],
        )
        self.assertEqual(result["status"],"BLOCKED_EVALUATOR_GAP")
        self.assertEqual(result["missing_evaluators"],["paddleocr-text-artifact"])

    def test_voice_whisper_plus_deterministic_cue_metrics_can_shortlist(self):
        result=aggregate_auto_eval(
            POLICY,
            stage="voice_take",
            asset_id="voice-a",
            receipts=[receipt("whisper-turbo-asr",asset_id="voice-a",metrics={
                "asr_text_match":96,
                "language_match":100,
            })],
            deterministic_metrics={"cue_fit":100},
        )
        self.assertEqual(result["status"],"AUTO_SHORTLIST")
        self.assertFalse(result["production_acceptance"])

    def test_longform_requires_human_review_even_with_same_video_metrics(self):
        receipts=[
            receipt("vbench-video-v0.1.5",asset_id="film-a",metrics={
                "subject_consistency":92,
                "background_consistency":88,
                "motion_smoothness":82,
                "aesthetic_quality":76,
                "imaging_quality":80,
            }),
            receipt("qwen3-vl-2b-semantic",asset_id="film-a",metrics={
                "semantic_adherence":90,
                "character_consistency":89,
                "continuity":86,
                "world_period_consistency":84,
            }),
            receipt("paddleocr-text-artifact",asset_id="film-a",metrics={"text_artifact_free":100}),
        ]
        result=aggregate_auto_eval(POLICY,stage="longform_rough_cut",asset_id="film-a",receipts=receipts)
        self.assertEqual(result["status"],"AUTO_SHORTLIST")
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["production_acceptance"])

    def test_ranking_prefers_shortlist_then_score_and_keeps_rejects(self):
        rows=rank_auto_eval_results([
            {"asset_id":"c","status":"AUTO_REJECT_HARD_FAIL","score":None},
            {"asset_id":"b","status":"AUTO_SHORTLIST","score":75},
            {"asset_id":"a","status":"AUTO_SHORTLIST","score":85},
            {"asset_id":"d","status":"AUTO_RETRY","score":65},
        ])
        self.assertEqual([x["asset_id"] for x in rows],["a","b","d","c"])
        self.assertEqual(rows[0]["auto_rank"],1)


if __name__=="__main__":
    unittest.main()
