import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/transcript-qa.py'
spec = importlib.util.spec_from_file_location('transcript_qa', SCRIPT)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def captions(words):
    return [{'text': word, 'startMs': index*300, 'endMs': index*300+250, 'confidence': .9} for index, word in enumerate(words.split())]

class TranscriptQATests(unittest.TestCase):
    def test_normalizes_punctuation_case_and_unicode_but_preserves_content(self):
        self.assertEqual(m.tokens('ÉÉN! Café, don’t — 123.'), ['één', 'café', "don't", '123'])
        result = m.evaluate('Dit is écht goed.', captions('DIT is écht goed'), 2, 'nl')
        self.assertEqual(result['wer'], 0)
        self.assertTrue(result['usable'])
        self.assertAlmostEqual(result['timing']['captionIntervalUnionSeconds'], 1)

    def test_dp_reports_substitution_deletion_insertion_and_wer_above_one(self):
        for reference, hypothesis, expected in [('one two three', 'one red three', 'substitution'), ('one two three', 'one three', 'deletion'), ('one three', 'one two three', 'insertion')]:
            result = m.evaluate(reference, captions(hypothesis), 3, 'en')
            self.assertEqual(result['alignment'][expected], 1)
        result = m.evaluate('one', captions('alpha beta gamma'), 3, 'en')
        self.assertEqual(result['wer'], 3)
        self.assertFalse(result['usable'])

    def test_invalid_timing_prevents_usable_even_with_exact_words(self):
        for updates in [{'startMs': -1}, {'endMs': 1001}, {'startMs': 200, 'endMs': 100}, {'startMs': None}, {'startMs': float('nan')}, {'endMs': float('inf')}]:
            words = captions('hello'); words[0].update(updates)
            result = m.evaluate('hello', words, 1, 'en')
            self.assertEqual(result['wer'], 0)
            self.assertFalse(result['usable'])
            self.assertTrue(result['timing']['invalid'])

    def test_overlaps_are_unioned_not_added_and_confidence_is_reported(self):
        words = [{'text':'one', 'startMs':0, 'endMs':800, 'confidence':.2}, {'text':'two', 'startMs':300, 'endMs':1000}]
        result = m.evaluate('one two', words, 1, 'en')
        self.assertEqual(result['timing']['captionIntervalUnionSeconds'], 1)
        self.assertEqual(result['confidence']['belowPointFive'], 1)
        self.assertEqual(result['confidence']['missing'], 1)
        self.assertEqual(result['timedReferenceWordCoverage'], 1)

    def test_empty_asr_and_nonmonotonic_words_fail_quality(self):
        self.assertEqual(m.evaluate('hello world', [], 1, 'en')['wer'], 1)
        words = captions('hello world'); words[1]['startMs'] = 0; words[0]['startMs'] = 10
        self.assertFalse(m.evaluate('hello world', words, 1, 'en')['usable'])

    def fixture(self, root, invalid=False, bad_words=False):
        manifest = []
        for language, script in [('nl','Dit werkt goed'), ('en','This works well')]:
            folder = root/'public'/'demos'/language; folder.mkdir(parents=True)
            words = captions('wrong wrong wrong' if bad_words else script)
            if invalid: words[-1]['endMs'] = 3000
            transcript = {'script':script, 'language':language, 'model':'tiny', 'captions':words}
            (folder/'transcript.json').write_text(json.dumps(transcript))
            (folder/'job.json').write_text(json.dumps({'job':{'duration':2, 'captions':words}}))
            manifest.append({'id':language, 'job':f'demos/{language}/job.json', 'duration':2, 'provenance':{'script':script, 'language':language}})
        path = root/'public'/'demos'/'manifest.json'; path.write_text(json.dumps(manifest))
        return path

    def test_real_manifest_loading_and_cli_quality_exit_behaviour(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); manifest = self.fixture(root)
            result = m.manifest_report(manifest)
            self.assertTrue(result['bothLanguagesTested']); self.assertTrue(result['usable'])
            self.assertEqual(result['languages']['nl']['microWer'], 0)
            data = json.loads(manifest.read_text()); data[0]['job'] = '../private.json'; manifest.write_text(json.dumps(data))
            with self.assertRaises(ValueError): m.manifest_report(manifest)
        for invalid, bad, strict, expected in [(False, True, False, 0), (False, True, True, 1), (True, False, False, 2)]:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory); manifest = self.fixture(root, invalid, bad); report = root/'qa.json'
                process = subprocess.run([sys.executable, str(SCRIPT), str(manifest), '--out', str(report)]+(['--require-usable'] if strict else []), capture_output=True, text=True)
                self.assertEqual(process.returncode, expected, process.stderr)
                self.assertFalse(json.loads(report.read_text())['usable'])

if __name__ == '__main__': unittest.main()
