import json
import shutil
from pathlib import Path
import tempfile
import unittest

from film.current_video_ensemble import CurrentVideoEnsembleError, finalize_current_video_ensemble
from film.vbench_auto_eval import DIMENSIONS, build_receipt

ROOT=Path(__file__).resolve().parents[2]
POLICY=json.loads((ROOT/"model-evaluations/auto-eval/policy.json").read_text())
BATCH=json.loads((ROOT/"model-evaluations/auto-eval/current_batch_20260926.json").read_text())
PENDING=json.loads((ROOT/"model-evaluations/auto-eval/vbench_pending_20260926.json").read_text())
REAL_ROOT=Path("/home/dragon/ai-film-dev/run-evidence/auto-eval/video-20260926")
REV="fd18b3d055cb0fc6f066ca90fe2c3c8cbb698490"


def make_root(td: Path)->Path:
    for row in BATCH["video_assets"]:
        aid=row["asset_id"]
        dst=td/aid
        dst.mkdir(parents=True,exist_ok=True)
        for name in ("qwen3vl.json","paddleocr.json"):
            shutil.copy2(REAL_ROOT/aid/name,dst/name)
    raw={name:[0.92,[]] for name in DIMENSIONS}
    for aid in PENDING["eligible_asset_ids"]:
        rec=build_receipt(asset_id=aid,results=raw,code_revision=REV)
        (td/aid/"vbench.json").write_text(json.dumps(rec))
    return td


class CurrentVideoEnsembleTests(unittest.TestCase):
    def test_three_vbench_receipts_finalize_four_asset_ensemble(self):
        with tempfile.TemporaryDirectory() as td:
            result=finalize_current_video_ensemble(
                policy=POLICY,batch=BATCH,pending=PENDING,receipt_root=make_root(Path(td))
            )
            self.assertEqual(result["status"],"PASS_AUTO_EVAL_COMPLETE")
            self.assertEqual(result["sample_count"],4)
            self.assertEqual(result["vbench_executed_count"],3)
            self.assertEqual(result["vbench_skipped_hard_fail_count"],1)
            self.assertEqual(set(result["auto_shortlist_asset_ids"]),set(PENDING["eligible_asset_ids"]))
            self.assertEqual(result["auto_retry_asset_ids"],[])
            self.assertEqual(result["auto_reject_asset_ids"],["wan22-sc01-sh04-zimage-ref-v1"])
            z=next(r for r in result["results"] if r["asset_id"]=="wan22-sc01-sh04-zimage-ref-v1")
            self.assertEqual(z["status"],"AUTO_REJECT_HARD_FAIL")
            self.assertEqual(z["vbench_execution"],"SKIPPED_TERMINAL_HARD_FAIL")
            self.assertFalse(result["human_review_required"])
            self.assertFalse(result["production_acceptance"])

    def test_missing_vbench_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=make_root(Path(td))
            (root/PENDING["eligible_asset_ids"][0]/"vbench.json").unlink()
            with self.assertRaisesRegex(CurrentVideoEnsembleError,"missing evaluator receipt"):
                finalize_current_video_ensemble(
                    policy=POLICY,batch=BATCH,pending=PENDING,receipt_root=root
                )

    def test_mismatched_vbench_asset_id_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=make_root(Path(td))
            aid=PENDING["eligible_asset_ids"][0]
            p=root/aid/"vbench.json"
            rec=json.loads(p.read_text()); rec["asset_id"]="wrong-asset"; p.write_text(json.dumps(rec))
            with self.assertRaisesRegex(CurrentVideoEnsembleError,"receipt asset mismatch"):
                finalize_current_video_ensemble(
                    policy=POLICY,batch=BATCH,pending=PENDING,receipt_root=root
                )


if __name__=="__main__":
    unittest.main()
