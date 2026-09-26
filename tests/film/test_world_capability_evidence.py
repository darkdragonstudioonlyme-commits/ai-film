import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
EV=json.loads((ROOT/"run-evidence/WORLD_CAPABILITY_HISTORICAL_MEDIA_20260926.json").read_text())
LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text())
SESSION=json.loads((ROOT/"projects/slice01/runtime/gpu_session.json").read_text())


class WorldCapabilityEvidenceTests(unittest.TestCase):
    def test_historical_china_and_europe_have_image_to_motion_technical_proof(self):
        self.assertEqual(EV["status"],"PASS_TECHNICAL_PROOF_NOT_PRODUCTION_ACCEPTED")
        self.assertEqual(set(EV["profiles_proven"]),{
            "china_tang_changan_8c",
            "europe_belle_epoque_paris_1900s",
        })
        rows={r["artifact_id"]:r for r in EV["artifacts"]}
        self.assertEqual(len(rows),5)
        for artifact_id in (
            "world-tang-changan-image-v1",
            "world-paris-belle-epoque-image-v2",
            "world-tang-changan-motion-v1",
            "world-paris-belle-epoque-motion-v1",
        ):
            self.assertEqual(rows[artifact_id]["disposition"],"RETAINED_TECHNICAL_PROOF")
            self.assertEqual(rows[artifact_id]["local_sync"]["status"],"PASS_HASH_VERIFIED")

    def test_rejected_paris_v1_is_preserved_as_cost_and_evidence(self):
        rows={r["artifact_id"]:r for r in EV["artifacts"]}
        self.assertEqual(rows["world-paris-belle-epoque-image-v1"]["disposition"],"REJECTED_TEXT_ARTIFACT")
        ledger={r["cost_id"]:r for r in LEDGER["entries"]}
        rejected=ledger["world-paris-belle-epoque-image-v1-rejected"]
        self.assertEqual(rejected["category"],"COMPUTE_REJECTED_TAKE")
        self.assertAlmostEqual(rejected["amount_usd"],0.001389,places=6)

    def test_cost_accounting_includes_all_world_attempts(self):
        self.assertAlmostEqual(EV["execution_cost_usd_total"],0.072946,places=6)
        self.assertAlmostEqual(EV["retained_execution_cost_usd"],0.071557,places=6)
        self.assertEqual(len(LEDGER["entries"]),25)
        self.assertAlmostEqual(sum(float(r["amount_usd"]) for r in LEDGER["entries"]),0.455474,places=6)

    def test_capability_is_not_silently_promoted_to_production(self):
        self.assertEqual(EV["quality_status"],"TECHNICAL_PROOF_NOT_OWNER_SCORED")
        self.assertFalse(EV["selection_authorized"])
        self.assertFalse(EV["production_acceptance"])
        self.assertFalse(EV["publish_authority"])

    def test_paid_runtime_state_uses_provider_bill_and_records_idle_gate(self):
        self.assertEqual(SESSION["provider_state"],"RUNNING")
        self.assertEqual(SESSION["operational_state"],"IDLE_OWNER_REVIEW_GATE")
        self.assertAlmostEqual(SESSION["execution_cost_usd"],0.455474,places=6)
        self.assertGreaterEqual(SESSION["provider_billed_usd"],EV["provider_billed_snapshot_usd"])
        self.assertLess(SESSION["provider_billed_usd"],SESSION["budget_cap_usd"])
        self.assertEqual(SESSION["world_capability"]["generated_outputs"],5)
        self.assertEqual(SESSION["world_capability"]["synced_outputs"],5)
        self.assertEqual(SESSION["world_capability"]["unsynced_outputs"],0)
        self.assertEqual(SESSION["stop_keep_decision"],"STOP_RECOMMENDED_OWNER_ACTION_AFTER_EVIDENCE_CLOSURE")


if __name__=="__main__":
    unittest.main()