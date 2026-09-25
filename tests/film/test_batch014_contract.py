import copy
import json
from pathlib import Path
import unittest

from film.script_engine import ScriptContractError, validate_screenplay, validate_screenplay_against_shots, validate_source_rights
from film.localization import LocalizationError, validate_localization_bundle
from film.reframe import ReframePlanError, compile_reframe_plan

ROOT=Path(__file__).resolve().parents[2]
SCREENPLAY=json.loads((ROOT/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
RIGHTS=json.loads((ROOT/"projects/slice01/rights/rights_register.json").read_text(encoding="utf-8"))
BUNDLE=json.loads((ROOT/"projects/slice01/localization/dialogue_bundle.json").read_text(encoding="utf-8"))
TIMING=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
REFRAME_POLICY=json.loads((ROOT/"projects/slice01/framing/reframe_policy.json").read_text(encoding="utf-8"))

EXPECTED_DIALOGUE={shot["dialogue_id"] for shot in SHOTS if shot.get("dialogue_id")}
BUDGETS={row["dialogue_id"]:float(row["end_offset_sec"])-float(row["start_offset_sec"]) for row in TIMING["dialogue_cues"]}

def sha(ch):
    return (ch*64)[:64]

class ScriptEngineTests(unittest.TestCase):
    def test_current_screenplay_is_75s_and_matches_shots(self):
        s=validate_source_rights(SCREENPLAY,RIGHTS["records"])
        s=validate_screenplay_against_shots(SCREENPLAY,SHOTS)
        self.assertEqual(s["target_duration_sec"],75.0)
        self.assertEqual(len(s["scene_ids"]),1)
        self.assertEqual(len(s["beat_ids"]),6)
        self.assertEqual(set(s["dialogue_ids"]),EXPECTED_DIALOGUE)

    def test_original_source_requires_original_rights(self):
        bad=copy.deepcopy(SCREENPLAY)
        bad["source"]["rights_status"]="UNKNOWN"
        with self.assertRaisesRegex(ScriptContractError,"ORIGINAL"):
            validate_screenplay(bad)

    def test_source_rights_register_must_match(self):
        records=copy.deepcopy(RIGHTS["records"])
        record=next(row for row in records if row["rights_id"]=="source-original")
        record["status"]="BLOCKED"
        with self.assertRaisesRegex(ScriptContractError,"rights status mismatch"):
            validate_source_rights(SCREENPLAY,records)

    def test_beat_timeline_gap_rejected(self):
        bad=copy.deepcopy(SCREENPLAY)
        bad["scenes"][0]["beats"][2]["start_sec"]=35.0
        with self.assertRaisesRegex(ScriptContractError,"not contiguous"):
            validate_screenplay(bad)

    def test_screenplay_dialogue_population_must_match_shots(self):
        bad=copy.deepcopy(SCREENPLAY)
        bad["scenes"][0]["dialogue"]=bad["scenes"][0]["dialogue"][:-1]
        with self.assertRaisesRegex(ScriptContractError,"dialogue mismatch"):
            validate_screenplay_against_shots(bad,SHOTS)

class LocalizationTests(unittest.TestCase):
    def test_current_bundle_has_only_zh_timing_pending(self):
        report=validate_localization_bundle(BUNDLE,expected_dialogue_ids=EXPECTED_DIALOGUE,cue_budgets_sec=BUDGETS)
        self.assertEqual(report["status"],"PARTIAL_OR_BLOCKED")
        self.assertEqual(len(report["lines"]),4)
        self.assertEqual(
            report["blockers"],
            [f"timing-not-measured:{dialogue_id}:zh-CN" for dialogue_id in sorted(EXPECTED_DIALOGUE)]
        )
        for line in report["lines"]:
            self.assertEqual(line["timing_measurements"]["en"]["status"],"PREVIS_MEASURED")
            self.assertEqual(line["timing_measurements"]["vi"]["status"],"PREVIS_MEASURED")
            self.assertIsNone(line["timing_measurements"]["zh-CN"]["duration_sec"])

    def test_missing_translation_is_visible_blocker(self):
        bad=copy.deepcopy(BUNDLE)
        bad["lines"][0]["texts"]["vi"]=""
        report=validate_localization_bundle(bad,expected_dialogue_ids=EXPECTED_DIALOGUE,cue_budgets_sec=BUDGETS)
        self.assertIn("missing-text:dlg_001:vi",report["blockers"])

    def test_over_budget_measurement_blocks(self):
        bad=copy.deepcopy(BUNDLE)
        bad["lines"][0]["timing_measurements"]["en"]["duration_sec"]=99.0
        report=validate_localization_bundle(bad,expected_dialogue_ids=EXPECTED_DIALOGUE,cue_budgets_sec=BUDGETS)
        self.assertTrue(any(x.startswith("timing-over-budget:dlg_001:en") for x in report["blockers"]))

    def test_dialogue_id_drift_rejected(self):
        bad=copy.deepcopy(BUNDLE)
        bad["lines"][0]["dialogue_id"]="dlg_wrong"
        with self.assertRaisesRegex(LocalizationError,"population mismatch"):
            validate_localization_bundle(bad,expected_dialogue_ids=EXPECTED_DIALOGUE,cue_budgets_sec=BUDGETS)

    def test_measured_timing_requires_hash_bound_evidence(self):
        bad=copy.deepcopy(BUNDLE)
        bad["lines"][0]["timing_measurements"]["en"]["evidence_sha256"]=None
        with self.assertRaisesRegex(LocalizationError,"evidence hash invalid"):
            validate_localization_bundle(bad,expected_dialogue_ids=EXPECTED_DIALOGUE,cue_budgets_sec=BUDGETS)

class ReframeTests(unittest.TestCase):
    def test_current_plan_preserves_all_shots_and_uses_no_crop_only(self):
        plan=compile_reframe_plan(SHOTS,REFRAME_POLICY,master_assets={})
        self.assertEqual(plan["status"],"READY_FOR_RENDER_BACKEND")
        self.assertEqual(len(plan["shots"]),8)
        self.assertEqual(plan["fallback_to_rerender_count"],3)
        self.assertFalse(plan["render_authorized"])
        self.assertEqual({row["shot_id"] for row in plan["shots"]},{shot["shot_id"] for shot in SHOTS})
        self.assertTrue(all(row["effective_strategy"]=="RERENDER_FROM_SPEC" for row in plan["shots"]))
        self.assertTrue(all(row["seed"]==next(s["seed"] for s in SHOTS if s["shot_id"]==row["shot_id"]) for row in plan["shots"]))

    def test_master_asset_enables_outpaint_for_preferred_shots(self):
        assets={
            shot_id:{"asset_id":"master_"+shot_id,"sha256":sha("a"),"manifest_sha256":sha("b")}
            for shot_id in ("sc01_sh02","sc01_sh04","sc01_sh05")
        }
        plan=compile_reframe_plan(SHOTS,REFRAME_POLICY,master_assets=assets)
        by_id={row["shot_id"]:row for row in plan["shots"]}
        self.assertEqual(plan["fallback_to_rerender_count"],0)
        for shot_id in assets:
            self.assertEqual(by_id[shot_id]["effective_strategy"],"OUTPAINT_FROM_MASTER")
            self.assertIsNotNone(by_id[shot_id]["source_master_asset"])

    def test_crop_only_strategy_rejected(self):
        bad=copy.deepcopy(REFRAME_POLICY)
        bad["shots"][0]["strategy"]="CROP_9X16_TO_16X9"
        with self.assertRaisesRegex(ReframePlanError,"unsupported"):
            compile_reframe_plan(SHOTS,bad,master_assets={})

    def test_reframe_policy_must_cover_all_shots(self):
        bad=copy.deepcopy(REFRAME_POLICY)
        bad["shots"]=bad["shots"][:-1]
        with self.assertRaisesRegex(ReframePlanError,"population mismatch"):
            compile_reframe_plan(SHOTS,bad,master_assets={})

if __name__=="__main__":
    unittest.main()
