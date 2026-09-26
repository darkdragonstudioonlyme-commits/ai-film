import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CAT=json.loads((ROOT/"projects/slice01/audio/rough_cut_voice_candidates.json").read_text())


class RoughVoiceCandidateTests(unittest.TestCase):
    def test_catalog_has_ten_hash_bound_nonfinal_candidates(self):
        self.assertEqual(CAT["status"],"ROUGH_CUT_CANDIDATES_HASH_VERIFIED")
        self.assertEqual(CAT["sample_count"],10)
        self.assertFalse(CAT["production_acceptance"])
        self.assertFalse(CAT["publish_authority"])
        self.assertEqual(len(CAT["samples"]),10)
        for row in CAT["samples"]:
            self.assertEqual(len(row["sha256"]),64)
            self.assertEqual(len(row["manifest_sha256"]),64)
            self.assertEqual(row["status"],"ROUGH_CUT_CANDIDATE_ONLY")
            self.assertFalse(row["production_acceptance"])

    def test_language_population_matches_auto_shortlist(self):
        by_lang={}
        for row in CAT["samples"]:
            by_lang.setdefault(row["language"],set()).add(row["dialogue_id"])
        self.assertEqual(by_lang["en"],{"dlg_001","dlg_002","dlg_003","dlg_004"})
        self.assertEqual(by_lang["vi"],{"dlg_001","dlg_002","dlg_003","dlg_004"})
        self.assertEqual(by_lang["zh-CN"],{"dlg_002","dlg_003"})

    def test_rough_lipsync_plans_reduce_audio_blockers_without_execution_authority(self):
        for lang in ("en","vi","zh-CN"):
            plan=json.loads((ROOT/f"projects/slice01/lipsync/plan_rough_{lang}.json").read_text())
            self.assertFalse(plan["execution_permitted"])
            self.assertEqual(len(plan["requests"]),3)
            self.assertEqual(len(plan["skipped"]),1)
            video_blockers={b for b in plan["blockers"] if b.startswith("missing-video:")}
            self.assertEqual(video_blockers,{
                "missing-video:sc01_sh03",
                "missing-video:sc01_sh04",
                "missing-video:sc01_sh06",
            })
            audio_blockers={b for b in plan["blockers"] if b.startswith("missing-audio:")}
            if lang in {"en","vi"}:
                self.assertEqual(audio_blockers,set())
            else:
                self.assertEqual(audio_blockers,{"missing-audio:dlg_001:zh-CN"})


if __name__=="__main__":
    unittest.main()
