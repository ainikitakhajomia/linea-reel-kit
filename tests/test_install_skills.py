import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("install_skills", ROOT / "scripts/install-skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallSkillsTests(unittest.TestCase):
    def test_absolute_binding_in_an_unrelated_directory_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "unrelated user directory"
            targets = installer.install(ROOT, [home])
            target = targets[0]
            content = target.read_text()
            self.assertIn(str(ROOT), content)
            self.assertNotIn(installer.TOKEN, content)
            target.write_text("user edited skill")
            with self.assertRaises(ValueError):
                installer.install(ROOT, [home])
            self.assertEqual(target.read_text(), "user edited skill")
            unrelated = target.parent / "notes.txt"
            unrelated.write_text("preserve")
            installer.install(ROOT, [home], force=True)
            self.assertEqual(unrelated.read_text(), "preserve")
            self.assertEqual(target.read_text(), content)

    def test_dry_run_is_readonly_and_multi_target_conflict_is_preflighted(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory) / "first", Path(directory) / "second"
            installer.install(ROOT, [first], dry_run=True)
            self.assertFalse(first.exists())
            installer.install(ROOT, [second])
            with self.assertRaises(ValueError):
                installer.install(ROOT, [first, second])
            self.assertFalse(first.exists())

    def test_invalid_repository_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "target"
            with self.assertRaises(ValueError):
                installer.install(directory, [home])
            self.assertFalse(home.exists())


if __name__ == "__main__":
    unittest.main()
