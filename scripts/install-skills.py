#!/usr/bin/env python3
"""Install the shared Reel Kit skill into user-level Codex/Claude skill discovery."""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

TOKEN = "__REEL_KIT_HOME__"
NAME = "linea-reel-kit"


def install(repo, destinations, *, force=False, dry_run=False):
    repo = Path(repo).expanduser().resolve()
    required = (repo / "scripts/reel.py", repo / "src/catalog.json", repo / "package.json", repo / f"skills/{NAME}/SKILL.md")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise ValueError("Invalid toolkit checkout; missing: " + ", ".join(missing))
    source = required[-1].read_text()
    if TOKEN not in source:
        raise ValueError("Canonical skill has no repository-path installation marker")
    content = source.replace(TOKEN, json.dumps(str(repo), ensure_ascii=False))
    targets = [Path(base).expanduser().resolve() / "skills" / NAME / "SKILL.md" for base in destinations]
    # Check all targets before writing any: mixed Codex/Claude installs must not partly overwrite.
    for target in targets:
        if target.exists() and not force:
            raise ValueError(f"Existing skill preserved: {target}. Use --force only to replace this skill file.")
        if target.is_symlink() or any(parent.is_symlink() for parent in list(target.parents)[:2]):
            raise ValueError(f"Refusing symlinked skill destination: {target}")
    if dry_run:
        return targets
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=".skill-", dir=target.parent)
        try:
            with os.fdopen(descriptor, "w") as stream:
                stream.write(content)
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return targets


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Absolute or relative checkout to bind into the installed skill")
    parser.add_argument("--codex", action="store_true")
    parser.add_argument("--claude", action="store_true")
    parser.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    parser.add_argument("--claude-home", default=os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    parser.add_argument("--force", action="store_true", help="Replace only the named SKILL.md; preserve unrelated files")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    destinations = ([args.codex_home] if args.codex else []) + ([args.claude_home] if args.claude else [])
    if not destinations:
        parser.error("Choose --codex, --claude or both")
    try:
        for target in install(args.repo, destinations, force=args.force, dry_run=args.dry_run):
            print(f"{'Would install' if args.dry_run else 'Installed'}: {target}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"install-skills: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
