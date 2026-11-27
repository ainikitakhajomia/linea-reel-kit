import importlib.util
import json
import re
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audio', ROOT / 'scripts/audio.py')
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg required')
class AudioMixTests(unittest.TestCase):
    def test_real_mix_preserves_video_and_duration_with_nonzero_audio(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source, music, output = folder / 'voice.mp4', folder / 'music.wav', folder / 'final.mp4'
            audio.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=32x32:r=10:d=1',
                       '-f', 'lavfi', '-i', 'sine=frequency=600:duration=1', '-c:v', 'libx264', '-c:a', 'aac', '-t', '1', source])
            audio.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=220:duration=0.25', music])
            job = folder / 'job.json'
            job.write_text(json.dumps({'job': {'effects': [{'id': 'pop', 'start': .2}]}}))
            source_bytes = source.read_bytes()
            result = audio.mix(source, output, music, job)
            info = audio.probe(output)
            self.assertLess(abs(float(info['format']['duration']) - 1), .1)
            self.assertTrue(result['videoCopy'])
            self.assertTrue(result['twoPass'])
            self.assertTrue(result['musicDucked'])
            self.assertEqual(result['sfxEvents'], 1)
            self.assertEqual(next(stream for stream in info['streams'] if stream['codec_type'] == 'audio')['codec_name'], 'aac')
            raw = audio.run(['ffmpeg', '-v', 'error', '-i', output, '-vn', '-f', 's16le', '-ac', '1', '-']).stdout
            samples = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
            self.assertGreater(max(abs(sample) for sample in samples), 100)
            measure = audio.run(['ffmpeg', '-hide_banner', '-i', output, '-af',
                                 'loudnorm=I=-16:TP=-1.5:print_format=json', '-f', 'null', '-'])
            measured = json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', measure.stderr.decode(), re.S)[-1])
            self.assertLess(abs(float(measured['input_i']) + 16), 1, 'encoded audio should approach -16 LUFS')
            self.assertLessEqual(float(measured['input_tp']), -.8, 'AAC true peak should remain below clipping with tolerance')
            self.assertEqual(source.read_bytes(), source_bytes)
            # Copy means exact compressed video packets survive the finishing pass.
            hashes = []
            for path in [source, output]:
                hashes.append(audio.run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:v:0', '-c', 'copy', '-f', 'hash', '-']).stdout)
            self.assertEqual(*hashes)
            with self.assertRaisesRegex(ValueError, 'differ'):
                audio.mix(source, source)
            with self.assertRaisesRegex(ValueError, 'exists'):
                audio.mix(source, output)

    def test_sound_synthesis_is_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = [Path(temp) / 'a.wav', Path(temp) / 'b.wav']
            for path in paths:
                audio.synthesize(path, .3, [(.05, 'caption')])
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())


if __name__ == '__main__':
    unittest.main()
