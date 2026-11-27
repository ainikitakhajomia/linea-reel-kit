#!/usr/bin/env python3
"""Small offline content workspace with immutable JSON record revisions."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import uuid

SCHEMA = 1
KINDS = {'idea', 'reel', 'carousel', 'slideshow', 'linkedin'}
STATES = {'idea', 'draft', 'ready', 'rendered', 'published', 'archived'}
TRANSITIONS = {
    'idea': {'draft', 'archived'}, 'draft': {'ready', 'archived'},
    'ready': {'draft', 'rendered', 'published', 'archived'},
    'rendered': {'draft', 'published', 'archived'}, 'published': {'archived'},
    'archived': {'draft'},
}


def now():
    return datetime.now(timezone.utc).isoformat()


def write_new(path, data):
    # Exclusive creation never replaces an existing file or revision.
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def init(workspace):
    workspace = Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    manifest = workspace / 'workspace.json'
    expected = {'schemaVersion': SCHEMA, 'tool': 'linea-reel-kit-content'}
    if manifest.exists():
        if json.loads(manifest.read_text()) != expected:
            raise ValueError('Existing workspace manifest is incompatible; no files changed')
    else:
        write_new(manifest, expected)
    (workspace / 'records').mkdir(exist_ok=True)
    return {'workspace': str(workspace.resolve()), **expected}


def require_workspace(workspace):
    workspace = Path(workspace)
    manifest = workspace / 'workspace.json'
    if not manifest.is_file() or json.loads(manifest.read_text()) != {'schemaVersion': SCHEMA, 'tool': 'linea-reel-kit-content'}:
        raise ValueError('Run content.py init first, or select a compatible workspace')
    return workspace


@contextmanager
def locked(workspace):
    workspace = require_workspace(workspace)
    lock = workspace / '.write-lock'
    try:
        handle = lock.open('x')
    except FileExistsError as exc:
        raise ValueError('Content workspace has an active writer; retry after it finishes') from exc
    try:
        handle.close()
        yield workspace
    finally:
        lock.unlink()


def validate_record(record):
    if not isinstance(record, dict) or record.get('schemaVersion') != SCHEMA:
        raise ValueError('Invalid content record schema')
    if not re.fullmatch(r'[0-9a-f]{12}', str(record.get('id', ''))):
        raise ValueError('Invalid record id')
    if record.get('kind') not in KINDS or record.get('status') not in STATES:
        raise ValueError('Invalid record kind or status')
    if not isinstance(record.get('revision'), int) or record['revision'] < 1:
        raise ValueError('Invalid record revision')
    if not isinstance(record.get('title'), str) or not record['title'].strip():
        raise ValueError('Record needs a nonempty title')
    if not isinstance(record.get('script'), str):
        raise ValueError('Record script must be text')
    if record.get('parentId') is not None and not re.fullmatch(r'[0-9a-f]{12}', str(record['parentId'])):
        raise ValueError('Invalid parent id')
    return record


def records(workspace):
    workspace = require_workspace(workspace)
    result = []
    for directory in sorted((workspace / 'records').iterdir()):
        if not directory.is_dir() or not re.fullmatch(r'[0-9a-f]{12}', directory.name):
            raise ValueError(f'Unexpected file in records workspace: {directory.name}')
        revisions = sorted(directory.glob('*.json'))
        if not revisions:
            raise ValueError(f'Record has no revision: {directory.name}')
        record = validate_record(json.loads(revisions[-1].read_text()))
        if record['id'] != directory.name or revisions[-1].stem != f"{record['revision']:06d}":
            raise ValueError('Record id/revision does not match storage path')
        result.append(record)
    return result


def create_record(workspace, title, kind, script='', parent=None):
    record = {'schemaVersion': SCHEMA, 'id': uuid.uuid4().hex[:12], 'revision': 1,
              'kind': kind, 'title': title.strip(), 'status': 'idea' if kind == 'idea' else 'draft',
              'script': script, 'parentId': parent, 'createdAt': now(), 'updatedAt': now()}
    validate_record(record)
    directory = workspace / 'records' / record['id']
    directory.mkdir()  # random collision fails safely; never reuse an existing record directory
    try:
        write_new(directory / '000001.json', record)
    except Exception:
        directory.rmdir()
        raise
    return record


def add(workspace, title, kind='idea', script=''):
    with locked(workspace) as workspace:
        return create_record(workspace, title, kind, script)


def change_status(workspace, identity, status):
    if status not in STATES:
        raise ValueError('Unknown content status')
    with locked(workspace) as workspace:
        matches = [record for record in records(workspace) if record['id'] == identity]
        if not matches:
            raise ValueError('Record not found')
        record = matches[0]
        if record['status'] == status:
            return record
        if status not in TRANSITIONS[record['status']]:
            raise ValueError(f"Invalid status transition: {record['status']} → {status}")
        record = {**record, 'status': status, 'revision': record['revision'] + 1, 'updatedAt': now()}
        validate_record(record)
        write_new(workspace / 'records' / identity / f"{record['revision']:06d}.json", record)
        return record


def derive(workspace, title, script):
    if not script.strip():
        raise ValueError('Cannot derive content from an empty script')
    with locked(workspace) as workspace:
        created = []
        try:
            idea = create_record(workspace, title, 'idea', script)
            created.append(idea)
            for kind in ['reel', 'carousel']:
                created.append(create_record(workspace, f'{title} · {kind}', kind, script, idea['id']))
            return created
        except Exception:
            # Roll back only this batch's new files; previous user records remain untouched.
            for record in created:
                directory = workspace / 'records' / record['id']
                (directory / '000001.json').unlink()
                directory.rmdir()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', default='out/content')
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ['init', 'list', 'add', 'status', 'derive']:
        child = sub.add_parser(command)
        child.add_argument('--workspace', default=argparse.SUPPRESS)
        if command in ['add', 'derive']:
            child.add_argument('--title', required=True)
            child.add_argument('--script', type=Path, required=command == 'derive', help='UTF-8 script text file')
        if command == 'add':
            child.add_argument('--kind', choices=sorted(KINDS), default='idea')
        if command == 'list':
            child.add_argument('--status', choices=sorted(STATES))
            child.add_argument('--kind', choices=sorted(KINDS))
        if command == 'status':
            child.add_argument('id')
            child.add_argument('state', choices=sorted(STATES))
    args = parser.parse_args()
    try:
        if args.command == 'init':
            result = init(args.workspace)
        elif args.command == 'list':
            result = [record for record in records(args.workspace)
                      if (not args.status or record['status'] == args.status) and (not args.kind or record['kind'] == args.kind)]
        elif args.command == 'status':
            result = change_status(args.workspace, args.id, args.state)
        else:
            script = args.script.read_text(encoding='utf-8') if args.script else ''
            result = derive(args.workspace, args.title, script) if args.command == 'derive' else add(args.workspace, args.title, args.kind, script)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'Content workspace error: {exc}\n')


if __name__ == '__main__':
    main()
