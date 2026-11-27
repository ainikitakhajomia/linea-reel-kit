#!/usr/bin/env python3
"""Measure actual NL/EN ASR output against demonstration scripts, without acoustic sync claims."""
from __future__ import annotations
import argparse
import json
import math
import statistics
import unicodedata
from pathlib import Path


def tokens(text):
    normalized = unicodedata.normalize('NFKC', str(text)).casefold().replace('’', "'")
    # Keep internal apostrophes, accents and numbers; punctuation is not a word error.
    words, current = [], []
    for character in normalized:
        if character.isalnum() or (character == "'" and current):
            current.append(character)
        elif current:
            words.append(''.join(current).strip("'")); current = []
    if current:
        words.append(''.join(current).strip("'"))
    return [word for word in words if word]


def align(reference, hypothesis):
    """Levenshtein DP with deterministic match/substitution/deletion/insertion ties."""
    rows = [[(0, []) for _ in range(len(hypothesis)+1)] for _ in range(len(reference)+1)]
    for i in range(1, len(reference)+1): rows[i][0] = (i, [('deletion', index-1, None) for index in range(1, i+1)])
    for j in range(1, len(hypothesis)+1): rows[0][j] = (j, [('insertion', None, index-1) for index in range(1, j+1)])
    for i, word in enumerate(reference, 1):
        for j, recognized in enumerate(hypothesis, 1):
            equal = word == recognized
            previous = rows[i-1][j-1]
            choices = [(previous[0]+(not equal), previous[1]+[('match' if equal else 'substitution', i-1, j-1)])]
            previous = rows[i-1][j]; choices.append((previous[0]+1, previous[1]+[('deletion', i-1, None)]))
            previous = rows[i][j-1]; choices.append((previous[0]+1, previous[1]+[('insertion', None, j-1)]))
            rows[i][j] = min(choices, key=lambda item: item[0])
    operations = rows[-1][-1][1]
    counts = {name: sum(operation[0] == name for operation in operations) for name in ['match', 'substitution', 'deletion', 'insertion']}
    return counts, operations


def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def evaluate(script, captions, duration, language, max_wer=.35, min_timed_coverage=.65):
    if not finite_number(duration) or duration <= 0:
        raise ValueError('Manifest duration must be finite and positive')
    if language not in ('nl', 'en'):
        raise ValueError('Expected explicitly identified nl or en narration')
    reference = tokens(script)
    if not reference:
        raise ValueError('Ground truth script has no normalized words')
    hypothesis, owners, intervals, invalid, confidence, missing_confidence = [], [], [], [], [], 0
    previous_start = -1
    valid_captions = set()
    for index, caption in enumerate(captions):
        words = tokens(caption.get('text', ''))
        hypothesis.extend(words); owners.extend([index]*len(words))
        start, end = caption.get('startMs'), caption.get('endMs')
        reason = None
        if not finite_number(start) or not finite_number(end): reason = 'missing/non-finite milliseconds'
        elif start < 0 or end <= start: reason = 'non-positive or reversed interval'
        elif end > duration*1000: reason = 'word extends beyond manifest duration'
        elif start < previous_start: reason = 'word starts are not monotonic'
        if finite_number(start): previous_start = start
        if reason: invalid.append({'caption': index, 'reason': reason, 'startMs': start if finite_number(start) or start is None else str(start), 'endMs': end if finite_number(end) or end is None else str(end)})
        else:
            valid_captions.add(index); intervals.append((start/1000, end/1000))
        probability = caption.get('confidence')
        if probability is None: missing_confidence += 1
        elif not finite_number(probability) or not 0 <= probability <= 1:
            invalid.append({'caption': index, 'reason': 'confidence outside [0,1]'})
        else: confidence.append(probability)
    counts, operations = align(reference, hypothesis)
    wer = sum(counts[name] for name in ['substitution', 'deletion', 'insertion'])/len(reference)
    matched_timed = sum(operation == 'match' and owners[hyp] in valid_captions for operation, _, hyp in operations)
    union, last_end = 0.0, 0.0
    for start, end in sorted(intervals):
        union += max(0, end-max(start, last_end)); last_end = max(last_end, end)
    timed_coverage = matched_timed/len(reference)
    usable = bool(captions) and not invalid and wer <= max_wer and timed_coverage >= min_timed_coverage
    return {
        'language': language, 'referenceWords': len(reference), 'recognizedWords': len(hypothesis),
        'wer': wer, 'alignment': counts, 'referenceWordCoverage': counts['match']/len(reference),
        'timedReferenceWordCoverage': timed_coverage, 'durationSeconds': duration,
        'timing': {'validCaptionCount': len(valid_captions), 'captionCount': len(captions), 'invalid': invalid, 'captionIntervalUnionSeconds': union, 'fractionOfVideoCoveredByCaptionIntervals': union/duration},
        'confidence': {'observed': len(confidence), 'missing': missing_confidence, 'mean': statistics.mean(confidence) if confidence else None, 'minimum': min(confidence) if confidence else None, 'belowPointFive': sum(value < .5 for value in confidence)},
        'thresholds': {'maximumWer': max_wer, 'minimumTimedReferenceWordCoverage': min_timed_coverage},
        'usable': usable, 'normalizedReference': reference, 'normalizedHypothesis': hypothesis,
        'errors': [{'operation': kind, 'reference': reference[ref] if ref is not None else None, 'hypothesis': hypothesis[hyp] if hyp is not None else None} for kind, ref, hyp in operations if kind != 'match'],
    }


def contained(root, relative):
    path = (root/relative).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('Manifest path escapes public root')
    return path


def manifest_report(manifest_path, public_root=None, max_wer=.35, min_timed_coverage=.65):
    manifest_path = Path(manifest_path).resolve()
    public_root = Path(public_root).resolve() if public_root else manifest_path.parent.parent
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, list) or not manifest: raise ValueError('Expected nonempty demonstration manifest list')
    results = []
    for entry in manifest:
        job_path = contained(public_root, entry['job'])
        data = json.loads(job_path.read_text())
        transcript = json.loads(job_path.with_name('transcript.json').read_text())
        truth = entry['provenance']['script']; language = entry['provenance']['language']
        # Evaluate exported job captions; verify the saved ASR transcript is the same input.
        captions = data['job'].get('captions', [])
        if transcript.get('captions') != captions: raise ValueError(f"{entry['id']}: job captions differ from saved ASR transcript")
        if transcript.get('script') != truth or transcript.get('language') != language: raise ValueError(f"{entry['id']}: transcript ground truth metadata differs from manifest")
        if not math.isclose(data['job']['duration'], entry['duration'], abs_tol=.001): raise ValueError(f"{entry['id']}: job duration differs from manifest")
        result = evaluate(truth, captions, entry['duration'], language, max_wer, min_timed_coverage)
        result.update({'id': entry['id'], 'model': transcript.get('model'), 'source': entry['job']})
        if not transcript.get('model'): result['usable'] = False
        results.append(result)
    languages = {}
    for language in sorted({item['language'] for item in results}):
        subset = [item for item in results if item['language'] == language]
        reference_words = sum(item['referenceWords'] for item in subset)
        errors = sum(sum(item['alignment'][name] for name in ['substitution', 'deletion', 'insertion']) for item in subset)
        languages[language] = {'demonstrations': len(subset), 'referenceWords': reference_words, 'microWer': errors/reference_words, 'usableCount': sum(item['usable'] for item in subset)}
    return {'schemaVersion': 1, 'method': 'NFKC/casefold punctuation-normalized token Levenshtein WER against authored synthetic narration scripts; milliseconds validated against source job duration.', 'limitations': ['Script-to-ASR agreement on synthetic espeak-ng speech does not establish performance on natural Dutch/English speakers.', 'Caption interval coverage is not acoustic forced alignment, phonetic lipsync or audiovisual synchronization proof.', 'Confidence is model-reported probability, not calibrated correctness.', 'Human transcript and moving-export review remain necessary.'], 'languages': languages, 'bothLanguagesTested': {'nl','en'}.issubset(languages), 'usable': all(item['usable'] for item in results) and {'nl','en'}.issubset(languages), 'fatalTimingErrors': sum(len(item['timing']['invalid']) for item in results), 'demonstrations': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, nargs='?', default=Path('public/demos/manifest.json'))
    parser.add_argument('--out', type=Path, default=Path('out/transcription-qa.json'))
    parser.add_argument('--public-root', type=Path)
    parser.add_argument('--max-wer', type=float, default=.35)
    parser.add_argument('--min-timed-coverage', type=float, default=.65)
    parser.add_argument('--require-usable', action='store_true', help='Also fail on high WER, insufficient coverage or untested language')
    args = parser.parse_args()
    if not 0 <= args.max_wer <= 1 or not 0 <= args.min_timed_coverage <= 1: parser.error('Thresholds must be between 0 and 1')
    try:
        result = manifest_report(args.manifest, args.public_root, args.max_wer, args.min_timed_coverage)
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.error(str(error))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'report': str(args.out), 'usable': result['usable'], 'fatalTimingErrors': result['fatalTimingErrors'], 'languages': result['languages']}))
    return 2 if result['fatalTimingErrors'] else 1 if args.require_usable and not result['usable'] else 0

if __name__ == '__main__': raise SystemExit(main())
