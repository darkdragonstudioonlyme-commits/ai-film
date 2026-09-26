import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.scored_media_promotion import (
    ScoredMediaPromotionError,
    build_scored_benchmark_plan,
)

ROOT=Path(__file__).resolve().parents[2]
SHOT_IDS=[
    row["shot_id"]
    for row in json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text())
]


def summary(motion_a=6,motion_b=4):
    voice_rows=[]
    for i in range(12):
        voice_rows.append({
            "kind":"voice",
            "id":f"vox_{i:02d}",
            "score":4+(i%3),
            "notes":"",
            "character_id":"an" if i<6 else "linh",
            "language":("en","zh-CN","vi")[i%3],
            "dialogue_id":f"dlg_{1+(i//3):03d}",
            "target_text":"x",
        })
    scores=[r["score"] for r in voice_rows]
    return {
        "schema_version":1,
        "review_id":"owner-review-test",
        "scale":{"min":0,"max":8},
        "score_set_complete":True,
        "voice":{
            "sample_count":12,
            "overall_mean":sum(scores)/len(scores),
            "by_character":{
                "an":{"sample_count":6,"total":30,"mean":5.0},
                "linh":{"sample_count":6,"total":30,"mean":5.0},
            },
            "by_language":{
                "en":{"sample_count":4,"total":20,"mean":5.0},
                "zh-CN":{"sample_count":4,"total":20,"mean":5.0},
                "vi":{"sample_count":4,"total":20,"mean":5.0},
            },
            "rows":voice_rows,
        },
        "motion":{
            "sample_count":2,
            "rows":[
                {"kind":"motion","id":"motion_A","score":motion_a,"notes":"","reference_model_id":"flux2-klein-4b"},
                {"kind":"motion","id":"motion_B","score":motion_b,"notes":"","reference_model_id":"z-image"},
            ],
            "selection_authorized":False,
            "production_acceptance":False,
        },
        "quality_status":"OWNER_SCORED_NOT_PRODUCTION_ACCEPTED",
        "selection_authorized":False,
        "production_acceptance":False,
    }


class ScoredMediaPromotionTests(unittest.TestCase):
    def test_unique_owner_motion_top_score_is_benchmark_ready_not_production_accepted(self):
        plan=build_scored_benchmark_plan(summary(),benchmark_shot_ids=SHOT_IDS)
        self.assertEqual(plan["status"],"READY_FOR_MULTI_SHOT_BENCHMARK_CONFIGURATION")
        self.assertEqual(plan["motion"]["selected_reference_model_id"],"flux2-klein-4b")
        self.assertEqual(plan["motion"]["selected_motion_id"],"motion_A")
        self.assertTrue(plan["selection_authorized"])
        self.assertFalse(plan["production_acceptance"])
        self.assertFalse(plan["publish_authority"])
        self.assertEqual(plan["benchmark_shot_ids"],SHOT_IDS)

    def test_motion_score_tie_blocks_promotion_without_guessing(self):
        plan=build_scored_benchmark_plan(summary(5,5),benchmark_shot_ids=SHOT_IDS)
        self.assertEqual(plan["status"],"BLOCKED_OWNER_MOTION_TIE")
        self.assertEqual(plan["motion"]["status"],"BLOCKED_MOTION_SCORE_TIE")
        self.assertIsNone(plan["motion"]["selected_reference_model_id"])
        self.assertFalse(plan["selection_authorized"])
        self.assertFalse(plan["production_acceptance"])

    def test_incomplete_or_accepting_owner_summary_fails_closed(self):
        bad=summary(); bad["score_set_complete"]=False
        with self.assertRaisesRegex(ScoredMediaPromotionError,"incomplete"):
            build_scored_benchmark_plan(bad,benchmark_shot_ids=SHOT_IDS)
        bad=summary(); bad["production_acceptance"]=True
        with self.assertRaisesRegex(ScoredMediaPromotionError,"must not grant"):
            build_scored_benchmark_plan(bad,benchmark_shot_ids=SHOT_IDS)

    def test_invalid_benchmark_shot_population_fails(self):
        with self.assertRaisesRegex(ScoredMediaPromotionError,"benchmark_shot_ids"):
            build_scored_benchmark_plan(summary(),benchmark_shot_ids=["a","a"])

    def test_cli_writes_plan_and_preserves_non_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            owner=td/"owner.json"; owner.write_text(json.dumps(summary()))
            out=td/"plan.json"
            proc=subprocess.run([
                sys.executable,str(ROOT/"tools/build_scored_benchmark_plan.py"),
                "--owner-summary",str(owner),"--out",str(out)
            ],cwd=ROOT,text=True,capture_output=True,check=False)
            self.assertEqual(proc.returncode,0,proc.stderr)
            plan=json.loads(out.read_text())
            self.assertEqual(plan["status"],"READY_FOR_MULTI_SHOT_BENCHMARK_CONFIGURATION")
            self.assertFalse(plan["production_acceptance"])
            self.assertFalse(plan["publish_authority"])


if __name__=="__main__":
    unittest.main()