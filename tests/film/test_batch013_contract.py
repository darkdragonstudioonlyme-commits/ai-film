import copy
import json
from pathlib import Path
import unittest

from film.lipsync_plan import LipSyncPlanError, compile_lipsync_plan
from film.audio_cues import AudioCueError, validate_cue_sheet
from film.audio_mix_plan import AudioMixPlanError, compile_audio_mix_plan

ROOT=Path(__file__).resolve().parents[2]
POLICY=json.loads((ROOT/"projects/slice01/lipsync/policy.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
TIMING=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
CUES=json.loads((ROOT/"projects/slice01/audio/cue_sheet.json").read_text(encoding="utf-8"))
MIX_POLICY=json.loads((ROOT/"projects/slice01/audio/mix_policy.json").read_text(encoding="utf-8"))

def sha(ch):
    return (ch*64)[:64]

def video_assets():
    return {
        "sc01_sh03":{"asset_id":"v3","sha256":sha("a"),"manifest_sha256":sha("1")},
        "sc01_sh04":{"asset_id":"v4","sha256":sha("b"),"manifest_sha256":sha("2")},
        "sc01_sh06":{"asset_id":"v6","sha256":sha("c"),"manifest_sha256":sha("3")},
    }

def audio_assets(language):
    return {
        "dlg_001":{"asset_id":"a1","sha256":sha("d"),"manifest_sha256":sha("4"),"language":language,"duration_sec":2.0},
        "dlg_002":{"asset_id":"a2","sha256":sha("e"),"manifest_sha256":sha("5"),"language":language,"duration_sec":2.0},
        "dlg_003":{"asset_id":"a3","sha256":sha("f"),"manifest_sha256":sha("6"),"language":language,"duration_sec":2.0},
        "dlg_004":{"asset_id":"a4","sha256":sha("0"),"manifest_sha256":sha("7"),"language":language,"duration_sec":1.0},
    }

def cleared_cues():
    sheet=copy.deepcopy(CUES)
    for i,cue in enumerate(sheet["cues"]):
        cue["source_status"]="BOUND"
        cue["rights_status"]="CLEARED"
        cue["rights_ref"]="rights:test:"+cue["cue_id"]
        cue["asset"]={
            "asset_id":"cue_"+cue["cue_id"],
            "sha256":sha(hex((i+1)%16)[2:]),
            "manifest_sha256":sha(hex((i+8)%16)[2:]),
        }
    return sheet

class LipSyncPlanTests(unittest.TestCase):
    def test_policy_is_selective_three_visible_one_skipped(self):
        rows=POLICY["dialogue_shots"]
        self.assertEqual(len(rows),4)
        self.assertEqual(sum(bool(row["mouth_visible"]) for row in rows),3)
        self.assertEqual([row["dialogue_id"] for row in rows if not row["mouth_visible"]],["dlg_004"])

    def test_current_plan_is_blocked_missing_final_media(self):
        plan=compile_lipsync_plan(POLICY,SHOTS,language="en",selected_videos={},dialogue_audio={})
        self.assertEqual(plan["status"],"BLOCKED_MISSING_MEDIA")
        self.assertEqual(len(plan["requests"]),3)
        self.assertEqual(len(plan["skipped"]),1)
        self.assertFalse(plan["execution_permitted"])
        self.assertEqual(len(plan["blockers"]),6)

    def test_bound_plan_ready_but_never_execution_authorized(self):
        plan=compile_lipsync_plan(POLICY,SHOTS,language="vi",selected_videos=video_assets(),dialogue_audio=audio_assets("vi"))
        self.assertEqual(plan["status"],"READY_FOR_BACKEND_EVAL")
        self.assertEqual(plan["blockers"],[])
        self.assertFalse(plan["execution_permitted"])
        self.assertTrue(all(row["video"] and row["audio"] for row in plan["requests"]))
        self.assertEqual(plan["skipped"][0]["dialogue_id"],"dlg_004")

    def test_audio_language_mismatch_blocks(self):
        plan=compile_lipsync_plan(POLICY,SHOTS,language="zh-CN",selected_videos=video_assets(),dialogue_audio=audio_assets("en"))
        self.assertEqual(plan["status"],"BLOCKED_MISSING_MEDIA")
        self.assertTrue(any(x.startswith("audio-language-mismatch") for x in plan["blockers"]))

    def test_policy_must_cover_every_dialogue(self):
        bad=copy.deepcopy(POLICY)
        bad["dialogue_shots"]=bad["dialogue_shots"][:-1]
        with self.assertRaisesRegex(LipSyncPlanError,"population mismatch"):
            compile_lipsync_plan(bad,SHOTS,language="en",selected_videos={},dialogue_audio={})

class AudioCueTests(unittest.TestCase):
    def test_current_cues_are_timeline_valid_but_rights_asset_blocked(self):
        result=validate_cue_sheet(CUES,total_duration_sec=75.0)
        self.assertEqual(result["status"],"BLOCKED_MISSING_ASSETS_OR_RIGHTS")
        self.assertEqual(len(result["cues"]),7)
        self.assertEqual(len(result["blockers"]),14)

    def test_out_of_bounds_cue_rejected(self):
        bad=copy.deepcopy(CUES)
        bad["cues"][0]["end_sec"]=76.0
        with self.assertRaisesRegex(AudioCueError,"outside timeline"):
            validate_cue_sheet(bad,total_duration_sec=75.0)

    def test_cleared_rights_requires_evidence_ref(self):
        bad=cleared_cues()
        bad["cues"][0]["rights_ref"]=None
        result=validate_cue_sheet(bad,total_duration_sec=75.0)
        self.assertIn("rights-evidence-missing:amb_rain",result["blockers"])

    def test_fully_bound_cues_ready(self):
        result=validate_cue_sheet(cleared_cues(),total_duration_sec=75.0)
        self.assertEqual(result["status"],"READY")
        self.assertEqual(result["blockers"],[])

class AudioMixPlanTests(unittest.TestCase):
    def test_current_mix_is_blocked_and_nonexecuting(self):
        plan=compile_audio_mix_plan(TIMING,SHOTS,CUES,language="en",dialogue_assets={},target=MIX_POLICY["target"])
        self.assertEqual(plan["status"],"BLOCKED_MISSING_ASSETS_OR_RIGHTS")
        self.assertFalse(plan["execution_permitted"])
        self.assertEqual(plan["duration_sec"],75.0)
        self.assertTrue(any(x.startswith("missing-final-dialogue") for x in plan["blockers"]))
        self.assertTrue(any(x.startswith("missing-audio-asset") for x in plan["blockers"]))

    def test_complete_mix_plan_is_deterministic_but_nonexecuting(self):
        a=compile_audio_mix_plan(TIMING,SHOTS,cleared_cues(),language="en",dialogue_assets=audio_assets("en"),target=MIX_POLICY["target"])
        b=compile_audio_mix_plan(TIMING,SHOTS,cleared_cues(),language="en",dialogue_assets=audio_assets("en"),target=MIX_POLICY["target"])
        self.assertEqual(a,b)
        self.assertEqual(a["status"],"READY_TO_MIX")
        self.assertEqual(a["blockers"],[])
        self.assertFalse(a["execution_permitted"])
        self.assertEqual(len(a["plan_digest"]),64)

    def test_dialogue_over_budget_blocks(self):
        audio=audio_assets("en")
        audio["dlg_004"]["duration_sec"]=9.0
        plan=compile_audio_mix_plan(TIMING,SHOTS,cleared_cues(),language="en",dialogue_assets=audio,target=MIX_POLICY["target"])
        self.assertIn("dialogue-over-budget:dlg_004",plan["blockers"])

    def test_language_mismatch_blocks(self):
        plan=compile_audio_mix_plan(TIMING,SHOTS,cleared_cues(),language="zh-CN",dialogue_assets=audio_assets("en"),target=MIX_POLICY["target"])
        self.assertTrue(any(x.startswith("dialogue-language-mismatch") for x in plan["blockers"]))

if __name__=="__main__":
    unittest.main()
