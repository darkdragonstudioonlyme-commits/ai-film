import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BASE_LOCK_PATH=ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.json"
REQ_PATH=ROOT/"model-evaluations/slice01/gpu-worker/requirements-base.lock.txt"
LIVE_LOCK_PATH=ROOT/"model-evaluations/slice01/gpu-worker/runtime_lock.runpod_a40.json"
LIVE_REQ_PATH=ROOT/"model-evaluations/slice01/gpu-worker/requirements-runpod-a40.lock.txt"
RESOLVER=ROOT/"run-evidence/RUNPOD_A40_RUNTIME_RESOLVER_20260925.json"
WORKER=ROOT/"run-evidence/GPU_WORKER_DRYRUN_20260925.json"
PRELAUNCH=ROOT/"run-evidence/GPU_PRELAUNCH_BUNDLE_20260925.json"


class RunPodA40RuntimeLockTests(unittest.TestCase):
    def test_base_lock_uses_resolver_compatible_hf_hub(self):
        runtime=json.loads(BASE_LOCK_PATH.read_text(encoding="utf-8"))
        req=REQ_PATH.read_text(encoding="utf-8")
        self.assertEqual(runtime["packages"]["huggingface-hub"],"1.33.0")
        self.assertIn("huggingface-hub==1.33.0",req)
        self.assertNotIn("huggingface-hub==2.0.0",req)
        self.assertEqual(runtime["dependency_resolution"]["status"],"PASS_AFTER_HF_HUB_PIN_CORRECTION")

    def test_live_a40_lock_binds_existing_torch_without_claiming_execution_ready(self):
        live=json.loads(LIVE_LOCK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(live["status"],"RUNPOD_A40_HOST_BOUND_RUNTIME")
        self.assertFalse(live["execution_ready"])
        self.assertEqual(live["target"]["gpu"],"NVIDIA A40")
        self.assertEqual(live["target"]["torch"],"2.8.0+cu128")
        self.assertEqual(live["target"]["torch_cuda"],"12.8")
        self.assertEqual(live["packages"]["huggingface-hub"],"1.33.0")
        self.assertIn("diffusers==0.40.0",LIVE_REQ_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("torch==",LIVE_REQ_PATH.read_text(encoding="utf-8"))

    def test_resolver_evidence_preserves_failed_and_successful_resolution(self):
        evidence=json.loads(RESOLVER.read_text(encoding="utf-8"))
        self.assertEqual(evidence["status"],"PASS")
        self.assertFalse(evidence["torch_reinstall_attempted"])
        self.assertIn("huggingface-hub==2.0.0",evidence["failed_resolution"]["requirements"])
        self.assertEqual(evidence["successful_dry_run"]["resolver_selected_huggingface_hub"],"1.33.0")

    def test_regenerated_worker_hashes_bind_corrected_locks(self):
        worker=json.loads(WORKER.read_text(encoding="utf-8"))
        self.assertEqual(worker["requirements_lock_sha256"],hashlib.sha256(REQ_PATH.read_bytes()).hexdigest())
        self.assertEqual(worker["runtime_lock_sha256"],hashlib.sha256(BASE_LOCK_PATH.read_bytes()).hexdigest())
        self.assertFalse(worker["execution_ready"])

    def test_prelaunch_bundle_uses_corrected_hf_hub_and_hashes(self):
        pre=json.loads(PRELAUNCH.read_text(encoding="utf-8"))
        self.assertEqual(pre["base_runtime"]["packages"]["huggingface-hub"],"1.33.0")
        self.assertEqual(pre["base_runtime"]["requirements_lock_sha256"],hashlib.sha256(REQ_PATH.read_bytes()).hexdigest())
        self.assertEqual(pre["base_runtime"]["runtime_lock_sha256"],hashlib.sha256(BASE_LOCK_PATH.read_bytes()).hexdigest())
        self.assertFalse(pre["execution_ready"])


if __name__=="__main__":
    unittest.main()
