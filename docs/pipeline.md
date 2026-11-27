# Offline editing pipeline

`scripts/reel.py` is a real FFmpeg editing pipeline with optional local faster-whisper transcription. It has no paid API or hosted generation dependency. Codex and Claude Code author the editorial decisions and use this deterministic runner for cuts, normalization, assets and timestamp remapping.

## Requirements

- Python 3.11+ and FFmpeg/ffprobe on PATH.
- Optional transcription: Python 3.11 or 3.12 virtual environment; other versions depend on native wheel availability.
- First ASR use downloads model weights from Hugging Face. After caching, inference is local on CPU/int8. `tiny` is a smoke-test model, not a Dutch quality target. Use `small` or `medium` for actual Dutch content and review names/terminology.

```bash
python3 scripts/reel.py doctor
python3.11 -m venv .venv-asr
.venv-asr/bin/pip install -r requirements-transcription.txt
# requirements-transcription.lock.txt records the actual successful macOS/arm64 smoke environment.
```

## Real source → words → edited video → compositor job

Run from repository root. Put job output under `public/` so the compositor resolves media from the public asset directory.

```bash
.venv-asr/bin/python scripts/reel.py transcribe /path/interview.mp4 \
  --language nl --model small --out public/jobs/interview/source-transcript.json

python3 scripts/reel.py edit /path/interview.mp4 \
  --transcript public/jobs/interview/source-transcript.json \
  --out public/jobs/interview --title 'Van idee naar resultaat'
```

`edit` can also invoke ASR itself when run in the ASR environment and no `--transcript` is supplied. `--no-transcribe` gives acoustic editing without captions. Add `--keep-silence` to preserve all pauses. Inputs remain intact. Output files:

- `edited.mp4`: H.264/yuv420p, 30 fps, 720×1280 by default, AAC/48kHz, audio normalized toward −16 LUFS, −1.5 dB true peak. Digital silence bypasses normalization to avoid FFmpeg 9 non-finite samples. Normalization is one-pass and not a broadcast-certified two-pass loudness workflow.
- `edl.json`: source SHA256, source/output intervals, removed intervals, detected silences, repeat candidates, limitations and decisions.
- `captions.json`: word timestamps remapped onto the new edit.
- `job.json`: `{ "job": { "title", "brand", "width", "height", "fps", "duration", "video", "captions", "effects" } }`, ready as compositor props. `duration` and effect start/duration are seconds; Caption timestamps are milliseconds.

Source is scaled to fill and center-cropped. Use `--width 1080 --height 1350` for a LinkedIn portrait or `--width 1920 --height 1080` for a landscape walkthrough. This is not face tracking or automatic reframing.

## Semantic take selection by the coding agent

```bash
python3 scripts/reel.py plan /path/interview.mp4 \
  --transcript transcript.json --out public/jobs/interview-plan
```

The acoustic planner cuts pauses longer than 0.7 s with 140 ms handles. If an ASR word overlaps the detected silence, it preserves that whole silence interval. This favors preserving quiet words over aggressive pacing.

Repeated take detection matches identical normalized sentences of four or more words. It suggests keeping the last occurrence, which does **not** imply better performance. Apply only after inspection with `--remove-repeat-takes`. The coding agent can make a stronger semantic decision by reading the transcript, listening and inspecting frames, then supplying a reviewed EDL:

```json
{"cuts": [[0, 1.2], [7.5, 12.3]]}
```

```bash
python3 scripts/reel.py edit /path/interview.mp4 --transcript transcript.json \
  --edl reviewed.json --out public/jobs/interview
```

These cuts override automatic cuts and always use source seconds. Validate that removals preserve the argument, don't change meaning, and don't cut a word mid-syllable. The engine rejects non-finite, backwards and out-of-bounds cuts. `vendor/askeditor/timeline.py` provides the MIT-licensed kept-source timeline engine; provenance and license are preserved beside it.

## Software walkthrough, local B-roll and brand

```bash
python3 scripts/reel.py edit /path/speaker.mp4 --transcript transcript.json \
  --walkthrough /path/screen.mp4 --broll /path/product.mp4 \
  --broll /path/screenshot.png --out public/jobs/demo
```

The job gets a `walkthrough` path for the renderer's layout. Local B-roll assets are copied into the job directory and receive spaced `broll` events. This is deterministic placement of supplied footage, not semantic stock search, automatic screen/speaker synchronization or an agent that understands footage by itself. The coding agent can inspect the input and rewrite effect timings/params in `job.json`. Muting and layout are renderer responsibilities.

`--brand brand.json` accepts an object containing `background`, `foreground`, `accent` and `fontFamily` (or the same inside a `brand` object). Default loads brands/studio-linea.json with colors observed on the public Studio Linea website; verify against approved brand tokens before publishing. No fonts or music are fetched implicitly.

## Reference analysis and three variants

```bash
python3 scripts/reel.py analyze-reference /path/owned-or-permitted-reference.mp4 \
  --out reference.json --frames public/reference-frames
python3 scripts/reel.py variants public/jobs/demo/job.json --out public/jobs/demo/variants
```

Reference analysis reports ffprobe metadata, encoding keyframes, scene-change candidates at score >0.32, acoustic pauses and up to 12 evenly spaced JPEGs. Encoding keyframes are not editorial cuts. An agent must inspect frames and listen to judge typography, composition, masking, easing, transition timing and audio storytelling. No reference asset is shipped into output automatically. Only analyze media you are allowed to download/use.

Variants produce minimal, dynamic and playful job props using the same edit and different effect recipes (`title-reveal`, `zoom-punch`, `comic-burst`). These are actual configurable variants, not three independently reasoned creative concepts; ask the coding agent to author different hooks/storyboards if that is the goal.

## Reproducible smoke demo and actual validation

```bash
python3 scripts/reel.py demo --out public/demo
python3 scripts/reel.py edit public/demo/source.mp4 \
  --transcript public/demo/transcript.json --out public/jobs/demo
python3 -m unittest discover -s tests -v
```

The demo uses FFmpeg test imagery and synthetic English speech from espeak (Linux) or macOS `say` when available; otherwise it uses a tone. Its authored transcript fixture is explicitly labelled **not ASR**. It tests technical plumbing and cannot demonstrate actual talking-head or premium editorial quality.

On 2026-11-27, faster-whisper 1.2.1/tiny CPU/int8 was actually installed and run locally on synthetic EN and NL speech. EN produced 11 words with near-exact text. NL produced 14 words but misrecognized the brand and closing phrase. Evidence: `public/demo/asr-en.json`, `public/demo/asr-nl.json`; NL source speech is `public/demo/nl.aiff`. These are smoke results, not a word-error-rate benchmark. Actual EN ASR was also passed into `edit` to produce `public/jobs/asr-demo`.

Eight tests passed: real FFmpeg video/audio edit, no-audio input, guarded quiet-word preservation, timestamp remapping, opt-in repeated takes, manual EDL validation, merged cuts and invalid transcript rejection. Browser rendering runs on the isolated GitHub runner, not the Mac, in line with the workspace instructions.

## Current limits

The editing CLI does not autonomously infer the best emotional take, track faces, generate/fetch stock B-roll, generate music/voiceovers, infer reference aesthetics, or guarantee broadcast loudness. For person isolation use the separate optional segmentation adapter described in docs/segmentation.md. Scene understanding and editorial judgment are performed by the existing coding agent with the provided skills and reviewable job JSON. Long inputs use per-clip temporary encodes to bound filter-graph size, so fast edits may still take real encoding time. Avoid unbounded numbers of tiny cuts. Outside-`public/` jobs must have their assets staged under public/ and job paths updated before this repository renderer can resolve them; their generated media paths are basenames.
