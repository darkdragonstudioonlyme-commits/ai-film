from __future__ import annotations

from copy import deepcopy
from typing import Any


class LipSyncPlanError(ValueError):
    pass


LANGUAGES = {"en", "zh-CN", "vi"}


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _normalize_media_identity(media: dict[str, Any] | None, *, kind: str, key: str) -> tuple[dict[str, Any] | None, str | None]:
    if media is None:
        return None, f"missing-{kind}:{key}"
    required = ("asset_id", "sha256", "manifest_sha256")
    missing = [field for field in required if not media.get(field)]
    if missing:
        return None, f"invalid-{kind}:{key}:{','.join(missing)}"
    if not _valid_sha(media["sha256"]) or not _valid_sha(media["manifest_sha256"]):
        return None, f"invalid-{kind}-hash:{key}"
    return {
        "asset_id": media["asset_id"],
        "sha256": media["sha256"],
        "manifest_sha256": media["manifest_sha256"],
    }, None


def compile_lipsync_plan(
    policy: dict[str, Any],
    shots: list[dict[str, Any]],
    *,
    language: str,
    selected_videos: dict[str, dict[str, Any]],
    dialogue_audio: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if language not in LANGUAGES:
        raise LipSyncPlanError(f"unsupported language: {language}")
    shot_by_id = {shot["shot_id"]: shot for shot in shots}
    if len(shot_by_id) != len(shots):
        raise LipSyncPlanError("duplicate shot id")
    if policy.get("status") != "POLICY_READY_NO_FINAL_MEDIA":
        raise LipSyncPlanError("lip-sync policy status is not preproduction-ready")

    requests: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    blockers: list[str] = []
    seen_dialogue: set[str] = set()

    for row in policy.get("dialogue_shots", []):
        dialogue_id = row.get("dialogue_id")
        shot_id = row.get("shot_id")
        speaker_id = row.get("speaker_id")
        if not dialogue_id or dialogue_id in seen_dialogue:
            raise LipSyncPlanError("invalid/duplicate dialogue_id in policy")
        seen_dialogue.add(dialogue_id)
        shot = shot_by_id.get(shot_id)
        if shot is None:
            raise LipSyncPlanError(f"policy references unknown shot: {shot_id}")
        if shot.get("dialogue_id") != dialogue_id:
            raise LipSyncPlanError(f"dialogue/shot mismatch: {dialogue_id}")
        if speaker_id not in shot.get("characters", []):
            raise LipSyncPlanError(f"speaker not present in shot: {dialogue_id}")
        if not row.get("mouth_visible", False):
            skipped.append({
                "dialogue_id": dialogue_id,
                "shot_id": shot_id,
                "speaker_id": speaker_id,
                "reason": row.get("skip_reason") or "MOUTH_NOT_VISIBLE",
            })
            continue

        video, video_error = _normalize_media_identity(
            selected_videos.get(shot_id),
            kind="video",
            key=shot_id,
        )
        audio, audio_error = _normalize_media_identity(
            dialogue_audio.get(dialogue_id),
            kind="audio",
            key=f"{dialogue_id}:{language}",
        )
        if audio is not None and dialogue_audio[dialogue_id].get("language") != language:
            audio = None
            audio_error = f"audio-language-mismatch:{dialogue_id}:{language}"
        if video_error:
            blockers.append(video_error)
        if audio_error:
            blockers.append(audio_error)

        requests.append({
            "schema_version": 1,
            "dialogue_id": dialogue_id,
            "shot_id": shot_id,
            "speaker_id": speaker_id,
            "language": language,
            "mouth_visibility": row.get("visibility"),
            "video": video,
            "audio": audio,
            "backend_candidates": list(policy.get("backend_candidates", [])),
            "execution_permitted": False,
        })

    expected_dialogue = {shot["dialogue_id"] for shot in shots if shot.get("dialogue_id")}
    if seen_dialogue != expected_dialogue:
        raise LipSyncPlanError(
            f"policy dialogue population mismatch expected={sorted(expected_dialogue)} actual={sorted(seen_dialogue)}"
        )

    return {
        "schema_version": 1,
        "project_id": policy["project_id"],
        "language": language,
        "status": "READY_FOR_BACKEND_EVAL" if not blockers else "BLOCKED_MISSING_MEDIA",
        "requests": requests,
        "skipped": skipped,
        "blockers": sorted(set(blockers)),
        "execution_permitted": False,
    }
