import copy
import json
from pathlib import Path
import unittest

from film.story_coverage import StoryCoverageError, compile_story_shot_coverage
from film.continuity_expectations import ContinuityExpectationError, compile_continuity_expectations, diff_observed_state
from film.subtitle_layout import SubtitleLayoutError, compile_subtitle_layout

ROOT=Path(__file__).resolve().parents[2]
SCREENPLAY=json.loads((ROOT/"projects/slice01/story/screenplay.json").read_text(encoding="utf-8"))
TIMING=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/continuity.json").read_text(encoding="utf-8"))
SUB_POLICY=json.loads((ROOT/"projects/slice01/subtitles/layout_policy.json").read_text(encoding="utf-8"))

class StoryCoverageTests(unittest.TestCase):
    def test_current_coverage_is_complete(self):
        report=compile_story_shot_coverage(SCREENPLAY,TIMING,SHOTS)
        self.assertEqual(report["status"],"COMPLETE")
        self.assertEqual(report["duration_sec"],75.0)
        self.assertEqual(len(report["beat_coverage"]),6)
        self.assertEqual(len(report["shots"]),8)
        self.assertEqual(report["beat_coverage"][0]["shot_ids"],["sc01_sh01","sc01_sh02"])
        self.assertEqual(report["beat_coverage"][1]["shot_ids"],["sc01_sh03","sc01_sh04"])
        self.assertTrue(all(row["covered"] for row in report["beat_coverage"]))

    def test_shot_crossing_beat_boundary_is_blocked(self):
        bad=copy.deepcopy(TIMING)
        # sh01 remains 0..8; sh02 becomes 8..16 and therefore crosses the beat_001 boundary at 15.
        # Reduce sh03 by one second so total runtime stays 75s and the failure is specifically beat coverage.
        bad["shots"][1]["duration_sec"]=8.0
        bad["shots"][2]["duration_sec"]=9.0
        report=compile_story_shot_coverage(SCREENPLAY,bad,SHOTS)
        self.assertEqual(report["status"],"BLOCKED_COVERAGE")
        self.assertIn("shot-not-contained-by-one-beat:sc01_sh02",report["blockers"])

    def test_timing_population_mismatch_rejected(self):
        bad=copy.deepcopy(TIMING)
        bad["shots"]=bad["shots"][:-1]
        with self.assertRaisesRegex(StoryCoverageError,"population mismatch"):
            compile_story_shot_coverage(SCREENPLAY,bad,SHOTS)

class ContinuityExpectationTests(unittest.TestCase):
    def setUp(self):
        self.report=compile_continuity_expectations(LEDGER,SHOTS)
        self.by_id={row["shot_id"]:row for row in self.report["shots"]}

    def observed_from_expectation(self, shot_id):
        exp=self.by_id[shot_id]
        return {
            "shot_id":shot_id,
            "expectation_digest":exp["expectation_digest"],
            "characters":copy.deepcopy(exp["characters"]),
        }

    def test_current_expectations_cover_all_shots(self):
        self.assertEqual(self.report["status"],"EXPECTATIONS_READY_NO_VISUAL_OBSERVATIONS")
        self.assertEqual(len(self.report["shots"]),8)
        sh06=self.by_id["sc01_sh06"]
        self.assertEqual(sh06["characters"]["an"]["injuries"]["left_forearm"],"wrapped in clean white gauze")
        self.assertEqual(sh06["characters"]["linh"]["props"]["red_paper_crane"],"held in left hand")

    def test_exact_observation_matches(self):
        observed=self.observed_from_expectation("sc01_sh06")
        diff=diff_observed_state(self.by_id["sc01_sh06"],observed)
        self.assertEqual(diff["status"],"MATCH")
        self.assertEqual(diff["mismatches"],[])

    def test_old_injury_state_is_detected_as_drift_not_intentional_change(self):
        observed=self.observed_from_expectation("sc01_sh06")
        observed["characters"]["an"]["injuries"]["left_forearm"]="fresh shallow cut, small amount of blood"
        diff=diff_observed_state(self.by_id["sc01_sh06"],observed)
        self.assertEqual(diff["status"],"DRIFT")
        self.assertTrue(any(row["path"].endswith("injuries.left_forearm") for row in diff["mismatches"]))

    def test_hair_change_suggests_hair_drift_tag(self):
        observed=self.observed_from_expectation("sc01_sh03")
        observed["characters"]["an"]["identity"]["hair"]="long blond hair"
        diff=diff_observed_state(self.by_id["sc01_sh03"],observed)
        self.assertIn("HAIR_DRIFT",diff["suggested_failure_tags"])

    def test_missing_character_observation_detected(self):
        observed=self.observed_from_expectation("sc01_sh03")
        del observed["characters"]["linh"]
        diff=diff_observed_state(self.by_id["sc01_sh03"],observed)
        self.assertEqual(diff["status"],"DRIFT")
        self.assertTrue(any(row["reason"]=="MISSING_CHARACTER_OBSERVATION" for row in diff["mismatches"]))

    def test_observation_must_bind_expectation_digest(self):
        observed=self.observed_from_expectation("sc01_sh03")
        observed["expectation_digest"]="0"*64
        with self.assertRaisesRegex(ContinuityExpectationError,"digest mismatch"):
            diff_observed_state(self.by_id["sc01_sh03"],observed)

class SubtitleLayoutTests(unittest.TestCase):
    def test_all_current_aspect_language_plans_are_text_ready(self):
        for aspect in ("9:16","16:9"):
            for language in ("en","zh-CN","vi"):
                plan=compile_subtitle_layout(TIMING,SHOTS,language=language,aspect=aspect,policy=SUB_POLICY)
                self.assertEqual(plan["status"],"READY_TEXT_LAYOUT",(aspect,language,plan["blockers"]))
                self.assertEqual(plan["blockers"],[])
                self.assertEqual(len(plan["rows"]),4)
                self.assertEqual(plan["visual_collision_status"],"NOT_EVALUATED_REQUIRES_RENDERED_FRAME_QC")
                self.assertFalse(plan["render_authorized"])

    def test_overdense_text_is_blocked(self):
        shots=copy.deepcopy(SHOTS)
        shot=next(row for row in shots if row.get("dialogue_id")=="dlg_001")
        shot["dialogue"]["vi"]=" ".join(["rất"]*80)
        plan=compile_subtitle_layout(TIMING,shots,language="vi",aspect="9:16",policy=SUB_POLICY)
        self.assertEqual(plan["status"],"BLOCKED_TEXT_LAYOUT")
        self.assertTrue(any("subtitle-cps-high:dlg_001:vi" in x for x in plan["blockers"]))
        self.assertTrue(any("subtitle-too-many-lines:dlg_001:vi:9:16" in x for x in plan["blockers"]))

    def test_invalid_safe_box_rejected(self):
        policy=copy.deepcopy(SUB_POLICY)
        policy["aspects"]["9:16"]["safe_box_norm"]["y"]=0.95
        policy["aspects"]["9:16"]["safe_box_norm"]["height"]=0.2
        with self.assertRaisesRegex(SubtitleLayoutError,"exceeds frame height"):
            compile_subtitle_layout(TIMING,SHOTS,language="en",aspect="9:16",policy=policy)

    def test_aspect_plans_have_distinct_safe_boxes(self):
        vertical=compile_subtitle_layout(TIMING,SHOTS,language="en",aspect="9:16",policy=SUB_POLICY)
        horizontal=compile_subtitle_layout(TIMING,SHOTS,language="en",aspect="16:9",policy=SUB_POLICY)
        self.assertNotEqual(vertical["safe_box_norm"],horizontal["safe_box_norm"])
        self.assertLess(SUB_POLICY["aspects"]["9:16"]["max_chars_per_line"]["en"],SUB_POLICY["aspects"]["16:9"]["max_chars_per_line"]["en"])

if __name__=="__main__":
    unittest.main()
