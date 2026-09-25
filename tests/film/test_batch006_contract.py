import csv
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.blind_scoring import BlindScoreError, ScoreSchema, parse_score_csv, unblind_and_rank, validate_complete_scores
from film.casting_jobs import compile_casting_jobs
from film.voice_eval import compile_voxcpm2_requests, validate_voice_output_manifest

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=json.loads((ROOT/"projects/slice01/casting/reference_contract.json").read_text(encoding="utf-8"))
MATRIX=json.loads((ROOT/"model-evaluations/slice01/model_matrix.json").read_text(encoding="utf-8"))
VOICE_CONFIG=json.loads((ROOT/"model-evaluations/slice01/voice/voxcpm2_eval_config.json").read_text(encoding="utf-8"))
VOICE_PACKET=json.loads((ROOT/"model-evaluations/slice01/voice/packet/eval_packet.json").read_text(encoding="utf-8"))

CAST_SCHEMA=ScoreSchema(criteria=(
    "identity_match",
    "within_character_consistency",
    "between_character_separation",
    "style_quality",
    "anatomy_artifact_free",
    "overall",
))


def complete_casting_csv(public_items, private_mapping):
    private_by={row["blind_id"]:row for row in private_mapping}
    out=StringIO()
    writer=csv.writer(out)
    writer.writerow(["blind_id",*CAST_SCHEMA.criteria,"failure_tags","notes"])
    for item in public_items:
        private=private_by[item["blind_id"]]
        base_score=5 if private["model_id"]=="z-image" else 4
        writer.writerow([item["blind_id"],*[base_score]*len(CAST_SCHEMA.criteria),"","synthetic-test"])
    return out.getvalue()


class Batch006Tests(unittest.TestCase):
    def test_casting_jobs_are_deterministic_and_non_executing(self):
        a=compile_casting_jobs(CONTRACT,MATRIX)
        b=compile_casting_jobs(CONTRACT,MATRIX)
        self.assertEqual(a,b)
        jobs,public,private=a
        self.assertEqual(len(jobs),32)
        self.assertEqual({row["model_id"] for row in jobs},{"z-image","flux2-klein-4b"})
        self.assertTrue(all(row["execution_permitted"] is False for row in jobs))
        self.assertEqual(len({row["job_id"] for row in jobs}),32)
        self.assertEqual(len({row["blind_id"] for row in jobs}),32)
        self.assertTrue(all(len(row["model_revision"])==40 for row in jobs))
        self.assertTrue(all("character_id" not in row and "model_id" not in row for row in public["items"]))
        self.assertTrue(all("character_id" in row and "model_id" in row for row in private["mapping"]))

    def test_casting_scores_fail_closed_when_incomplete(self):
        _,public,_=compile_casting_jobs(CONTRACT,MATRIX)
        rows=parse_score_csv("blind_id,identity_match,within_character_consistency,between_character_separation,style_quality,anatomy_artifact_free,overall,failure_tags,notes\n")
        with self.assertRaisesRegex(BlindScoreError,"population mismatch"):
            validate_complete_scores(public["items"],rows,CAST_SCHEMA)

    def test_casting_ranking_is_deterministic_after_complete_scores(self):
        _,public,private=compile_casting_jobs(CONTRACT,MATRIX)
        rows=parse_score_csv(complete_casting_csv(public["items"],private["mapping"]))
        validated=validate_complete_scores(public["items"],rows,CAST_SCHEMA)
        ranked=unblind_and_rank(validated,private["mapping"],group_fields=("model_id","style"))
        self.assertEqual(len(ranked),4)
        self.assertEqual(ranked[0]["group"]["model_id"],"z-image")
        self.assertEqual(ranked[0]["overall"],5.0)
        self.assertTrue(all(row["sample_count"]==8 for row in ranked))

    def test_casting_cli_does_not_open_private_map_before_score_completion(self):
        _,public,_=compile_casting_jobs(CONTRACT,MATRIX)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"blind_items.json").write_text(json.dumps(public),encoding="utf-8")
            (root/"scores.csv").write_text(
                "blind_id,identity_match,within_character_consistency,between_character_separation,style_quality,anatomy_artifact_free,overall,failure_tags,notes\n",
                encoding="utf-8",
            )
            (root/"blind_map_private.json").write_text("{MALFORMED",encoding="utf-8")
            proc=subprocess.run(
                [sys.executable,str(ROOT/"tools/ingest_casting_scores.py"),"--eval-dir",str(root)],
                cwd=ROOT,text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,2)
            self.assertIn("BLIND_SCORE_FAIL",proc.stderr)
            self.assertNotIn("JSONDecodeError",proc.stderr)


    def test_casting_cli_rejects_complete_scores_without_assets_before_private_map(self):
        _,public,private=compile_casting_jobs(CONTRACT,MATRIX)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"blind_items.json").write_text(json.dumps(public),encoding="utf-8")
            (root/"scores.csv").write_text(complete_casting_csv(public["items"],private["mapping"]),encoding="utf-8")
            (root/"blind_map_private.json").write_text("{MALFORMED",encoding="utf-8")
            proc=subprocess.run(
                [sys.executable,str(ROOT/"tools/ingest_casting_scores.py"),"--eval-dir",str(root)],
                cwd=ROOT,text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,2)
            self.assertIn("asset identity incomplete",proc.stderr)
            self.assertNotIn("JSONDecodeError",proc.stderr)

    def test_voxcpm2_requests_bind_exact_identity_and_no_reference_audio(self):
        requests=compile_voxcpm2_requests(VOICE_CONFIG,VOICE_PACKET)
        self.assertEqual(len(requests),12)
        self.assertTrue(all(row["execution_permitted"] is False for row in requests))
        self.assertTrue(all(row["reference_audio"] is None for row in requests))
        self.assertTrue(all(row["model"]["revision"]=="32279effe8c19989596f05d353d1447f51d9e915" for row in requests))
        self.assertTrue(all(row["model"]["package"]=="voxcpm==2.0.3" for row in requests))
        self.assertEqual({row["language"] for row in requests},{"en","zh-CN","vi"})

    def test_voxcpm2_output_manifest_binds_request_and_cue_fit(self):
        request=compile_voxcpm2_requests(VOICE_CONFIG,VOICE_PACKET)[0]
        manifest={
            "request_digest":request["request_digest"],
            "blind_id":request["blind_id"],
            "audio_sha256":"a"*64,
            "sample_rate_hz":48000,
            "duration_sec":2.0,
            "bytes":192044,
        }
        validated=validate_voice_output_manifest(request,manifest)
        self.assertTrue(validated["cue_fit"])
        bad=dict(manifest,request_digest="0"*64)
        with self.assertRaisesRegex(ValueError,"request digest mismatch"):
            validate_voice_output_manifest(request,bad)


    def test_voxcpm2_score_ingestion_end_to_end(self):
        requests=compile_voxcpm2_requests(VOICE_CONFIG,VOICE_PACKET)
        private=json.loads((ROOT/"model-evaluations/slice01/voice/packet/blind_map_private.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outputs=[]
            for request in requests:
                outputs.append({
                    "request_digest":request["request_digest"],
                    "blind_id":request["blind_id"],
                    "audio_sha256":("a" if request["language"]=="en" else "b")*64,
                    "sample_rate_hz":48000,
                    "duration_sec":min(1.5,request["cue_budget_sec"]-0.1),
                    "bytes":144044,
                })
            outputs_path=root/"outputs.json"
            outputs_path.write_text(json.dumps({"schema_version":1,"outputs":outputs}),encoding="utf-8")

            scores_path=root/"scores.csv"
            fields=[
                "blind_id","intelligibility","character_match","cross_language_identity",
                "between_character_separation","prosody","artifact_free","overall",
                "audio_duration_sec","cue_fit","failure_tags","notes",
            ]
            with scores_path.open("w",encoding="utf-8",newline="") as fh:
                writer=csv.writer(fh)
                writer.writerow(fields)
                for sample in VOICE_PACKET["samples"]:
                    writer.writerow([sample["blind_id"],5,5,5,5,5,5,5,"","","","synthetic-test"])

            out_path=root/"ranking.json"
            proc=subprocess.run(
                [
                    sys.executable,
                    str(ROOT/"tools/ingest_voxcpm2_scores.py"),
                    "--outputs",str(outputs_path),
                    "--scores",str(scores_path),
                    "--out",str(out_path),
                ],
                cwd=ROOT,text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)
            result=json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(result["status"],"UNBLINDED_AFTER_OUTPUT_AND_SCORE_VALIDATION")
            self.assertEqual(len(result["outputs"]),12)
            self.assertEqual(len(result["ranking"]),2)
            self.assertTrue(all(row["sample_count"]==6 for row in result["ranking"]))
            self.assertEqual({row["group"]["character_id"] for row in result["ranking"]},{"an","linh"})

    def test_voxcpm2_score_ingestion_rejects_incomplete_score_set(self):
        requests=compile_voxcpm2_requests(VOICE_CONFIG,VOICE_PACKET)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            outputs=[
                {
                    "request_digest":request["request_digest"],
                    "blind_id":request["blind_id"],
                    "audio_sha256":"a"*64,
                    "sample_rate_hz":48000,
                    "duration_sec":1.0,
                    "bytes":100,
                }
                for request in requests
            ]
            outputs_path=root/"outputs.json"
            outputs_path.write_text(json.dumps({"outputs":outputs}),encoding="utf-8")
            scores_path=root/"scores.csv"
            scores_path.write_text(
                "blind_id,intelligibility,character_match,cross_language_identity,between_character_separation,prosody,artifact_free,overall,audio_duration_sec,cue_fit,failure_tags,notes\n",
                encoding="utf-8",
            )
            proc=subprocess.run(
                [
                    sys.executable,
                    str(ROOT/"tools/ingest_voxcpm2_scores.py"),
                    "--outputs",str(outputs_path),
                    "--scores",str(scores_path),
                    "--out",str(root/"ranking.json"),
                ],
                cwd=ROOT,text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,2)
            self.assertIn("VOICE_EVAL_FAIL",proc.stderr)
            self.assertFalse((root/"ranking.json").exists())



if __name__=="__main__":
    unittest.main()
