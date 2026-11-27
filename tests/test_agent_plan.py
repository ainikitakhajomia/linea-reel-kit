import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('agent_plan', Path(__file__).resolve().parents[1]/'scripts/agent-plan.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AgentPlanTests(unittest.TestCase):
    def test_composed_request_preserves_both_media_requirements(self):
        result = m.plan('Combineer talking head met softwarewalkthrough en tekst achter mij', {'source':'owned.mp4'})
        self.assertIn('behind-speaker', result['routes'])
        self.assertIn('walkthrough', result['routes'])
        self.assertEqual(result['missingInputs'], ['walkthrough'])
        self.assertIn('segment-edited-video', result['operations'])
        self.assertLess(result['operations'].index('edit'), result['operations'].index('segment-edited-video'))

    def test_missing_media_is_not_treated_as_ready(self):
        result = m.plan('Maak een slideshow vanuit dit script', {'script':'script.txt'})
        self.assertEqual(result['state'], 'needs-inputs')
        self.assertEqual(result['missingInputs'], ['images'])

    def test_five_variants_are_distinct_and_use_catalog(self):
        result = m.plan('Edit this talking head', {'source':'owned.mp4'}, 5)
        self.assertEqual(result['state'], 'ready-for-agent-authoring')
        self.assertEqual(len({x['editorialDirection'] for x in result['variants']}), 5)
        self.assertEqual(len({tuple(x['candidateEffects']) for x in result['variants']}), 5)

    def test_script_reel_does_not_invent_a_filmed_speaker_requirement(self):
        result = m.plan('Maak een complete Instagram Reel vanuit dit script', {'script':'owned.txt'})
        self.assertEqual(result['routes'], ['script-reel'])
        self.assertEqual(result['missingInputs'], [])
        self.assertNotIn('transcribe', result['operations'])

    def test_variant_count_is_inferred_from_user_brief(self):
        self.assertEqual(len(m.plan('Maak vijf creatieve varianten')['variants']), 5)
        self.assertEqual(len(m.plan('Make three versions')['variants']), 3)

    def test_catalog_drift_and_invalid_input_fail(self):
        with self.assertRaises(ValueError): m.plan('talking head', catalog=[{'id':'other'}])
        with self.assertRaises(ValueError): m.plan('')
        with self.assertRaises(ValueError): m.plan('talking head', count=6)

if __name__ == '__main__': unittest.main()
