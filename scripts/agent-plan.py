#!/usr/bin/env python3
"""Turn a natural-language editing brief into an input-aware, reviewable local plan.

This routes capabilities, not semantic take selection or reference-style perception.
The coding agent reviews the plan, authors the timeline and executes its operations.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = [
    ('behind-speaker', r'achter (?:mij|me|de spreker)|behind (?:me|the speaker)|behind[- ]speaker', ['kinetic-hook', 'code-body'], ['source', 'foreground'], ['edit', 'segment-edited-video', 'author-behind-speaker-timeline']),
    ('walkthrough', r'walkthrough|screen ?record|schermopname|software', ['video-card', 'live-cursor', 'page-scroll'], ['source', 'walkthrough'], ['edit', 'align-screen-actions-to-speech', 'author-split-screen-timeline']),
    ('slideshow', r'slideshow|slide ?show|diavoorstelling', ['magazine-cover', 'storyboard-deck', 'picture-dive'], ['script', 'images'], ['storyboard', 'author-image-scenes']),
    ('product', r'saas|productvideo|product video', ['prompt-bar', 'layer-explode', 'live-cursor'], ['walkthrough'], ['analyze-product-evidence', 'author-product-timeline']),
    ('typography', r'kinetic|kinetisch|typograf|typograph', ['kinetic-hook', 'word-stamp', 'intertitle'], ['script'], ['storyboard', 'author-word-timing']),
    ('humor', r'humor|grappig|funny|comedy', ['comment-thread', 'receipt-printer', 'impact-frame'], ['script'], ['review-joke-setup-payoff', 'author-reaction-timing']),
    ('storytelling', r'storytelling|verhaal|story video', ['screenplay-page', 'video-card', 'intertitle'], ['script'], ['author-story-arc', 'author-evidence-scenes']),
    ('3d', r'\b3d\b|diepte|depth', ['layer-explode', 'orbit-ring', 'room-doors'], [], ['author-perspective-scenes']),
]
VARIANTS = [
    ('editorial', 'Lead with the clearest claim; fewer cuts and generous reading time.', ['kinetic-hook', 'video-card', 'intertitle']),
    ('proof-first', 'Open on visible product evidence, then explain the outcome.', ['video-card', 'live-cursor', 'word-stamp']),
    ('question', 'Use a specific audience question; reveal the answer after evidence.', ['comment-thread', 'prompt-bar', 'follow-chip']),
    ('contrast', 'Make the before/after visible with matched framing and a clear transition.', ['grid-collapse', 'shape-transitions', 'giant-captions']),
    ('story', 'Use setup, friction, resolution; keep the original speaker wording.', ['screenplay-page', 'video-backdrop', 'intertitle']),
]

def plan(brief, available=None, count=None, catalog=None):
    if not brief.strip():
        raise ValueError('Brief is empty')
    if count is None:
        match = re.search(r'\b([1-5]|een|twee|drie|vier|vijf|one|two|three|four|five)\s+(?:creatieve |creative )?(?:varianten|variants|versies|versions)\b', brief.lower())
        numbers = {'een':1,'twee':2,'drie':3,'vier':4,'vijf':5,'one':1,'two':2,'three':3,'four':4,'five':5}
        count = numbers.get(match[1], int(match[1]) if match and match[1].isdigit() else 1) if match else 1
    if not 1 <= count <= 5:
        raise ValueError('Choose between 1 and 5 variants')
    available = dict(available or {})
    known = {x['id'] for x in (catalog or json.loads((ROOT/'src/catalog.json').read_text()))}
    normalized = brief.lower()
    routes = [rule for rule in RULES if re.search(rule[1], normalized)]
    if not routes and (available.get('script') or re.search(r'vanuit (?:dit|een|het) script|from (?:this |a |the )?script', normalized)):
        routes = [('script-reel', '', ['kinetic-hook', 'storyboard-deck', 'intertitle'], ['script'], ['storyboard', 'author-scene-evidence', 'author-word-timing'])]
    if not routes:
        routes = [('talking-head', '', ['kinetic-hook', 'giant-captions', 'video-card'], ['source'], ['transcribe', 'review-semantic-edl', 'edit', 'author-speech-aligned-effects'])]
    # Caption-first edits and silence/bad-take removal remain relevant with other routes.
    editing = bool(re.search(r'talking.?head|takes|stilte|silence|captions|ondertitel|spreker', normalized))
    requirements = list(dict.fromkeys(item for rule in routes for item in rule[3]))
    if editing and 'source' not in requirements:
        requirements.insert(0, 'source')
    operations = list(dict.fromkeys((['transcribe', 'review-semantic-edl', 'edit'] if editing else []) + [item for rule in routes for item in rule[4]]))
    missing = [item for item in requirements if not available.get(item)]
    # Foreground is derived from the edited source, not a separately required user upload.
    if 'foreground' in missing and available.get('source'):
        missing.remove('foreground')
    selected = list(dict.fromkeys(effect for rule in routes for effect in rule[2]))
    unknown = [effect for effect in selected if effect not in known]
    if unknown:
        raise ValueError('Catalog does not support selected effects: ' + ', '.join(unknown))
    variants = []
    for index in range(count):
        name, direction, vocabulary = VARIANTS[index]
        variants.append({'name': name, 'editorialDirection': direction, 'candidateEffects': [x for x in vocabulary if x in known], 'requiresDistinctHookAndSceneOrder': count > 1})
    return {
        'schemaVersion': 1, 'brief': brief, 'brand': 'brands/studio-linea.json',
        'routes': [rule[0] for rule in routes], 'inputs': available, 'missingInputs': missing,
        'state': 'needs-inputs' if missing else 'ready-for-agent-authoring',
        'candidateEffects': selected, 'operations': operations + ['review-timeline', 'render-on-permitted-host', 'inspect-moving-export', 'validate-media'],
        'variants': variants, 'effectBudget': {'simultaneousPrimaryIdeas': 1, 'initialRecipesPerShort': 3},
        'decisionsForAgent': ['Inspect actual reference timing, composition, easing and audio when supplied.', 'Choose complete takes by meaning and delivery; silence and exact-repeat heuristics cannot decide this.', 'Align effects to transcript evidence; do not invent word timestamps for untranscribed speech.', 'Use provided/owned media; report missing inputs instead of inventing a filmed person.'],
        'limitations': ['Plan only: no media was edited, segmented, rendered or visually validated.', 'Catalog recipes are independent implementations, not verified reference-quality equivalents.', '3D recipes use projected 2.5D Canvas geometry; no physical 3D scene/lighting engine.', 'Portrait segmentation and optical tracking require separate inference and export inspection.'],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('brief', help='Natural-language Dutch or English editing request')
    parser.add_argument('--out', type=Path, required=True)
    for item in ['source', 'walkthrough', 'script', 'images', 'reference']:
        parser.add_argument('--'+item, type=Path)
    parser.add_argument('--variants', type=int, help='Override count inferred from the brief (1–5)')
    args = parser.parse_args()
    inputs = {}
    for item in ['source', 'walkthrough', 'script', 'images', 'reference']:
        value = getattr(args, item)
        if value:
            value = value.expanduser().resolve()
            if not value.exists():
                parser.error(f'{item} input does not exist: {value}')
            inputs[item] = str(value)
    try:
        result = plan(args.brief, inputs, args.variants)
    except ValueError as error:
        parser.error(str(error))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'plan': str(args.out), 'state': result['state'], 'missingInputs': result['missingInputs']}))

if __name__ == '__main__':
    main()
