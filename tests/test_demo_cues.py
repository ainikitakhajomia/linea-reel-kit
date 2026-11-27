import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

spec=importlib.util.spec_from_file_location('demos',Path(__file__).resolve().parents[1]/'scripts/demos.py')
demos=importlib.util.module_from_spec(spec);spec.loader.exec_module(demos)


def words(items):
    return [{'text':text,'startMs':round(onset*1000),'endMs':round(onset*1000)+100} for text,onset in items]


class SpeechCueTests(unittest.TestCase):
    def test_irregular_real_onsets_punctuation_accents_and_first_hook_preroll(self):
        captions=words([('Maandag,',.22),('op',1.1),('VRIJDAG!',1.43),('één',4.15),('proces.',4.53),('klaar',5.4)])
        cues=demos.speech_cues(captions,['maandag','vrijdag','een proces'],6)
        self.assertEqual([c['mode'] for c in cues],['exact-normalized-asr']*3)
        self.assertEqual([c['start'] for c in cues],[0,1.43,4.15])
        self.assertEqual(cues[0]['asrOnsetSeconds'],.22)
        self.assertAlmostEqual(cues[0]['duration'],1.43)
        self.assertAlmostEqual(cues[-1]['start']+cues[-1]['duration'],6)
        self.assertEqual(captions[3]['startMs'],4150)

    def test_unrecognized_phrase_falls_back_to_actual_irregular_word_onset(self):
        captions=words([('a',.1),('b',.3),('c',1.7),('d',2.65),('e',4.1),('f',4.7)])
        cues=demos.speech_cues(captions,['a','not recognized','e'],6)
        self.assertEqual(cues[1]['mode'],'actual-asr-word-quantile')
        self.assertEqual(cues[1]['asrToken'],'c')
        self.assertEqual(cues[1]['start'],1.7)
        self.assertIsNotNone(cues[1]['fallbackReason'])
        self.assertEqual(cues[2]['start'],4.1)

    def test_close_or_late_cues_get_reported_readability_constraints(self):
        captions=words([('a',.1),('b',.2),('c',1.95)])
        cues=demos.speech_cues(captions,['a','b','c'],2)
        self.assertEqual([c['start'] for c in cues],[0,.5,1.5])
        self.assertTrue(cues[1]['clampedForMinimumHold'])
        self.assertTrue(cues[2]['clampedForMinimumHold'])
        self.assertTrue(all(c['duration']>=.5 for c in cues))
        self.assertEqual(captions[-1]['startMs'],1950)

    def test_bad_or_missing_actual_word_times_are_rejected(self):
        for captions,duration in [([],6),(words([('a',1),('b',.5),('c',2)]),4),(words([('a',.1),('b',.2),('c',.3)]),1)]:
            with self.assertRaises(ValueError):demos.speech_cues(captions,['a','b','c'],duration)


class NativeDrawingTests(unittest.TestCase):
    def test_geometry_strokes_and_radius_are_native_and_angles_unchanged(self):
        draw=demos.NativeDraw.__new__(demos.NativeDraw);draw.draw=Mock()
        with patch.object(demos,'SCALE',2):
            draw.line((10,20,30,40),width=3,fill='#fff')
            draw.rounded_rectangle((1,2,30,40),8,fill='#fff')
            draw.pieslice((1,2,30,40),180,360,fill='#fff')
        draw.draw.line.assert_called_once_with((20,40,60,80),width=6,fill='#fff')
        draw.draw.rounded_rectangle.assert_called_once_with((2,4,60,80),16,fill='#fff')
        draw.draw.pieslice.assert_called_once_with((2,4,60,80),180,360,fill='#fff')

    def test_fonts_are_rasterized_at_native_size_without_loading_pixels(self):
        imagefont=Mock()
        demos.font.cache_clear()
        with patch.object(demos,'SCALE',2),patch.dict('sys.modules',{'PIL':SimpleNamespace(ImageFont=imagefont)}),patch.object(Path,'exists',return_value=True):
            demos.font(22,True)
        self.assertEqual(imagefont.truetype.call_args.args[1],44)
        demos.font.cache_clear()

if __name__=='__main__':unittest.main()
