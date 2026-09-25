import copy
import json
from pathlib import Path
import unittest

from film.adapters import AdapterError, compile_backend_request
from film.benchmark import build_jobs, file_sha256, resolve_requirements

ROOT=Path(__file__).resolve().parents[2]
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
PLAN=json.loads((ROOT/"model-evaluations/slice01/benchmark_plan.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))
PROMPT_HASHES={s["shot_id"]:file_sha256(ROOT/"projects/slice01/compiled"/f"{s['shot_id']}.json") for s in SHOTS}


class AdapterTests(unittest.TestCase):
    def test_image_request_is_deterministic_and_non_executing(self):
        jobs=build_jobs(MATRIX,PLAN,SHOTS,profile_name="smoke",only_models={"z-image"},prompt_hashes=PROMPT_HASHES)
        job=resolve_requirements(jobs[0],None)
        a=compile_backend_request(job,MATRIX,ROOT)
        b=compile_backend_request(job,MATRIX,ROOT)
        self.assertEqual(a,b)
        self.assertEqual(a["model"]["pipeline"],"ZImagePipeline")
        self.assertFalse(a["execution_permitted"])
        self.assertEqual(len(a["request_digest"]),64)

    def test_video_request_rejects_missing_reference(self):
        jobs=build_jobs(MATRIX,PLAN,SHOTS,profile_name="video_core",only_models={"wan22-ti2v-5b"},prompt_hashes=PROMPT_HASHES)
        job=resolve_requirements(jobs[0],None)
        with self.assertRaisesRegex(AdapterError,"missing requirements"):
            compile_backend_request(job,MATRIX,ROOT)

    def test_video_request_accepts_resolved_reference_contract(self):
        jobs=build_jobs(MATRIX,PLAN,SHOTS,profile_name="video_core",only_models={"wan22-ti2v-5b"},prompt_hashes=PROMPT_HASHES)
        job=resolve_requirements(jobs[0],{"shots":{jobs[0]["shot_id"]:{"reference_image":"refs/keyframe.png"}}})
        request=compile_backend_request(job,MATRIX,ROOT)
        self.assertEqual(request["references"]["reference_image"],"refs/keyframe.png")
        self.assertFalse(request["execution_permitted"])

    def test_prompt_digest_tamper_is_rejected(self):
        jobs=build_jobs(MATRIX,PLAN,SHOTS,profile_name="smoke",only_models={"flux2-klein-4b"},prompt_hashes=PROMPT_HASHES)
        job=resolve_requirements(jobs[0],None)
        job["prompt_sha256"]="0"*64
        with self.assertRaisesRegex(AdapterError,"digest mismatch"):
            compile_backend_request(job,MATRIX,ROOT)

    def test_disabled_qwen_is_rejected(self):
        jobs=build_jobs(MATRIX,PLAN,SHOTS,profile_name="smoke",only_models={"z-image"},prompt_hashes=PROMPT_HASHES)
        job=resolve_requirements(jobs[0],None)
        job=copy.deepcopy(job)
        job["model"]["model_id"]="qwen-image-2.1"
        with self.assertRaisesRegex(AdapterError,"disabled"):
            compile_backend_request(job,MATRIX,ROOT)


if __name__=="__main__":
    unittest.main()
