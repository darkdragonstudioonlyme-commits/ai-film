from array import array
from pathlib import Path
import tempfile
import unittest
import wave

from film.audio import AudioContractError, mix_dialogue_timeline


def write_wav(path: Path, samples: list[int], rate: int=48000):
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        wav.writeframes(array("h",samples).tobytes())


class AudioTests(unittest.TestCase):
    def test_mix_places_clip_on_timeline(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            clip=root/"clip.wav"
            write_wav(clip,[1000]*480)
            out=root/"mix.wav"
            result=mix_dialogue_timeline(
                [{"dialogue_id":"d1","start_sec":0.01,"path":str(clip)}],
                total_duration_sec=0.05,
                output_path=out,
            )
            self.assertEqual(result["duration_sec"],0.05)
            with wave.open(str(out),"rb") as wav:
                samples=array("h"); samples.frombytes(wav.readframes(wav.getnframes()))
            self.assertTrue(all(v==0 for v in samples[:480]))
            self.assertTrue(all(v==1000 for v in samples[480:960]))

    def test_out_of_timeline_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            clip=root/"clip.wav"; write_wav(clip,[1]*4800)
            with self.assertRaises(AudioContractError):
                mix_dialogue_timeline(
                    [{"dialogue_id":"d1","start_sec":0.05,"path":str(clip)}],
                    total_duration_sec=0.10,
                    output_path=root/"mix.wav",
                )


if __name__=="__main__":
    unittest.main()
