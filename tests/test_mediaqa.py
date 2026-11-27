import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mediaqa", ROOT / "scripts/validate-media.py")
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class MediaQATests(unittest.TestCase):
    def test_actual_black_silent_fixture_reports_intervals_and_missing_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, report_path = root / "black fixture.mp4", root / "report.json"
            qa.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=160x240:r=30:d=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", source])
            original_hash = qa.sha256(source)
            self.assertEqual(qa.main([str(source), "--out", str(report_path)]), 0)
            report = json.loads(report_path.read_text())
            self.assertEqual(report["video"]["width"], 160)
            self.assertEqual(report["video"]["height"], 240)
            self.assertAlmostEqual(report["durationSeconds"], 2, delta=0.1)
            self.assertFalse(report["audio"]["present"])
            self.assertTrue(any(x["code"] == "missing-audio" for x in report["warnings"]))
            self.assertGreaterEqual(report["blackIntervals"][0]["duration"], 1.9)
            self.assertGreaterEqual(report["staticIntervals"][0]["duration"], 1.9)
            self.assertEqual(original_hash, qa.sha256(source))

    def test_actual_moving_fixture_measures_loudness_and_no_black(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "moving.mp4"
            qa.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=160x240:r=30:d=2", "-f", "lavfi", "-i", "sine=frequency=440:duration=2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", source])
            report = qa.validate_media(source)
            self.assertTrue(report["audio"]["present"])
            self.assertIsInstance(report["audio"]["loudness"]["integratedLUFS"], float)
            self.assertIsInstance(report["audio"]["loudness"]["truePeakDBTP"], float)
            self.assertEqual(report["blackIntervals"], [])

    def test_source_cannot_be_overwritten_by_report(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.mp4"
            source.write_bytes(b"source")
            self.assertEqual(qa.main([str(source), "--out", str(source)]), 2)
            self.assertEqual(source.read_bytes(), b"source")


if __name__ == "__main__":
    unittest.main()
