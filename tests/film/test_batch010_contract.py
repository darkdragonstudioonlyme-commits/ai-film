import copy
import json
from pathlib import Path
import unittest

from film.production_state import (
    ProductionStateError,
    new_shot,
    new_take,
    revise_shot_spec,
    select_take,
    transition_shot,
    transition_take,
)
from film.generation_control import (
    GenerationControlError,
    apply_attempt_outcome,
    begin_attempt,
    logical_generation_key,
    new_logical_job,
    record_provider_submission,
    request_cancel,
    transition_attempt,
    reconcile_unknown_outcome,
)
from film.edit_plan import compile_edit_plan

ROOT=Path(__file__).resolve().parents[2]
TIMING=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))


class ProductionStateTests(unittest.TestCase):
    def accepted_take(self,shot):
        take=new_take(
            take_id="take1",shot_id=shot["shot_id"],shot_spec_revision=shot["spec_revision"],
            asset_id="asset1",manifest_sha256="a"*64,
        )
        take=transition_take(take,expected_version=1,to_state="QC_PENDING")
        return transition_take(take,expected_version=2,to_state="ACCEPTED")

    def test_stale_shot_transition_rejected(self):
        shot=new_shot("s1",1)
        shot=transition_shot(shot,expected_version=1,to_state="READY")
        with self.assertRaisesRegex(ProductionStateError,"stale shot version"):
            transition_shot(shot,expected_version=1,to_state="GENERATING")

    def test_selection_is_revisioned_and_previous_record_immutable(self):
        shot=new_shot("s1",1)
        shot=transition_shot(shot,expected_version=1,to_state="READY")
        shot=transition_shot(shot,expected_version=2,to_state="GENERATING")
        shot=transition_shot(shot,expected_version=3,to_state="REVIEW")
        take=self.accepted_take(shot)
        selected,rev1=select_take(shot,take,expected_shot_version=4,actor="reviewer")
        before=copy.deepcopy(rev1)
        take2=new_take(take_id="take2",shot_id="s1",shot_spec_revision=1,asset_id="asset2",manifest_sha256="b"*64)
        take2=transition_take(take2,expected_version=1,to_state="QC_PENDING")
        take2=transition_take(take2,expected_version=2,to_state="ACCEPTED")
        selected2,rev2=select_take(selected,take2,expected_shot_version=5,actor="reviewer",previous_selection=rev1)
        self.assertEqual(rev1,before)
        self.assertEqual(rev2["selection_revision"],2)
        self.assertEqual(rev2["supersedes_selection_id"],rev1["selection_id"])
        self.assertEqual(selected2["selected_take_id"],"take2")

    def test_ready_shot_cannot_skip_review_for_selection(self):
        shot=new_shot("s1",1)
        shot=transition_shot(shot,expected_version=1,to_state="READY")
        take=self.accepted_take(shot)
        with self.assertRaisesRegex(ProductionStateError,"REVIEW/APPROVED"):
            select_take(shot,take,expected_shot_version=2,actor="reviewer")

    def test_stale_spec_take_cannot_be_selected(self):
        shot=new_shot("s1",1)
        shot=transition_shot(shot,expected_version=1,to_state="READY")
        shot=transition_shot(shot,expected_version=2,to_state="GENERATING")
        shot=transition_shot(shot,expected_version=3,to_state="REVIEW")
        old_take=self.accepted_take(shot)
        shot=revise_shot_spec(shot,expected_version=4,new_spec_revision=2)
        shot=transition_shot(shot,expected_version=5,to_state="GENERATING")
        shot=transition_shot(shot,expected_version=6,to_state="REVIEW")
        with self.assertRaisesRegex(ProductionStateError,"stale shot spec"):
            select_take(shot,old_take,expected_shot_version=7,actor="reviewer")


class GenerationControlTests(unittest.TestCase):
    def key(self):
        return logical_generation_key(
            shot_spec={"shot_id":"s1","revision":1},
            model_identity={"repo":"m","revision":"r"},
            compiled_prompt={"prompt":"hello"},
            reference_digests=["b"*64,"a"*64],
            seed_policy={"seed":7},
            workflow_config={"steps":10},
            creative_revision=1,
        )

    def test_logical_key_is_order_stable_for_references(self):
        a=self.key()
        b=logical_generation_key(
            shot_spec={"shot_id":"s1","revision":1},
            model_identity={"repo":"m","revision":"r"},
            compiled_prompt={"prompt":"hello"},
            reference_digests=["a"*64,"b"*64],
            seed_policy={"seed":7},
            workflow_config={"steps":10},
            creative_revision=1,
        )
        self.assertEqual(a,b)

    def test_unknown_outcome_blocks_retry_until_reconciled(self):
        job=new_logical_job(logical_key=self.key(),max_attempts=3,cost_ceiling_usd=5)
        job,attempt=begin_attempt(job)
        attempt=record_provider_submission(attempt,expected_version=1,provider_request_id="provider-1")
        attempt=transition_attempt(attempt,expected_version=2,to_state="UNKNOWN_OUTCOME",cost_usd=1.0)
        job=apply_attempt_outcome(job,attempt)
        self.assertEqual(job["status"],"UNKNOWN_OUTCOME")
        self.assertEqual(job["cost_spent_usd"],1.0)
        with self.assertRaisesRegex(GenerationControlError,"reconcile UNKNOWN_OUTCOME"):
            begin_attempt(job)
        job,reconciled=reconcile_unknown_outcome(
            job,attempt,expected_attempt_version=3,
            resolved_state="FAILED_RETRYABLE",
            provider_evidence="provider says request failed before generation",
        )
        self.assertEqual(job["status"],"READY")
        self.assertEqual(job["cost_spent_usd"],1.0)
        self.assertEqual(reconciled["state"],"FAILED_RETRYABLE")

    def test_same_attempt_outcome_cannot_be_applied_twice(self):
        job=new_logical_job(logical_key=self.key(),max_attempts=2,cost_ceiling_usd=5)
        job,attempt=begin_attempt(job)
        attempt=record_provider_submission(attempt,expected_version=1,provider_request_id="provider-1")
        attempt=transition_attempt(attempt,expected_version=2,to_state="FAILED_RETRYABLE",cost_usd=1.0)
        job=apply_attempt_outcome(job,attempt)
        with self.assertRaisesRegex(GenerationControlError,"already applied"):
            apply_attempt_outcome(job,attempt)

    def test_cost_ceiling_stops_outcome(self):
        job=new_logical_job(logical_key=self.key(),max_attempts=2,cost_ceiling_usd=1.0)
        job,attempt=begin_attempt(job)
        attempt=record_provider_submission(attempt,expected_version=1,provider_request_id="provider-1")
        attempt=transition_attempt(attempt,expected_version=2,to_state="FAILED_RETRYABLE",cost_usd=1.1)
        with self.assertRaisesRegex(GenerationControlError,"cost ceiling"):
            apply_attempt_outcome(job,attempt)

    def test_cancelled_ready_job_cannot_start(self):
        job=new_logical_job(logical_key=self.key(),max_attempts=2,cost_ceiling_usd=5)
        job=request_cancel(job)
        self.assertEqual(job["status"],"CANCELLED")
        with self.assertRaisesRegex(GenerationControlError,"cancelled"):
            begin_attempt(job)


class EditPlanTests(unittest.TestCase):
    def test_missing_media_is_explicit_blocker(self):
        subtitles={"en":"projects/slice01/timing/subtitles/en.srt"}
        plan=compile_edit_plan(
            TIMING,SHOTS,selected_takes={},dialogue_tracks={},
            subtitle_tracks=subtitles,aspect="9:16",language="en",
        )
        self.assertEqual(plan["status"],"BLOCKED_MISSING_MEDIA")
        self.assertEqual(plan["duration_sec"],75.0)
        self.assertEqual(sum(x.startswith("missing-selected-take:") for x in plan["blockers"]),8)
        self.assertEqual(sum(x.startswith("missing-dialogue-audio:") for x in plan["blockers"]),4)
        self.assertFalse(plan["render_authorized"])

    def test_complete_media_plan_is_deterministic_but_not_render_authorized(self):
        selected={
            shot["shot_id"]:{
                "selection_revision":1,"take_id":"take_"+shot["shot_id"],
                "asset_id":"video_"+shot["shot_id"],"manifest_sha256":"a"*64,
            }
            for shot in SHOTS
        }
        dialogue={}
        for cue in TIMING["dialogue_cues"]:
            budget=cue["end_offset_sec"]-cue["start_offset_sec"]
            dialogue[cue["dialogue_id"]]={
                "language":"en","asset_id":"audio_"+cue["dialogue_id"],
                "sha256":"b"*64,"duration_sec":budget-0.1,
            }
        kwargs=dict(
            timing=TIMING,shots=SHOTS,selected_takes=selected,dialogue_tracks=dialogue,
            subtitle_tracks={"en":"projects/slice01/timing/subtitles/en.srt"},
            aspect="9:16",language="en",
        )
        a=compile_edit_plan(**kwargs)
        b=compile_edit_plan(**kwargs)
        self.assertEqual(a,b)
        self.assertEqual(a["status"],"READY_TO_RENDER")
        self.assertEqual(a["blockers"],[])
        self.assertFalse(a["render_authorized"])
        self.assertEqual(len(a["plan_digest"]),64)

    def test_dialogue_over_budget_blocks(self):
        selected={
            shot["shot_id"]:{
                "selection_revision":1,"take_id":"t","asset_id":"v","manifest_sha256":"a"*64,
            } for shot in SHOTS
        }
        dialogue={
            cue["dialogue_id"]:{"language":"en","asset_id":"a","sha256":"b"*64,"duration_sec":99}
            for cue in TIMING["dialogue_cues"]
        }
        plan=compile_edit_plan(TIMING,SHOTS,selected_takes=selected,dialogue_tracks=dialogue,subtitle_tracks={"en":"x.srt"},aspect="9:16",language="en")
        self.assertTrue(any(x.startswith("dialogue-over-budget:") for x in plan["blockers"]))


if __name__=="__main__":
    unittest.main()
