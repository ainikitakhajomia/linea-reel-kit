"""Real FFmpeg pixel/alpha verification, without ML dependencies or browser rendering."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('segment', ROOT / 'scripts/segment.py')
segment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(segment)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg is required')
class SegmentationTests(unittest.TestCase):
    def test_chromakey_alpha_sequence_and_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source, output = folder / 'synthetic.mkv', folder / 'foreground'
            segment.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
                         'color=c=0x00ff00:s=32x32:r=5:d=0.4,drawbox=x=8:y=8:w=16:h=16:color=red:t=fill',
                         '-c:v', 'ffv1', source])
            before = source.read_bytes()
            metadata = segment.segment(source, output)
            self.assertEqual(metadata['frames'], 2)
            self.assertEqual(metadata['fps'], 5)
            self.assertTrue((output / '000000.png').is_file())
            self.assertTrue((output / '000001.png').is_file())
            self.assertEqual(json.loads((output / 'metadata.json').read_text())['alpha'], True)
            pixels = segment.run(['ffmpeg', '-v', 'error', '-i', output / '000000.png',
                                  '-f', 'rawvideo', '-pix_fmt', 'rgba', '-']).stdout
            self.assertEqual(len(pixels), 32 * 32 * 4)
            self.assertLess(pixels[(2 * 32 + 2) * 4 + 3], 5, 'green background should be transparent')
            self.assertGreater(pixels[(16 * 32 + 16) * 4 + 3], 250, 'red subject should stay opaque')
            self.assertEqual(before, source.read_bytes(), 'source media must remain unchanged')
            with self.assertRaisesRegex(ValueError, 'empty'):
                segment.segment(source, output)

    def test_color_rejects_filter_injection_before_ffmpeg(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'exists.mp4'
            source.write_bytes(b'not needed: validate arguments before probing')
            with self.assertRaisesRegex(ValueError, 'hexadecimal'):
                segment.segment(source, Path(folder) / 'out', color='green,scale=1:1')


if __name__ == '__main__':
    unittest.main()
