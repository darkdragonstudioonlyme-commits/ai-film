import json
from pathlib import Path
import unittest

from film.admission import evaluate_admission
from film.cost_ledger import budget_decision
from film.launch_gate import LaunchGateError, digest, validate_launch_authorization

ROOT=Path(__file__).resolve().parents[2]
PROPOSAL=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_PROPOSAL_2026-09-24.json").read_text(encoding="utf-8"))
PLAN=json.loads((ROOT/"model-evaluations/slice01/GPU_RENTAL_EXECUTION_PLAN_20260925.json").read_text(encoding="utf-8"))
RATES=json.loads((ROOT/"model-evaluations/slice01/rate_snapshot_20260925.json").read_text(encoding="utf-8"))
ACTIVE=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.active.json").read_text(encoding="utf-8"))
PLACEHOLDER=json.loads((ROOT/"model-evaluations/slice01/launch_authorization.placeholder.json").read_text(encoding="utf-8"))
HOST=json.loads((ROOT/"run-evidence/RUNPOD_A40_HOST_20260925.json").read_text(encoding="utf-8"))
WORKER=json.loads((ROOT/"projects/slice01/runtime/worker_runpod_a40.json").read_text(encoding="utf-8"))
RESOURCES=json.loads((ROOT/"model-evaluations/slice01/resource_profiles.json").read_text(encoding="utf-8"))
COST_POLICY=json.loads((ROOT/"projects/slice01/runtime/cost_policy.json").read_text(encoding="utf-8"))
COST_LEDGER=json.loads((ROOT/"projects/slice01/runtime/cost_ledger.json").read_text(encoding="utf-8"))
READINESS=json.loads((ROOT/"projects/slice01/readiness/stage_readiness.json").read_text(encoding="utf-8"))


class RunPodA40LiveAuthorityTests(unittest.TestCase):
    def test_active_receipt_validates_exact_a40_60_cap(self):
        result=validate_launch_authorization(
            ACTIVE,
            proposal_digest=digest(PROPOSAL),
            rate_snapshot=RATES,
            requested_gpu="NVIDIA A40",
            requested_max_usd=60.0,
        )
        self.assertTrue(result["launch_permitted"])
        self.assertEqual(result["rate_usd_per_hour"],0.49)
        self.assertEqual(result["max_total_usd"],60.0)
        self.assertEqual(ACTIVE["execution_plan_digest"],PLAN["plan_digest"])
        self.assertFalse(ACTIVE["new_resource_creation_authorized"])
        self.assertFalse(ACTIVE["publish_authority"])

    def test_active_receipt_rejects_over_cap(self):
        with self.assertRaisesRegex(LaunchGateError,"exceeds authorization"):
            validate_launch_authorization(
                ACTIVE,
                proposal_digest=digest(PROPOSAL),
                rate_snapshot=RATES,
                requested_gpu="NVIDIA A40",
                requested_max_usd=60.01,
            )

    def test_historical_placeholder_remains_blocked(self):
        with self.assertRaisesRegex(LaunchGateError,"not explicitly authorized"):
            validate_launch_authorization(
                PLACEHOLDER,
                proposal_digest=digest(PROPOSAL),
                rate_snapshot=RATES,
                requested_gpu="RTX 5090",
                requested_max_usd=60.0,
            )

    def test_host_evidence_is_exact_live_a40_stack(self):
        self.assertEqual(HOST["pod_id"],"0h1twwxqw6yx0k")
        self.assertEqual(HOST["gpu"]["name"],"NVIDIA A40")
        self.assertEqual(HOST["gpu"]["memory_total_mib"],46068)
        self.assertEqual(HOST["gpu"]["driver_version"],"580.159.03")
        self.assertEqual(HOST["torch_version"],"2.8.0+cu128")
        self.assertEqual(HOST["torch_cuda_version"],"12.8")
        self.assertTrue(HOST["torch_cuda_available"])
        self.assertEqual(HOST["cgroup"]["cpu_quota_cores"],7.65)
        self.assertEqual(HOST["cgroup"]["memory_max_bytes"],49999998976)
        self.assertEqual(HOST["storage"]["disk_bytes_total"],268435456000)

    def test_measured_worker_is_ready_as_host_but_profiles_stay_fail_closed(self):
        profile=next(row for row in RESOURCES["profiles"] if row["profile_id"]=="model-flux2-klein-4b")
        decision=evaluate_admission(profile,WORKER)
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])
        self.assertEqual(WORKER["vram_status"],"MEASURED")
        self.assertEqual(WORKER["runtime_status"],"BASE_RUNTIME_MEASURED_FLUX2_ZIMAGE_VOXCPM2_PASS_VIDEO_PENDING")

    def test_cost_policy_and_bootstrap_estimate_enforce_60_cap(self):
        self.assertEqual(COST_POLICY["status"],"AUTHORIZED_BOUNDED")
        self.assertEqual(COST_POLICY["current_authorized_budget_usd"],60.0)
        self.assertEqual(len(COST_LEDGER["entries"]),17)
        by_id={row["cost_id"]:row for row in COST_LEDGER["entries"]}
        self.assertAlmostEqual(by_id["runpod-a40-bootstrap-estimate-20260925"]["amount_usd"],0.11027,places=6)
        self.assertAlmostEqual(by_id["flux2-castjob_d3ec86da4ca6b1fc-pass"]["amount_usd"],0.00138,places=6)
        self.assertAlmostEqual(by_id["flux2-formal-smoke-20260925"]["amount_usd"],0.0021,places=6)
        self.assertAlmostEqual(by_id["zimage-castjob_8e02916e0db64eb6-pass"]["amount_usd"],0.004647,places=6)
        self.assertAlmostEqual(by_id["zimage-formal-smoke-20260926"]["amount_usd"],0.048111,places=6)
        self.assertAlmostEqual(by_id["voxcpm2-voxreq_7f50b3325b6132e8-pass"]["amount_usd"],0.004291,places=6)
        self.assertAlmostEqual(sum(float(row["amount_usd"]) for row in COST_LEDGER["entries"]),0.27329,places=6)
        ok=budget_decision(COST_LEDGER,budget_usd=60.0,proposed_charge_usd=59.7267)
        self.assertTrue(ok["allowed"])
        blocked=budget_decision(COST_LEDGER,budget_usd=60.0,proposed_charge_usd=59.727)
        self.assertFalse(blocked["allowed"])

    def test_resource_profiles_record_a40_host_without_fake_model_measurements(self):
        tier=next(row for row in RESOURCES["worker_tiers"] if row["tier"]=="RUNPOD_A40_48GB")
        self.assertEqual(tier["measured_vram_mib"],46068)
        self.assertEqual(tier["measurement_status"],"HOST_MEASURED_MODEL_STACK_UNMEASURED")
        flux=next(row for row in RESOURCES["profiles"] if row["model_id"]=="flux2-klein-4b")
        zimg=next(row for row in RESOURCES["profiles"] if row["model_id"]=="z-image")
        others=[row for row in RESOURCES["profiles"] if row["model_id"] not in {"flux2-klein-4b","z-image"}]
        self.assertEqual(flux["vram_status"],"MEASURED")
        self.assertEqual(flux["formal_smoke_peak_nvidia_mib"],20415)
        self.assertTrue(flux["admission_ready"])
        self.assertEqual(flux["required_vram_gb"],20.0)
        self.assertEqual(flux["vram_reserve_gb"],4.0)
        self.assertEqual(zimg["vram_status"],"MEASURED")
        self.assertEqual(zimg["qualification_peak_vram_mib"],21913.0)
        self.assertEqual(zimg["formal_smoke_peak_nvidia_mib"],26227)
        self.assertEqual(zimg["formal_smoke_peak_torch_mib"],25892.0)
        self.assertTrue(zimg["admission_ready"])
        self.assertEqual(zimg["required_vram_gb"],26.0)
        self.assertEqual(zimg["vram_reserve_gb"],4.0)
        self.assertTrue(all(row["vram_status"]=="UNMEASURED" for row in others))
        self.assertTrue(all(row["admission_ready"] is False for row in others))

    def test_readiness_opens_only_casting_and_voice_without_auto_execution(self):
        self.assertEqual(READINESS["status"],"HAS_RUNNABLE_STAGE")
        self.assertEqual(set(READINESS["ready_stages"]),{"casting_reference_generation","voice_eval"})
        self.assertTrue(READINESS["evidence"]["paid_gpu_authorized"])
        self.assertFalse(READINESS["execution_permitted"])
        by={row["stage_id"]:row for row in READINESS["stages"]}
        self.assertEqual(by["casting_reference_generation"]["status"],"READY")
        self.assertEqual(by["voice_eval"]["status"],"READY")
        self.assertFalse(by["casting_reference_generation"]["execution_permitted"])
        self.assertFalse(by["voice_eval"]["execution_permitted"])


if __name__=="__main__":
    unittest.main()
