import copy
import json
from pathlib import Path
import tempfile
import unittest

from film.edit_plan import compile_edit_plan
from film.render_compile import RenderCompileError, compile_ffmpeg_render_spec
from film.technical_qc import bind_media_identity, evaluate_ffprobe
from film.delivery import DeliveryError, build_delivery_manifest, expected_variants

ROOT=Path(__file__).resolve().parents[2]
TIMING=json.loads((ROOT/"projects/slice01/timing/timing.json").read_text(encoding="utf-8"))
SHOTS=json.loads((ROOT/"projects/slice01/shots/benchmark_shots.json").read_text(encoding="utf-8"))


def ready_plan():
    selected={
        shot["shot_id"]:{
            "selection_revision":1,
            "take_id":"take_"+shot["shot_id"],
            "asset_id":"video_"+shot["shot_id"],
            "manifest_sha256":"a"*64,
        }
        for shot in SHOTS
    }
    dialogue={}
    for cue in TIMING["dialogue_cues"]:
        budget=cue["end_offset_sec"]-cue["start_offset_sec"]
        dialogue[cue["dialogue_id"]]={
            "language":"en",
            "asset_id":"audio_"+cue["dialogue_id"],
            "sha256":"b"*64,
            "duration_sec":budget-0.1,
        }
    return compile_edit_plan(
        TIMING,SHOTS,
        selected_takes=selected,
        dialogue_tracks=dialogue,
        subtitle_tracks={"en":"projects/slice01/timing/subtitles/en.srt"},
        aspect="9:16",language="en",
    )


def catalog_for(plan):
    catalog={}
    for segment in plan["segments"]:
        video=segment["video"]
        catalog[video["asset_id"]]={
            "path":f"/media/{video['asset_id']}.mp4",
            "sha256":"c"*64,
            "manifest_sha256":video["manifest_sha256"],
        }
    for cue in plan["dialogue"]:
        audio=cue["audio"]
        catalog[audio["asset_id"]]={
            "path":f"/media/{audio['asset_id']}.wav",
            "sha256":audio["sha256"],
        }
    return catalog


class RenderCompileTests(unittest.TestCase):
    def test_blocked_edit_plan_cannot_compile(self):
        blocked=json.loads((ROOT/"projects/slice01/edit/edit_plan.placeholder.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(RenderCompileError,"not READY_TO_RENDER"):
            compile_ffmpeg_render_spec(blocked,{},output_path="/out.mp4")

    def test_ready_plan_compiles_deterministically_without_execution_authority(self):
        plan=ready_plan()
        catalog=catalog_for(plan)
        a=compile_ffmpeg_render_spec(plan,catalog,output_path="/out.mp4")
        b=compile_ffmpeg_render_spec(plan,catalog,output_path="/out.mp4")
        self.assertEqual(a,b)
        self.assertFalse(a["execution_permitted"])
        self.assertEqual((a["width"],a["height"]),(720,1280))
        self.assertEqual(len(a["video_inputs"]),8)
        self.assertEqual(len(a["audio_inputs"]),4)
        self.assertEqual(a["ffmpeg_argv"][0],"ffmpeg")
        self.assertIn("-filter_complex",a["ffmpeg_argv"])
        self.assertEqual(len(a["spec_digest"]),64)

    def test_tampered_edit_plan_digest_rejected(self):
        plan=ready_plan()
        plan["segments"][0]["duration_sec"]=999
        with self.assertRaisesRegex(RenderCompileError,"digest mismatch"):
            compile_ffmpeg_render_spec(plan,catalog_for(ready_plan()),output_path="/out.mp4")

    def test_video_manifest_mismatch_rejected(self):
        plan=ready_plan()
        catalog=catalog_for(plan)
        first=plan["segments"][0]["video"]["asset_id"]
        catalog[first]["manifest_sha256"]="d"*64
        with self.assertRaisesRegex(RenderCompileError,"manifest mismatch"):
            compile_ffmpeg_render_spec(plan,catalog,output_path="/out.mp4")


class TechnicalQCTests(unittest.TestCase):
    def good_probe(self):
        return {
            "format":{"duration":"75.000000"},
            "streams":[
                {"codec_type":"video","width":720,"height":1280,"avg_frame_rate":"24/1"},
                {"codec_type":"audio","sample_rate":"48000"},
            ],
        }

    def test_good_probe_passes(self):
        result=evaluate_ffprobe(
            self.good_probe(),
            expected_duration_sec=75,
            expected_width=720,
            expected_height=1280,
            expected_fps=24,
        )
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["blockers"],[])

    def test_wrong_dimensions_duration_audio_fail(self):
        probe=self.good_probe()
        probe["format"]["duration"]="73.0"
        probe["streams"][0]["width"]=1280
        probe["streams"][0]["height"]=720
        probe["streams"][1]["sample_rate"]="44100"
        result=evaluate_ffprobe(
            probe,
            expected_duration_sec=75,
            expected_width=720,
            expected_height=1280,
            expected_fps=24,
        )
        self.assertEqual(result["status"],"FAIL")
        self.assertTrue(any(x.startswith("duration:") for x in result["blockers"]))
        self.assertTrue(any(x.startswith("dimensions:") for x in result["blockers"]))
        self.assertTrue(any(x.startswith("audio-sample-rate:") for x in result["blockers"]))

    def test_media_identity_binding_hashes_exact_file(self):
        qc=evaluate_ffprobe(
            self.good_probe(),
            expected_duration_sec=75,
            expected_width=720,
            expected_height=1280,
            expected_fps=24,
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"media.mp4"
            path.write_bytes(b"synthetic-container-bytes")
            bound=bind_media_identity(qc,path,technical_qc_id="techqc-1")
            self.assertEqual(bound["technical_qc_id"],"techqc-1")
            self.assertEqual(len(bound["media_sha256"]),64)
            self.assertEqual(bound["media_bytes"],len(b"synthetic-container-bytes"))


class DeliveryTests(unittest.TestCase):
    def complete(self):
        rows=[]
        for variant in expected_variants():
            aspect=variant["aspect"]
            language=variant["language"]
            key=f"{aspect}-{language}"
            rows.append({
                "aspect":aspect,
                "language":language,
                "media_asset_id":"media-"+key,
                "media_sha256":"a"*64,
                "media_manifest_sha256":"b"*64,
                "subtitle_path":f"subs/{language}.srt",
                "subtitle_sha256":"c"*64,
                "technical_qc_id":"tech-"+key,
                "technical_qc_status":"PASS",
            })
        return rows

    def test_complete_package_can_still_be_publication_blocked(self):
        manifest=build_delivery_manifest(
            self.complete(),
            publication_gate_status="BLOCKED",
            creative_qc_ref="qc/final.json",
            rights_gate_ref="rights/final.json",
        )
        self.assertEqual(manifest["status"],"PACKAGE_COMPLETE_PUBLICATION_BLOCKED")
        self.assertFalse(manifest["published"])
        self.assertFalse(manifest["publish_action_performed"])
        self.assertEqual(manifest["blockers"],[])

    def test_authorized_package_still_does_not_publish(self):
        manifest=build_delivery_manifest(
            self.complete(),
            publication_gate_status="AUTHORIZED_TO_PUBLISH",
            creative_qc_ref="qc/final.json",
            rights_gate_ref="rights/final.json",
        )
        self.assertEqual(manifest["status"],"PACKAGE_AUTHORIZED_NOT_PUBLISHED")
        self.assertFalse(manifest["published"])

    def test_missing_variant_is_incomplete(self):
        rows=self.complete()[:-1]
        manifest=build_delivery_manifest(
            rows,
            publication_gate_status="BLOCKED",
            creative_qc_ref="qc/final.json",
            rights_gate_ref="rights/final.json",
        )
        self.assertEqual(manifest["status"],"INCOMPLETE")
        self.assertTrue(any(x.startswith("missing-variant:") for x in manifest["blockers"]))

    def test_empty_gate_refs_rejected(self):
        with self.assertRaisesRegex(DeliveryError,"required"):
            build_delivery_manifest(
                self.complete(),
                publication_gate_status="BLOCKED",
                creative_qc_ref="",
                rights_gate_ref="",
            )


if __name__=="__main__":
    unittest.main()
