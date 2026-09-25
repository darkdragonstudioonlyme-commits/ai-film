from __future__ import annotations

from array import array
import hashlib
from pathlib import Path
import wave


class AudioContractError(ValueError):
    pass


def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def read_pcm16_mono(path: Path, *, sample_rate: int=48000) -> array:
    with wave.open(str(path),"rb") as wav:
        if wav.getnchannels()!=1:
            raise AudioContractError(f"expected mono WAV: {path}")
        if wav.getsampwidth()!=2:
            raise AudioContractError(f"expected PCM16 WAV: {path}")
        if wav.getframerate()!=sample_rate:
            raise AudioContractError(f"sample rate mismatch: {path}")
        frames=wav.readframes(wav.getnframes())
    samples=array("h")
    samples.frombytes(frames)
    return samples


def write_pcm16_mono(path: Path, samples: array, *, sample_rate: int=48000) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples.tobytes())


def mix_dialogue_timeline(
    clips: list[dict],
    *,
    total_duration_sec: float,
    output_path: Path,
    sample_rate: int=48000,
) -> dict:
    if total_duration_sec<=0:
        raise AudioContractError("total duration must be positive")
    total_samples=int(round(total_duration_sec*sample_rate))
    mix=array("h",[0])*total_samples
    placements=[]
    for clip in sorted(clips,key=lambda row:(row["start_sec"],row["dialogue_id"])):
        path=Path(clip["path"])
        samples=read_pcm16_mono(path,sample_rate=sample_rate)
        start=int(round(float(clip["start_sec"])*sample_rate))
        end=start+len(samples)
        if start<0 or end>total_samples:
            raise AudioContractError(f"clip outside timeline: {clip['dialogue_id']}")
        for idx,value in enumerate(samples,start):
            summed=int(mix[idx])+int(value)
            mix[idx]=max(-32768,min(32767,summed))
        placements.append({
            "dialogue_id":clip["dialogue_id"],
            "start_sec":float(clip["start_sec"]),
            "duration_sec":round(len(samples)/sample_rate,6),
            "source_sha256":file_sha256(path),
        })
    write_pcm16_mono(output_path,mix,sample_rate=sample_rate)
    return {
        "path":str(output_path),
        "sample_rate":sample_rate,
        "duration_sec":round(total_samples/sample_rate,6),
        "bytes":output_path.stat().st_size,
        "sha256":file_sha256(output_path),
        "placements":placements,
    }
