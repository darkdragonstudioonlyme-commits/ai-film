import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from film.asset_graph import AssetGraph, AssetGraphError
from film.qc import QCError, acceptance_decision, experiment_delta, validate_experiment
from film.rights import RightsError, publication_gate, validate_rights_record

ROOT=Path(__file__).resolve().parents[2]


def sha(ch):
    return (ch * 64)[:64]


class AssetGraphTests(unittest.TestCase):
    def setUp(self):
        self.assets=[
            {"asset_id":"story","kind":"story","content_sha256":sha("a"),"manifest_sha256":sha("1"),"approved":True,"evidence":True},
            {"asset_id":"shot","kind":"shot_spec","content_sha256":sha("b"),"manifest_sha256":sha("2")},
            {"asset_id":"image","kind":"image","content_sha256":sha("c"),"manifest_sha256":sha("3")},
            {"asset_id":"video","kind":"video","content_sha256":sha("d"),"manifest_sha256":sha("4")},
            {"asset_id":"dialogue","kind":"dialogue","content_sha256":sha("e"),"manifest_sha256":sha("5")},
            {"asset_id":"voice","kind":"voice","content_sha256":sha("f"),"manifest_sha256":sha("6")},
            {"asset_id":"lipsync","kind":"lipsync","content_sha256":sha("0"),"manifest_sha256":sha("7")},
            {"asset_id":"background","kind":"image","content_sha256":sha("8"),"manifest_sha256":sha("9")},
        ]
        self.edges=[
            {"parent_asset_id":"story","child_asset_id":"shot"},
            {"parent_asset_id":"shot","child_asset_id":"image"},
            {"parent_asset_id":"image","child_asset_id":"video"},
            {"parent_asset_id":"dialogue","child_asset_id":"voice"},
            {"parent_asset_id":"voice","child_asset_id":"lipsync"},
            {"parent_asset_id":"video","child_asset_id":"lipsync"},
        ]

    def test_dialogue_invalidation_is_selective(self):
        graph=AssetGraph(self.assets,self.edges)
        plan=graph.invalidation_plan({"dialogue"},reason="dialogue revised")
        self.assertEqual(plan["affected_assets"],["dialogue","lipsync","voice"])
        self.assertIn("background",plan["unaffected_assets"])
        self.assertIn("image",plan["unaffected_assets"])
        self.assertFalse(plan["regeneration_authorized"])

    def test_image_change_reaches_video_and_lipsync_only(self):
        graph=AssetGraph(self.assets,self.edges)
        plan=graph.invalidation_plan({"image"},reason="casting reference changed")
        self.assertEqual(plan["descendants_invalidated"],["lipsync","video"])
        self.assertNotIn("voice",plan["affected_assets"])

    def test_cycle_rejected(self):
        graph=AssetGraph(self.assets,self.edges)
        with self.assertRaisesRegex(AssetGraphError,"cycle"):
            graph.add_dependency("lipsync","story")

    def test_deletion_dry_run_blocks_approved_and_referenced_assets(self):
        graph=AssetGraph(self.assets,self.edges)
        impact=graph.deletion_impact({"story"},selected_asset_ids={"story"})
        self.assertFalse(impact["delete_permitted"])
        self.assertIn("approved:story",impact["blockers"])
        self.assertIn("selected:story",impact["blockers"])
        self.assertIn("evidence:story",impact["blockers"])
        self.assertIn("referenced-by-descendants:story",impact["blockers"])

    def test_immutable_asset_conflict_rejected(self):
        graph=AssetGraph(self.assets,self.edges)
        bad=copy.deepcopy(self.assets[0])
        bad["content_sha256"]=sha("b")
        with self.assertRaisesRegex(AssetGraphError,"immutable asset conflict"):
            graph.add_asset(bad)


class QCTests(unittest.TestCase):
    def record(self):
        return {
            "qc_id":"qc1",
            "asset_id":"video1",
            "manifest_sha256":sha("a"),
            "scope":"sequence",
            "scores":{
                "story_comprehension":4.5,
                "visual_quality":4.5,
                "character_consistency":4.5,
                "motion_quality":4.0,
                "continuity":4.5,
            },
            "failure_tags":[],
        }

    def test_acceptance_passes_without_severe_failures(self):
        decision=acceptance_decision(self.record(),required_scores={"visual_quality":4,"character_consistency":4,"motion_quality":3.5})
        self.assertTrue(decision["accepted"])
        self.assertFalse(decision["selection_authorized"])

    def test_severe_failure_blocks_even_with_high_scores(self):
        row=self.record()
        row["failure_tags"]=["FACE_DRIFT"]
        decision=acceptance_decision(row,required_scores={"visual_quality":4})
        self.assertFalse(decision["accepted"])
        self.assertIn("severe-failure:FACE_DRIFT",decision["blockers"])

    def test_unknown_failure_tag_rejected(self):
        row=self.record()
        row["failure_tags"]=["MAGIC_FAILURE"]
        with self.assertRaisesRegex(QCError,"unknown failure"):
            acceptance_decision(row,required_scores={"visual_quality":4})

    def test_experiment_delta_requires_same_metric_population(self):
        exp={
            "experiment_id":"exp1",
            "hypothesis":"new reference improves identity",
            "changed_variable":"reference_image",
            "eval_population_id":"slice01-heldout-v1",
            "sample_count":8,
            "baseline_metrics":{"identity":3.8,"cost":1.2},
            "candidate_metrics":{"identity":4.2,"cost":1.3},
            "regressions":[],
            "decision":"KEEP",
        }
        result=experiment_delta(exp)
        self.assertAlmostEqual(result["deltas"]["identity"],0.4)
        self.assertTrue(result["promotion_authorized"])
        bad=copy.deepcopy(exp)
        bad["candidate_metrics"]={"identity":4.2}
        with self.assertRaisesRegex(QCError,"metric sets differ"):
            validate_experiment(bad)

    def test_regression_blocks_promotion_even_when_decision_keep(self):
        exp={
            "experiment_id":"exp2",
            "hypothesis":"faster sampler keeps quality",
            "changed_variable":"sampler_steps",
            "eval_population_id":"slice01-heldout-v1",
            "sample_count":8,
            "baseline_metrics":{"quality":4.2},
            "candidate_metrics":{"quality":4.3},
            "regressions":["temporal_flicker+0.3"],
            "decision":"KEEP",
        }
        self.assertFalse(experiment_delta(exp)["promotion_authorized"])


class RightsTests(unittest.TestCase):
    def policy(self):
        return [
            {"subject_type":"source","subject_id":"project-source"},
            {"subject_type":"voice","subject_id":"an"},
            {"subject_type":"voice","subject_id":"linh"},
            {"subject_type":"likeness","subject_id":"an"},
            {"subject_type":"likeness","subject_id":"linh"},
            {"subject_type":"model_output","subject_id":"visual-generation"},
            {"subject_type":"music","subject_id":"project-music"},
        ]

    def cleared_records(self):
        common={"allowed_uses":["COMMERCIAL_PUBLICATION"],"evidence_ref":"test-evidence"}
        return [
            {"rights_id":"r1","subject_type":"source","subject_id":"project-source","status":"ORIGINAL",**common},
            {"rights_id":"r2","subject_type":"voice","subject_id":"an","status":"CONSENTED",**common},
            {"rights_id":"r3","subject_type":"voice","subject_id":"linh","status":"CONSENTED",**common},
            {"rights_id":"r4","subject_type":"likeness","subject_id":"an","status":"ORIGINAL",**common},
            {"rights_id":"r5","subject_type":"likeness","subject_id":"linh","status":"ORIGINAL",**common},
            {"rights_id":"r6","subject_type":"model_output","subject_id":"visual-generation","status":"MODEL_LICENSE_CLEARED",**common},
            {"rights_id":"r7","subject_type":"music","subject_id":"project-music","status":"LICENSED",**common},
        ]

    def assets(self):
        return [
            {"asset_id":"final-video","content_sha256":sha("a"),"manifest_sha256":sha("b"),"publishable":True,"revoked":False}
        ]

    def test_complete_gate_requires_owner_approval_but_does_not_publish(self):
        result=publication_gate(
            selected_assets=self.assets(),
            rights_records=self.cleared_records(),
            creative_qc_pass=True,
            technical_qc_pass=True,
            provenance_complete=True,
            distribution_rules_checked_on="2026-09-25",
            as_of="2026-09-25",
            required_subjects=self.policy(),
            owner_approved=False,
        )
        self.assertEqual(result["status"],"READY_FOR_OWNER_APPROVAL")
        self.assertFalse(result["publish_action_performed"])
        approved=publication_gate(
            selected_assets=self.assets(),
            rights_records=self.cleared_records(),
            creative_qc_pass=True,
            technical_qc_pass=True,
            provenance_complete=True,
            distribution_rules_checked_on="2026-09-25",
            as_of="2026-09-25",
            required_subjects=self.policy(),
            owner_approved=True,
        )
        self.assertEqual(approved["status"],"AUTHORIZED_TO_PUBLISH")
        self.assertFalse(approved["publish_action_performed"])

    def test_missing_music_and_qc_block_publication(self):
        records=[r for r in self.cleared_records() if r["subject_type"]!="music"]
        result=publication_gate(
            selected_assets=self.assets(),
            rights_records=records,
            creative_qc_pass=False,
            technical_qc_pass=True,
            provenance_complete=True,
            distribution_rules_checked_on="2026-09-25",
            as_of="2026-09-25",
            required_subjects=self.policy(),
        )
        self.assertEqual(result["status"],"BLOCKED")
        self.assertIn("creative-qc-not-pass",result["blockers"])
        self.assertIn("rights-missing:music:project-music",result["blockers"])

    def test_revoked_asset_and_rights_block(self):
        assets=self.assets()
        assets[0]["revoked"]=True
        records=self.cleared_records()
        records[1]["status"]="REVOKED"
        result=publication_gate(
            selected_assets=assets,
            rights_records=records,
            creative_qc_pass=True,
            technical_qc_pass=True,
            provenance_complete=True,
            distribution_rules_checked_on="2026-09-25",
            as_of="2026-09-25",
            required_subjects=self.policy(),
        )
        self.assertIn("asset-revoked:final-video",result["blockers"])
        self.assertTrue(any(x.startswith("rights-blocked:voice:an") for x in result["blockers"]))


if __name__=="__main__":
    unittest.main()
