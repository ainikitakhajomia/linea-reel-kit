import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/story.py'
spec=importlib.util.spec_from_file_location('story',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class StoryTests(unittest.TestCase):
 def test_no_overlap_and_readability(self):
  b={'accent':'#27335f','foreground':'#111316','background':'#f6f5f1'};x=m.storyboard('Dit is een hook. Dit is bewijs. Doe mee.',b);job=x['job'];self.assertEqual(job['brand'],b);self.assertEqual(len(job['effects']),3)
  for before,after in zip(job['effects'],job['effects'][1:]):self.assertAlmostEqual(before['start']+before['duration'],after['start'],places=2)
  self.assertEqual(m.feedback(job)['issues'],[])
 def test_safe_svg_text_and_empty_script(self):
  b={'accent':'#27335f','foreground':'#111316','background':'#f6f5f1'};svg=m.svg_slide('<script>alert(1)</script>',0,1,b);self.assertNotIn('<script>',svg);self.assertIn('&lt;script&gt;',svg)
  with self.assertRaises(ValueError):m.storyboard('',b)
