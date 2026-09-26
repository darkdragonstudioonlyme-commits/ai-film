import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BLIND=json.loads((ROOT/"projects/slice01/casting/formal_comparison/blind_items.json").read_text(encoding="utf-8"))
BLIND_EV=json.loads((ROOT/"run-evidence/IMAGE_MODEL_BLIND_MATERIALIZATION_20260926.json").read_text(encoding="utf-8"))
VOX_EV=json.loads((ROOT/"run-evidence/VOXCPM2_A40_QUALIFICATION_20260926.json").read_text(encoding="utf-8"))
VOICE_PROFILES=json.loads((ROOT/"model-evaluations/slice01/voice/resource_profiles.json").read_text(encoding="utf-8"))
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
VOX_BATCH=json.loads((ROOT/"run-evidence/VOXCPM2_FORMAL_BATCH_20260926.json").read_text(encoding="utf-8"))


class VoxCPM2QualificationEvidenceTests(unittest.TestCase):
    def test_blind_materialization_is_eight_verified_neutral_copies(self):
        self.assertEqual(BLIND_EV["status"],"PASS_8_NEUTRAL_COPIES_VERIFIED")
        self.assertEqual(BLIND_EV["sample_count"],8)
        self.assertFalse(BLIND_EV["manifest"]["model_identity_in_manifest"])
        self.assertEqual(
            BLIND_EV["manifest"]["sha256"],
            "2dbc18d0f9ebc56024980b864a7fc27d6633a18ed9741049f851404512fe2728",
        )
        self.assertTrue(all(row["verified"] for row in BLIND_EV["items"]))

    def test_public_blind_packet_has_neutral_paths_without_model_identity(self):
        self.assertEqual(len(BLIND["items"]),8)
        for row in BLIND["items"]:
            self.assertEqual(row["asset_locator_status"],"POD_LOCAL_NEUTRAL_COPY_VERIFIED")
            self.assertEqual(
                row["pod_neutral_path"],
                f"/workspace/artifacts/blind-comparison/{row['blind_id']}.png",
            )
            for forbidden in ("model_id","model_revision","job_id","source_blind_id"):
                self.assertNotIn(forbidden,row)
        self.assertFalse(BLIND["selection_authorized"])

    def test_voxcpm2_single_sample_qualification_is_hash_bound_and_cue_fit(self):
        self.assertEqual(VOX_EV["status"],"PASS_SINGLE_SAMPLE_RUNTIME_QUALIFICATION")
        self.assertEqual(VOX_EV["request"]["request_id"],"voxreq_7f50b3325b6132e8")
        self.assertEqual(VOX_EV["request"]["language"],"en")
        self.assertEqual(VOX_EV["request"]["reference_audio"],None)
        self.assertFalse(VOX_EV["request"]["voice_cloning"])
        self.assertEqual(VOX_EV["measurements"]["gpu_peak_memory_mib"],5827.0)
        self.assertAlmostEqual(VOX_EV["measurements"]["inference_sec"],3.452767,places=6)
        self.assertAlmostEqual(VOX_EV["measurements"]["elapsed_sec"],31.527109,places=6)
        self.assertEqual(VOX_EV["output"]["duration_sec"],3.04)
        self.assertTrue(VOX_EV["output"]["cue_fit"])
        self.assertEqual(
            VOX_EV["output"]["sha256"],
            "f562abbb391460d4cda9f75c0930bfe8ccb603257fd971b6a8a19a33544d3940",
        )
        self.assertEqual(VOX_EV["quality_status"],"NOT_EVALUATED")
        self.assertFalse(VOX_EV["production_acceptance"])

    def test_voice_resource_profile_is_admission_ready_but_quality_pending(self):
        self.assertEqual(
            VOICE_PROFILES["status"],
            "VOXCPM2_FORMAL_PACKET_MEASURED_QUALITY_PENDING",
        )
        profile=VOICE_PROFILES["profiles"][0]
        self.assertEqual(profile["model_id"],"voxcpm2")
        self.assertEqual(profile["required_vram_gb"],6.0)
        self.assertEqual(profile["vram_reserve_gb"],4.0)
        self.assertEqual(profile["admission_threshold_gb"],10.0)
        self.assertTrue(profile["admission_ready"])
        self.assertEqual(profile["formal_packet_status"],"PASS_RUNTIME_12_SAMPLES_CUE_FIT_10_12")
        self.assertEqual(profile["quality_status"],"AWAITING_OWNER_SCORING")
        self.assertFalse(profile["production_acceptance"])

    def test_formal_batch_is_12_runtime_pass_with_two_cue_fit_failures(self):
        self.assertEqual(VOX_BATCH["sample_count"],12)
        self.assertEqual(VOX_BATCH["pass_runtime"],12)
        self.assertEqual(VOX_BATCH["cue_fit_pass"],10)
        self.assertEqual(VOX_BATCH["cue_fit_fail"],2)
        self.assertTrue(VOX_BATCH["all_media_synced_and_hash_verified"])
        self.assertEqual({row["language"] for row in VOX_BATCH["cue_fit_failures"]},{"zh-CN"})
        self.assertEqual(VOX_BATCH["quality_status"],"AWAITING_OWNER_SCORING")
        self.assertFalse(VOX_BATCH["production_acceptance"])

    def test_cost_ledger_includes_voxcpm2_qualification_once(self):
        rows=[row for row in LEDGER["entries"] if row["cost_id"]=="voxcpm2-voxreq_7f50b3325b6132e8-pass"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["category"],"COMPUTE_ACCEPTED")
        self.assertEqual(rows[0]["logical_key"],"T-019-VOXCPM2-QUALIFICATION")
        self.assertAlmostEqual(rows[0]["amount_usd"],0.004291,places=6)
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in LEDGER["entries"]),0.455474,places=6)


if __name__=="__main__":
    unittest.main()