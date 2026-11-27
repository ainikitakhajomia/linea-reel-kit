---
name: linea-reel-kit
description: Edit talking heads, walkthroughs, reels, animated slideshows and carousels with the local Studio Linea Reel Kit; analyze video references, select takes and apply branded motion graphics from a reviewable job timeline.
---

# Linea Reel Kit

Configured repository, `REEL_KIT_HOME` (JSON string): __REEL_KIT_HOME__

Resolve this path before running commands. The installer substitutes an absolute checkout path. For a repository-local copy with an unsubstituted marker, use an existing absolute `REEL_KIT_HOME` environment variable, or locate the package root among the ancestors of this **skill file**: it contains `scripts/reel.py`, `src/catalog.json` and `package.json`. Do not infer the checkout from the caller's working directory. Run commands below with the resolved repository as their working directory; preserve shell quoting for user-supplied paths.

Deliver an edited artifact and playable review, with concrete limitations and evidence. Use the existing coding agent for semantic/editorial decisions; the scripts provide deterministic media operations. No separate LLM API is needed.

## Route the user's intent

| Request | Action |
| --- | --- |
| Edit a talking head; remove bad takes | Transcribe, inspect the transcript and candidate cuts, author a semantic EDL, edit, add restrained effects, render/review. |
| Apply principles from a reference | Gather scene statistics and permitted frame samples, inspect visual/audio details, write a short style analysis, implement those principles using owned assets. |
| Put large text behind me | Edit first, create synchronized foreground frames, set `foregroundFrames` and a behind-speaker text event. Read `docs/segmentation.md`. |
| Combine speaker and software walkthrough | Pass both sources through `--walkthrough`, then set intentional layout/timings in the job. Do not claim automatic content synchronization. |
| Creative variants (including five) | Use `scripts/agent-plan.py --variants 5` for distinct editorial directions. Rewrite hook, scene order and emphasis for each; a palette change is not another creative edit. Render every requested version. |
| Script → animated slideshow | Turn the script into a concise scene/storyboard job, choose relevant effects, check readability and export. Do not invent a filmed speaker. |
| Instagram, LinkedIn, brand or humor | Choose appropriate aspect ratio and safe text size, load the brand preset, use effects to support the message. Humor needs editorial judgment, not random effects. |
| Carousel | Author a slide sequence, render the carousel export, inspect every slide for text overflow and hierarchy. |

## Convert the brief into an input-aware plan

For broad requests, run the local intent router before choosing commands. It composes intents (for example walkthrough + text behind the speaker), checks supplied paths, selects existing catalog IDs, identifies missing media and proposes an ordered operation list:

```sh
python3 scripts/agent-plan.py 'Combineer mijn talking head met een softwarewalkthrough en tekst achter mij' --source /absolute/speaker.mp4 --walkthrough /absolute/screen.mp4 --out out/edit-plan.json
python3 scripts/agent-plan.py 'Maak vijf creatieve varianten van deze talking head' --source /absolute/speaker.mp4 --variants 5 --out out/five-variants.json
```

Available inputs are `--source`, `--walkthrough`, `--script`, `--images` (file or directory) and `--reference`. The output is an authoring plan, **not an executed edit**. Read it and use actual input evidence to revise its candidate effects. `needs-inputs` means complete independent planning first, then request only the missing material that blocks the user's result. A foreground matte can be derived from the edited source; it does not require a separate upload. A text-only motion request can use `typography`; a photo slideshow needs actual imagery. Do not turn generic keyword matching into a claim of reference understanding.

The router infers one through five variants from common Dutch/English phrases; `--variants` overrides that count. Verify it matches the user's request; deliver the requested count. `reel.py variants` currently supplies only three baseline timeline variations, so use those only as starting points and author any remaining jobs. Keep variant job directories and filenames distinct.

## Inspect inputs and plan

1. Identify the user's actual source files, brief, output format and existing house style. Inspect supplied files and duration; ask for missing footage only if needed. Never substitute test imagery and call it the user's finished video.
2. Run `python3 scripts/reel.py doctor`. Install missing **free** dependencies only within the authorized environment. Node dependencies use `npm ci`; ASR uses an isolated Python 3.11/3.12 venv and `requirements-transcription.txt`. Browser binaries use `npm run install:browser` where browser rendering is permitted.
3. Read `docs/pipeline.md` for supported commands and timing. Read only relevant effect records from `src/catalog.json`, using names/categories/IDs. Do not load or apply all 67 effects. They are independent baseline recipes, not proof of parity with the public reference demonstrations.
4. Load `brands/studio-linea.json` as the first preset unless the user supplied another. Keep brand JSON in `job.brand`; preserve source and license information for supplied fonts, media and music.
5. Create a named job directory under `public/jobs/`. Keep original media intact. A job outside `public/` needs explicit media staging before this repository's renderer can resolve it.

## Transcribe, select takes and edit

```sh
.venv-asr/bin/python scripts/reel.py transcribe /absolute/source.mp4 --language nl --model small --out public/jobs/example/source-transcript.json
python3 scripts/reel.py plan /absolute/source.mp4 --transcript public/jobs/example/source-transcript.json --out public/jobs/example-plan
```

Use `--language en` for English. `tiny` is for smoke tests; actual NL results have known recognition errors. Review brand names and critical phrases. Captions use `{text,startMs,endMs,timestampMs,confidence}` in milliseconds.

The automatic plan removes acoustic silence with handles and protects intervals overlapping transcript words. Exact repeated sentences are only **candidates**: the last take is not necessarily the best. Read the transcript, inspect/listen to the relevant source, and choose semantically complete, natural takes. For a deliberate edit, write `reviewed.json` containing source-second cuts, for example `{"cuts":[[0,1.2],[7.5,12.3]]}`. Then:

```sh
python3 scripts/reel.py edit /absolute/source.mp4 --transcript public/jobs/example/source-transcript.json --edl reviewed.json --brand brands/studio-linea.json --out public/jobs/example --title 'Van idee naar resultaat'
```

`--edl` overrides automatic cuts. `--remove-repeat-takes` is an opt-in exact-sentence heuristic, not semantic take selection. Review `edl.json`, which records source hash and output timing. Never edit source files to implement cuts. For manual silence-only edits use `--no-transcribe`; do not claim transcription ran.

Add a supplied screen recording with `--walkthrough /absolute/screen.mp4`. Add owned or appropriately licensed local B-roll with repeated `--broll /absolute/file.mp4`. Placement is initially spaced; inspect the story and rewrite event timings. Do not call this automatic stock search or fetch unlicensed footage. The renderer mutes secondary footage unless explicitly authored otherwise; preserve the speaker's primary audio.

## Author motion and inspect references

`job.json` is `{ "job": {...} }`. Core fields are `title`, `brand`, `width`, `height`, `fps`, `duration` (seconds), `video` (path relative to `public/`), `captions` and `effects`. Events use `{id,start,duration,text,...parameters}` with seconds. Treat the JSON timeline as the source of truth. Use one dominant visual idea at a time; start with at most three graphic recipes per short and add only when the content earns them. The planner's candidate list is a palette, not a command to apply every effect. Prefer a small number of purposeful effects: hierarchy for the hook, emphasis on a key idea, a transition for a real topic change, and a legible ending. Check cue timing against actual speech.

```sh
python3 scripts/reel.py analyze-reference /absolute/permitted-reference.mp4 --out reference.json --frames public/jobs/reference-frames
python3 scripts/reel.py variants public/jobs/example/job.json --out public/jobs/example/variants
```

Frame sampling and scene thresholds are diagnostic aids. Inspect permitted examples frame by frame around the chosen cut/effect, using FFmpeg samples or available media tools. Record composition, entrance/exit duration, easing, text hierarchy, masking, crop/camera motion and audio accents. Encoding keyframes are not cuts. Reproduce editing principles with independently authored graphics; never bypass access restrictions or copy protected reference media/private code into the library.

For `--reference`, the router only records the path: run `analyze-reference`, inspect sampled frames and audio, then write observed style decisions into the authoring plan. A name or URL alone is not a visual analysis. If source access is restricted, request an authorized reference rather than bypassing it.

For text behind a real person, segment the **edited** video so cuts, crop and FPS match. Use the tested chromakey route for green screen; the optional MediaPipe portrait adapter needs its own environment and a quality review. Set `job.foregroundFrames` using the documented numbered PNG pattern. Inspect hair/edges/motion before claiming success.

## Script, storyboard, feedback and carousel

```sh
python3 scripts/story.py storyboard /absolute/script.txt --out public/jobs/slideshow --brand brands/studio-linea.json
python3 scripts/story.py feedback public/jobs/slideshow/job.json --out out/feedback
python3 scripts/story.py carousel /absolute/script.txt --out public/carousels/example
node src/render-carousel.mjs public/carousels/example out/carousel
```

These commands provide an editable scene plan, deterministic diagnostics, SVG slides and PNG export. Read the generated storyboard, improve its hook, story arc and scene graphics for the specific brief, then render the job. Programmatic feedback is not an audience or editorial quality score. Carousel PNG export uses a browser and follows the same host rendering-location restrictions as video. Inspect SVG/PNG text fit on each slide, and treat carousels as a slide sequence rather than screenshots of a video.

## Review and export

```sh
npm run review
npm run render -- public/jobs/example/job.json out/example.mp4
```

Follow the host repository's `AGENTS.md` for rendering location. In the Studio Linea development workspace, browser rendering belongs on the isolated runner and must not run on the Mac or production server. Do ordinary FFmpeg analysis/edits and prepare the renderable job locally, then use the repository's CI workflow for the browser render. Elsewhere, local rendering is fine when that environment permits it. Do not alter production environments.

Inspect the moving export, not only JSON or one still: caption sync, word clipping, audio joins, loudness, crop, text margins, readability, graphic timing, foreground edges and final duration. Read `docs/visual-acceptance.md` for the quality bar. Tests demonstrate technical behavior; they do not establish reference-quality equivalence. Report what actually ran, artifact paths, and remaining limitations. Do not claim an effect, ASR model or adapter was tested merely because its code exists.

Canvas `orbit-ring`, `layer-explode` and `room-doors` are perspective/2.5D recipes, not physical 3D simulation. The synthetic person fixture demonstrates layering, not natural portrait-mask quality. Keep these distinctions in delivery notes and choose a real 3D or tracking implementation only if available, licensed and warranted by the brief.

Use free local tools only unless the user explicitly authorizes a paid service. A missing input, unsupported capability or external permission is a concrete limitation to report; do not silently invent footage, voices, functionality or verification.
