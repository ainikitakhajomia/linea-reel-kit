import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "reel.py"
spec = importlib.util.spec_from_file_location("reel", SCRIPT)
reel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reel)


def caption(text, start, end):
    return {"text": text, "startMs": start, "endMs": end, "timestampMs": None, "confidence": None}


class TimingTests(unittest.TestCase):
    def test_silence_edit_keeps_word_and_maps_timestamps(self):
        words = [caption("quiet word", 3200, 3600), caption("later", 5100, 5500)]
        plan = reel.make_plan(6, [[1, 2.5], [3, 4]], words)
        self.assertEqual(len(plan["cuts"]), 1)
        self.assertAlmostEqual(plan["cuts"][0][0], 1.14)
        self.assertAlmostEqual(plan["cuts"][0][1], 2.36)
        mapped = reel.remap_captions(words, plan["clips"])
        self.assertEqual(mapped[0]["startMs"], 1980)
        self.assertEqual(mapped[1]["endMs"], 4280)

    def test_repeated_takes_require_optin_and_preserve_last(self):
        words = [caption("This is my first sentence.", 100, 1000), caption("This is my first sentence.", 2000, 3000)]
        safe = reel.make_plan(4, [], words)
        edited = reel.make_plan(4, [], words, remove_repeats=True)
        self.assertEqual(safe["cuts"], [])
        self.assertEqual(edited["cuts"], [[0.1, 1.0]])
        self.assertEqual(len(safe["repeatCandidates"]), 1)
        mapped = reel.remap_captions(words, edited["clips"])
        self.assertEqual(len(mapped), 1)
        self.assertEqual(mapped[0]["startMs"], 1100)

    def test_no_entire_source_removal(self):
        with self.assertRaises(ValueError):
            reel.complement([[0, 6]], 6)

    def test_cuts_merge_and_clamp(self):
        self.assertEqual(reel.merge_intervals([[-1, 2], [1.5, 4], [6, 9]], 8), [[0, 4], [6, 8]])

    def test_invalid_transcript_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text(json.dumps([caption("bad", 5000, 6000)]))
            with self.assertRaises(ValueError):
                reel.read_captions(path, 2)

    def test_manual_semantic_edl_recomputes_output_and_rejects_bad_cuts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "edl.json"
            reel.save(path, {"cuts": [[1, 3]]})
            plan = reel.apply_manual_cuts(reel.make_plan(5, [], []), path)
            self.assertEqual(plan["duration"], 3)
            self.assertEqual(plan["clips"][1]["outputStart"], 1)
            reel.save(path, {"cuts": [[3, 6]]})
            with self.assertRaises(ValueError):
                reel.apply_manual_cuts(plan, path)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class FFmpegIntegrationTests(unittest.TestCase):
    def test_source_to_edited_job_and_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source with spaces.mp4"
            reel.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=blue:s=160x240:r=30:d=3", "-f", "lavfi", "-i", "sine=frequency=440:duration=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", source])
            transcript = root / "transcript.json"
            reel.save(transcript, [caption("Hallo world.", 250, 2250)])
            out = root / "job"
            code = reel.main(["edit", str(source), "--transcript", str(transcript), "--out", str(out), "--width", "180", "--height", "320"])
            self.assertEqual(code, 0)
            result = reel.load(out / "job.json")["job"]
            self.assertGreater(result["duration"], 2.9)
            self.assertEqual(len(result["captions"]), 1)
            info, duration = reel.probe(out / "edited.mp4")
            self.assertTrue(reel.has_audio(info))
            self.assertAlmostEqual(duration, 3, delta=0.15)
            self.assertTrue(source.exists())
            reference = root / "reference.json"
            self.assertEqual(reel.main(["analyze-reference", str(source), "--out", str(reference)]), 0)
            self.assertEqual(reel.load(reference)["sceneChangesSeconds"], [])

    def test_audio_missing_gets_silent_track(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "silent.mp4"
            reel.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=160x240:r=30:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", source])
            self.assertEqual(reel.main(["edit", str(source), "--no-transcribe", "--out", str(root / "job"), "--width", "180", "--height", "320"]), 0)
            info, duration = reel.probe(root / "job" / "edited.mp4")
            self.assertTrue(reel.has_audio(info))
            self.assertAlmostEqual(duration, 1, delta=0.2)


if __name__ == "__main__":
    unittest.main()
