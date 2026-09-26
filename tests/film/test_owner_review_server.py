import json
from pathlib import Path
import tempfile
import unittest

from tools.serve_owner_review import expected_voice_ids, validate_and_save

ROOT=Path(__file__).resolve().parents[2]


def payload(score=4):
    ids=sorted(expected_voice_ids())
    return {
        "schema_version":1,
        "review_id":"owner-review-server-test",
        "scale":{"min":0,"max":8},
        "voice":[{"kind":"voice","id":item_id,"score":score,"notes":""} for item_id in ids],
        "motion":[
            {"kind":"motion","id":"motion_A","score":5,"notes":""},
            {"kind":"motion","id":"motion_B","score":3,"notes":""},
        ],
    }


class OwnerReviewServerTests(unittest.TestCase):
    def test_complete_review_is_atomically_saved(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"scores.json"
            result=validate_and_save(payload(),output_path=out)
            self.assertEqual(result["status"],"PASS_COMPLETE_OWNER_REVIEW_SAVED")
            self.assertEqual(result["voice_samples"],12)
            self.assertEqual(result["motion_samples"],2)
            saved=json.loads(out.read_text())
            self.assertEqual(saved["scale"],{"min":0,"max":8})
            self.assertEqual(len(saved["voice"]),12)

    def test_incomplete_review_is_not_saved(self):
        from film.owner_review import OwnerReviewError
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"scores.json"
            bad=payload(); bad["voice"].pop()
            with self.assertRaises(OwnerReviewError):
                validate_and_save(bad,output_path=out)
            self.assertFalse(out.exists())


if __name__=="__main__":
    unittest.main()