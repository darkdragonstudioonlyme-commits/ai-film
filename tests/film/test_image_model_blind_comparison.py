import csv
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from film.blind_scoring import BlindScoreError
from film.image_model_blind_compare import (
    SCORE_SCHEMA,
    build_comparison_packet,
    rank_complete_scores,
    score_template_csv,
)

ROOT=Path(__file__).resolve().parents[2]
FLUX=json.loads((ROOT/"run-evidence/FLUX2_KLEIN_A40_FORMAL_SMOKE_20260925.json").read_text(encoding="utf-8"))
ZIMG=json.loads((ROOT/"run-evidence/Z_IMAGE_A40_FORMAL_SMOKE_20260926.json").read_text(encoding="utf-8"))
PUBLIC=json.loads((ROOT/"projects/slice01/casting/formal_comparison/blind_items.json").read_text(encoding="utf-8"))
PRIVATE=json.loads((ROOT/"projects/slice01/casting/formal_comparison/blind_map_private.json").read_text(encoding="utf-8"))
SCORES=(ROOT/"projects/slice01/casting/formal_comparison/scores.csv").read_text(encoding="utf-8")


class ImageModelBlindComparisonTests(unittest.TestCase):
    def test_packet_is_deterministic_eight_sample_and_model_opaque_publicly(self):
        public,private=build_comparison_packet(FLUX,ZIMG)
        self.assertEqual(public,PUBLIC)
        self.assertEqual(private,PRIVATE)
        self.assertEqual(public["status"],"AWAITING_BLIND_SCORES")
        self.assertEqual(public["sample_count"],8)
        self.assertFalse(public["selection_authorized"])
        self.assertFalse(public["production_acceptance"])
        self.assertEqual(len(public["items"]),8)
        self.assertEqual(len(private["mapping"]),8)
        self.assertTrue(all("model_id" not in row and "job_id" not in row and "model_revision" not in row for row in public["items"]))
        self.assertEqual({row["model_id"] for row in private["mapping"]},{"flux2-klein-4b","z-image"})

    def test_population_is_balanced_by_character_and_style(self):
        counts={}
        for row in PUBLIC["items"]:
            key=(row["character_id"],row["style"],row["slot"])
            counts[key]=counts.get(key,0)+1
        self.assertEqual(counts,{
            ("an","photoreal","face_front"):2,
            ("an","stylized_3d","face_front"):2,
            ("linh","photoreal","face_front"):2,
            ("linh","stylized_3d","face_front"):2,
        })
        self.assertTrue(all(row["width"]==1024 and row["height"]==1024 for row in PUBLIC["items"]))

    def test_score_template_is_blank_and_cannot_unblind_incomplete_scores(self):
        self.assertEqual(score_template_csv(PUBLIC),SCORES)
        rows=list(csv.DictReader(StringIO(SCORES)))
        self.assertEqual(len(rows),8)
        self.assertTrue(all(all(not (row.get(name) or "").strip() for name in SCORE_SCHEMA.criteria) for row in rows))
        with self.assertRaises(BlindScoreError):
            rank_complete_scores(PUBLIC,PRIVATE,SCORES)

    def test_complete_synthetic_scores_can_rank_only_after_all_eight_scores(self):
        mapping={row["blind_id"]:row for row in PRIVATE["mapping"]}
        out=StringIO()
        writer=csv.writer(out,lineterminator="\n")
        writer.writerow(["blind_id",*SCORE_SCHEMA.criteria,"failure_tags","notes"])
        for item in PUBLIC["items"]:
            model=mapping[item["blind_id"]]["model_id"]
            value=5 if model=="flux2-klein-4b" else 4
            writer.writerow([item["blind_id"],*[value]*len(SCORE_SCHEMA.criteria),"","synthetic-test-only"])
        ranking=rank_complete_scores(PUBLIC,PRIVATE,out.getvalue())
        self.assertEqual(len(ranking),2)
        self.assertEqual(ranking[0]["group"]["model_id"],"flux2-klein-4b")
        self.assertEqual(ranking[0]["sample_count"],4)
        self.assertEqual(ranking[1]["sample_count"],4)
        self.assertFalse(PUBLIC["selection_authorized"])

    def test_cli_rebuild_is_deterministic_and_non_selecting(self):
        with tempfile.TemporaryDirectory() as td:
            proc=subprocess.run(
                [sys.executable,str(ROOT/"tools/build_image_model_blind_comparison.py"),"--out-dir",td],
                cwd=ROOT,text=True,capture_output=True,check=False,
            )
            self.assertEqual(proc.returncode,0,proc.stderr)
            public=json.loads((Path(td)/"blind_items.json").read_text(encoding="utf-8"))
            private=json.loads((Path(td)/"blind_map_private.json").read_text(encoding="utf-8"))
            scores=(Path(td)/"scores.csv").read_text(encoding="utf-8")
            self.assertEqual(public,PUBLIC)
            self.assertEqual(private,PRIVATE)
            self.assertEqual(scores,SCORES)
            self.assertFalse(public["selection_authorized"])


if __name__=="__main__":
    unittest.main()
