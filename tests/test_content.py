import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('content', ROOT / 'scripts/content.py')
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)


class ContentWorkspaceTests(unittest.TestCase):
    def test_derive_links_records_and_status_preserves_revisions(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            content.init(workspace)
            idea, reel, carousel = content.derive(workspace, 'Nieuwe workflow', 'Een Nederlands script.')
            self.assertEqual(reel['parentId'], idea['id'])
            self.assertEqual(carousel['parentId'], idea['id'])
            old = workspace / 'records' / reel['id'] / '000001.json'
            before = old.read_bytes()
            updated = content.change_status(workspace, reel['id'], 'ready')
            self.assertEqual(updated['revision'], 2)
            self.assertEqual(old.read_bytes(), before)
            self.assertEqual(len(content.records(workspace)), 3)
            self.assertEqual(next(r for r in content.records(workspace) if r['id'] == reel['id'])['status'], 'ready')
            with self.assertRaisesRegex(ValueError, 'transition'):
                content.change_status(workspace, idea['id'], 'published')

    def test_incompatible_workspace_and_malformed_state_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            manifest = workspace / 'workspace.json'
            manifest.write_text('{"userData":true}')
            before = manifest.read_bytes()
            with self.assertRaisesRegex(ValueError, 'incompatible'):
                content.init(workspace)
            self.assertEqual(manifest.read_bytes(), before)
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            content.init(workspace)
            record = content.add(workspace, 'Idea')
            path = workspace / 'records' / record['id'] / '000001.json'
            record['status'] = 'unknown'
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, 'status'):
                content.records(workspace)

    def test_writer_lock_and_empty_script_do_not_create_records(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace = Path(folder)
            content.init(workspace)
            with content.locked(workspace):
                with self.assertRaisesRegex(ValueError, 'active writer'):
                    content.add(workspace, 'Concurrent')
            with self.assertRaisesRegex(ValueError, 'empty'):
                content.derive(workspace, 'Empty', '   ')
            self.assertEqual(content.records(workspace), [])


if __name__ == '__main__':
    unittest.main()
