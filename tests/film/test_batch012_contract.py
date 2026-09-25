import copy
import json
from pathlib import Path
import tempfile
import unittest

from film.admission import evaluate_admission
from film.queue_control import QueueControlError, cancel_job, dispatch_next, enqueue_job, new_queue, queue_status
from film.cost_ledger import CostLedgerError, append_cost, budget_decision, new_ledger, summarize_costs

ROOT=Path(__file__).resolve().parents[2]


class AdmissionTests(unittest.TestCase):
    def worker(self,**overrides):
        row={
            "worker_id":"w1",
            "capabilities":["image_generation","cuda"],
            "runtime_ids":["gpu-worker-base-v1"],
            "vram_status":"MEASURED",
            "available_vram_gb":32.0,
            "quarantined":False,
        }
        row.update(overrides)
        return row

    def measured_profile(self,**overrides):
        row={
            "profile_id":"image-z",
            "admission_ready":True,
            "vram_status":"MEASURED",
            "required_vram_gb":28.0,
            "vram_reserve_gb":2.0,
            "required_capabilities":["image_generation","cuda"],
            "required_runtime_id":"gpu-worker-base-v1",
        }
        row.update(overrides)
        return row

    def test_measured_profile_admits_compatible_worker(self):
        decision=evaluate_admission(self.measured_profile(),self.worker())
        self.assertTrue(decision["admitted"])
        self.assertEqual(decision["reasons"],[])
        self.assertFalse(decision["throughput_claimed"])
        self.assertIsNone(decision["measured_throughput"])

    def test_unmeasured_profile_rejected_even_on_96gb_worker(self):
        profile=self.measured_profile(
            admission_ready=False,
            vram_status="UNMEASURED",
            required_vram_gb=None,
        )
        worker=self.worker(available_vram_gb=96.0)
        decision=evaluate_admission(profile,worker)
        self.assertFalse(decision["admitted"])
        self.assertIn("PROFILE_NOT_ADMISSION_READY",decision["reasons"])
        self.assertIn("VRAM_REQUIREMENT_UNMEASURED",decision["reasons"])
        self.assertIn("VRAM_REQUIREMENT_MISSING",decision["reasons"])

    def test_runtime_capability_and_vram_fail_closed(self):
        decision=evaluate_admission(
            self.measured_profile(required_vram_gb=31,vram_reserve_gb=2,required_runtime_id="runtime-x",required_capabilities=["image_generation","cuda","special"]),
            self.worker(),
        )
        self.assertFalse(decision["admitted"])
        self.assertTrue(any(x.startswith("INSUFFICIENT_VRAM") for x in decision["reasons"]))
        self.assertTrue(any(x.startswith("MISSING_CAPABILITIES") for x in decision["reasons"]))
        self.assertTrue(any(x.startswith("RUNTIME_MISMATCH") for x in decision["reasons"]))

    def test_quarantined_worker_rejected(self):
        self.assertIn("WORKER_QUARANTINED",evaluate_admission(self.measured_profile(),self.worker(quarantined=True))["reasons"])


class QueueTests(unittest.TestCase):
    def profiles(self):
        return {
            "blocked":{
                "profile_id":"blocked","admission_ready":False,"vram_status":"UNMEASURED","required_vram_gb":None,
                "required_capabilities":["image_generation"],"required_runtime_id":"gpu-worker-base-v1",
            },
            "ready":{
                "profile_id":"ready","admission_ready":True,"vram_status":"MEASURED","required_vram_gb":8.0,"vram_reserve_gb":1.0,
                "required_capabilities":["image_generation"],"required_runtime_id":"gpu-worker-base-v1",
            },
        }

    def worker(self):
        return {
            "worker_id":"w1","capabilities":["image_generation"],"runtime_ids":["gpu-worker-base-v1"],
            "vram_status":"MEASURED","available_vram_gb":16.0,"quarantined":False,
        }

    def test_max_depth_backpressure(self):
        q=new_queue(max_depth=2,per_project_concurrency=1)
        q=enqueue_job(q,job_id="j1",project_id="p1",admission_profile_id="ready")
        q=enqueue_job(q,job_id="j2",project_id="p2",admission_profile_id="ready")
        with self.assertRaisesRegex(QueueControlError,"QUEUE_BACKPRESSURE_MAX_DEPTH"):
            enqueue_job(q,job_id="j3",project_id="p3",admission_profile_id="ready")

    def test_incompatible_head_does_not_starve_compatible_later_job(self):
        q=new_queue(max_depth=4,per_project_concurrency=1)
        q=enqueue_job(q,job_id="j1",project_id="p1",admission_profile_id="blocked")
        q=enqueue_job(q,job_id="j2",project_id="p2",admission_profile_id="ready")
        q,dispatched,blocked=dispatch_next(q,worker=self.worker(),admission_profiles=self.profiles(),active_by_project={})
        self.assertEqual(dispatched["job_id"],"j2")
        self.assertEqual(blocked[0]["job_id"],"j1")
        self.assertEqual(blocked[0]["reason"],"ADMISSION_REJECTED")
        self.assertEqual(queue_status(q)["queued_job_ids"],["j1"])

    def test_project_concurrency_skip_is_visible_and_later_project_dispatches(self):
        q=new_queue(max_depth=4,per_project_concurrency=1)
        q=enqueue_job(q,job_id="j1",project_id="p1",admission_profile_id="ready")
        q=enqueue_job(q,job_id="j2",project_id="p2",admission_profile_id="ready")
        q,dispatched,blocked=dispatch_next(q,worker=self.worker(),admission_profiles=self.profiles(),active_by_project={"p1":1})
        self.assertEqual(dispatched["job_id"],"j2")
        self.assertEqual(blocked,[{"job_id":"j1","reason":"PROJECT_CONCURRENCY_LIMIT"}])

    def test_cancelled_queued_job_is_not_dispatched(self):
        q=new_queue(max_depth=3,per_project_concurrency=1)
        q=enqueue_job(q,job_id="j1",project_id="p1",admission_profile_id="ready")
        q=cancel_job(q,"j1")
        q,dispatched,blocked=dispatch_next(q,worker=self.worker(),admission_profiles=self.profiles(),active_by_project={})
        self.assertIsNone(dispatched)
        self.assertEqual(queue_status(q)["counts"]["CANCELLED"],1)


class CostLedgerTests(unittest.TestCase):
    def ledger(self):
        ledger=new_ledger("slice01")
        entries=[
            ("c1","COMPUTE_ACCEPTED",2.0),
            ("c2","COMPUTE_FAILED",1.0),
            ("c3","COMPUTE_REJECTED_TAKE",0.5),
            ("c4","STORAGE",0.25),
            ("c5","TRANSFER",0.1),
            ("c6","API",0.2),
        ]
        for cid,cat,amount in entries:
            ledger=append_cost(ledger,cost_id=cid,category=cat,amount_usd=amount,logical_key="job1")
        return ledger

    def test_all_cost_categories_counted(self):
        summary=summarize_costs(self.ledger())
        self.assertEqual(summary["total_usd"],4.05)
        self.assertEqual(summary["by_category"]["COMPUTE_FAILED"],1.0)
        self.assertEqual(summary["by_category"]["COMPUTE_REJECTED_TAKE"],0.5)
        self.assertEqual(summary["by_category"]["STORAGE"],0.25)
        self.assertEqual(summary["by_category"]["TRANSFER"],0.1)
        self.assertEqual(summary["by_logical_key"]["job1"],4.05)

    def test_budget_guard_includes_failed_and_noncompute_cost(self):
        ledger=self.ledger()
        ok=budget_decision(ledger,budget_usd=5.0,proposed_charge_usd=0.9)
        self.assertTrue(ok["allowed"])
        blocked=budget_decision(ledger,budget_usd=5.0,proposed_charge_usd=1.0)
        self.assertFalse(blocked["allowed"])
        self.assertTrue(blocked["all_cost_categories_counted"])

    def test_duplicate_cost_receipt_rejected(self):
        ledger=new_ledger("slice01")
        ledger=append_cost(ledger,cost_id="same",category="STORAGE",amount_usd=1)
        with self.assertRaisesRegex(CostLedgerError,"duplicate cost_id"):
            append_cost(ledger,cost_id="same",category="TRANSFER",amount_usd=1)


if __name__=="__main__":
    unittest.main()
