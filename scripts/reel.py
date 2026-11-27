#!/usr/bin/env python3
"""Offline-first editing: FFmpeg + optional faster-whisper; no paid services."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Vendored, attribution-preserving MIT timing engine; see vendor/askeditor/provenance.json.
from vendor.askeditor.timeline import Timeline

BRAND_FILE = ROOT / "brands" / "studio-linea.json"
BRAND = json.loads(BRAND_FILE.read_text()) if BRAND_FILE.is_file() else {
    "background": "#f6f5f1", "foreground": "#111316", "accent": "#27335f", "fontFamily": "Arial, sans-serif"}


def run(args, *, check=True):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if check and result.returncode:
        raise ValueError(f"{args[0]} failed ({result.returncode}): {result.stderr[-2500:]}")
    return result


def require_tools():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            raise ValueError(f"Missing {tool}. Install FFmpeg first.")


def load(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"Media does not exist: {path}")
    result = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path]).stdout)
    duration = float(result.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Input must have a finite, positive duration")
    return result, duration


def has_audio(info):
    return any(s["codec_type"] == "audio" for s in info["streams"])


def read_captions(path, duration):
    data = load(path)
    if isinstance(data, dict):
        data = data.get("captions", data.get("job", {}).get("captions"))
    if not isinstance(data, list):
        raise ValueError("Transcript must be a Caption[] or {captions: Caption[]}")
    captions = []
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            raise ValueError("Each caption needs text, startMs and endMs")
        start, end = float(item["startMs"]), float(item["endMs"])
        if not all(math.isfinite(x) for x in (start, end)) or start < 0 or end <= start or end > duration * 1000 + 100:
            raise ValueError(f"Caption timing outside source duration: {item}")
        captions.append({"text": item["text"], "startMs": start, "endMs": min(end, duration * 1000),
                         "timestampMs": item.get("timestampMs"), "confidence": item.get("confidence")})
    return sorted(captions, key=lambda c: c["startMs"])


def detect_silence(path, duration, audio=True):
    if not audio:
        return []
    result = run(["ffmpeg", "-hide_banner", "-i", Path(path).resolve(), "-af", "silencedetect=noise=-35dB:d=0.55", "-vn", "-f", "null", "-"])
    events = re.findall(r"silence_(start|end):\s*([\d.]+)", result.stderr)
    intervals, start = [], None
    for kind, value in events:
        if kind == "start":
            start = float(value)
        elif start is not None:
            intervals.append([start, min(float(value), duration)])
            start = None
    if start is not None:
        intervals.append([start, duration])
    return intervals


def merge_intervals(intervals, duration):
    result = []
    for start, end in sorted(intervals):
        start, end = max(0, start), min(duration, end)
        if end <= start:
            continue
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result


def complement(cuts, duration):
    timeline = Timeline.keeping(duration, merge_intervals(cuts, duration))
    keeps = [[start, end] for start, end in timeline.segments if end - start >= 0.04]
    if not keeps:
        raise ValueError("Edit would remove the entire source; review the transcript and silence threshold")
    return keeps


def sentences(captions):
    result, current = [], []
    for caption in captions:
        if current and caption["startMs"] - current[-1]["endMs"] > 800:
            result.append(current)
            current = []
        current.append(caption)
        if re.search(r"[.!?]\s*$", caption["text"]):
            result.append(current)
            current = []
    if current:
        result.append(current)
    return result


def repeat_candidates(captions):
    """Exact normalized sentences only: no claim to infer a 'good' performance."""
    seen, candidates = {}, []
    for group in sentences(captions):
        text = " ".join(c["text"].strip() for c in group)
        normalized = " ".join(re.findall(r"\w+", text.lower()))
        if len(normalized.split()) < 4:
            continue
        span = [group[0]["startMs"] / 1000, group[-1]["endMs"] / 1000]
        if normalized in seen:
            candidates.append({"remove": seen[normalized], "keep": span, "reason": "exact normalized sentence repeated; prefer latest take", "confidence": "heuristic", "text": text})
        seen[normalized] = span
    return candidates


def make_plan(duration, silence, captions, remove_repeats=False):
    cuts = []
    for start, end in silence:
        # Never cut an ASR word, even if the detector calls a quiet word silence.
        guarded = any(c["startMs"] / 1000 < end and c["endMs"] / 1000 > start for c in captions)
        if end - start > 0.7 and not guarded:
            cuts.append([start + (0 if start == 0 else 0.14), end - (0 if end >= duration else 0.14)])
    candidates = repeat_candidates(captions)
    if remove_repeats:
        cuts.extend(c["remove"] for c in candidates)
    keeps = complement(cuts, duration)
    offset, timeline = 0.0, []
    for start, end in keeps:
        timeline.append({"sourceStart": round(start, 6), "sourceEnd": round(end, 6), "outputStart": round(offset, 6), "outputEnd": round(offset + end - start, 6)})
        offset += end - start
    return {"version": 1, "sourceDuration": duration, "duration": offset, "silence": silence,
            "cuts": merge_intervals(cuts, duration), "clips": timeline, "repeatCandidates": candidates,
            "repeatRemovalApplied": remove_repeats,
            "limitations": ["Silence detection is acoustic, not semantic.", "Repeat detection only matches normalized identical sentences and cannot judge delivery quality.", "Source files are preserved; review EDL before publishing."]}


def apply_manual_cuts(plan, path):
    """Allow a coding agent to author a semantic edit after inspecting the transcript."""
    cuts = load(path).get("cuts")
    if not isinstance(cuts, list):
        raise ValueError("Manual EDL must contain cuts: [[sourceStartSeconds, sourceEndSeconds], ...]")
    for item in cuts:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("Each cut must contain start and end seconds")
        if not all(isinstance(x, (float, int)) and math.isfinite(x) for x in item):
            raise ValueError("Cut timing must be finite numbers")
        if item[0] < 0 or item[1] <= item[0] or item[1] > plan["sourceDuration"]:
            raise ValueError("Cut timing outside source duration")
    clips, offset = [], 0.0
    for start, end in complement(cuts, plan["sourceDuration"]):
        clips.append({"sourceStart": start, "sourceEnd": end, "outputStart": offset, "outputEnd": offset + end - start})
        offset += end - start
    plan.update(cuts=merge_intervals(cuts, plan["sourceDuration"]), clips=clips, duration=offset, manualCutsApplied=True)
    return plan


def remap_captions(captions, clips):
    result = []
    for c in captions:
        for clip in clips:
            start = max(c["startMs"] / 1000, clip["sourceStart"])
            end = min(c["endMs"] / 1000, clip["sourceEnd"])
            if end - start > 0.001:
                mapped = dict(c)
                mapped["startMs"] = round((clip["outputStart"] + start - clip["sourceStart"]) * 1000, 3)
                mapped["endMs"] = round((clip["outputStart"] + end - clip["sourceStart"]) * 1000, 3)
                mapped["timestampMs"] = None
                result.append(mapped)
    return sorted(result, key=lambda c: c["startMs"])


def transcribe_file(source, output, language=None, model="tiny"):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise ValueError("Transcription needs the optional environment: python3 -m venv .venv-asr && .venv-asr/bin/pip install -r requirements-transcription.txt. Then use .venv-asr/bin/python scripts/reel.py transcribe ...; or supply --transcript JSON / --no-transcribe.") from exc
    engine = WhisperModel(model, device="cpu", compute_type="int8")
    segments, info = engine.transcribe(str(Path(source).resolve()), language=language, word_timestamps=True, vad_filter=True)
    captions = [{"text": w.word, "startMs": round(w.start * 1000), "endMs": max(round(w.start * 1000) + 1, round(w.end * 1000)), "timestampMs": None, "confidence": w.probability}
                for segment in segments for w in (segment.words or [])]
    save(output, {"language": info.language, "model": model, "captions": captions})
    return captions


def static_path(path):
    try:
        return str(Path(path).resolve().relative_to((ROOT / "public").resolve())).replace("\\", "/")
    except ValueError:
        # Copy an outside job under public before rendering; avoid local absolute URL leakage.
        return Path(path).name


def render_edit(source, out, plan, info, width=720, height=1280):
    out = Path(out).resolve()
    source = Path(source).resolve()
    if out == source:
        raise ValueError("Output cannot overwrite source")
    if not any(s["codec_type"] == "video" for s in info["streams"]):
        raise ValueError("Input must contain a video stream")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reel-cut-") as tmp:
        tmp = Path(tmp)
        paths = []
        for i, clip in enumerate(plan["clips"]):
            segment = tmp / f"clip-{i:04}.mp4"
            duration = clip["sourceEnd"] - clip["sourceStart"]
            args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", clip["sourceStart"], "-i", source, "-t", duration]
            if not has_audio(info):
                args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            args += ["-map", "0:v:0", "-map", "0:a:0" if has_audio(info) else "1:a:0", "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps=30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest", segment]
            run(args)
            paths.append(segment)
        concat = tmp / "concat.txt"
        concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths))
        # FFmpeg 9 loudnorm produces non-finite samples for digital silence.
        normalize = has_audio(info)
        if normalize:
            level = run(["ffmpeg", "-hide_banner", "-i", source, "-af", "volumedetect", "-vn", "-f", "null", "-"]).stderr
            peak = re.search(r"max_volume: ([\-\w.]+) dB", level)
            normalize = peak is not None and float(peak.group(1)) > -65
        final = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c:v", "copy"]
        if normalize:
            final += ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"]
        run(final + ["-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", out])


def command_edit(args):
    require_tools()
    source = Path(args.input).resolve()
    info, duration = probe(source)
    out = Path(args.out).resolve()
    if out == source.parent:
        raise ValueError("Choose a dedicated job directory, not the source directory")
    out.mkdir(parents=True, exist_ok=True)
    if args.transcript:
        captions = read_captions(args.transcript, duration)
    elif args.no_transcribe:
        captions = []
    else:
        transcribe_file(source, out / "source-transcript.json", args.language, args.model)
        captions = read_captions(out / "source-transcript.json", duration)
    silence = [] if args.keep_silence else detect_silence(source, duration, has_audio(info))
    plan = make_plan(duration, silence, captions, args.remove_repeat_takes)
    if args.edl:
        plan = apply_manual_cuts(plan, args.edl)
    plan["source"] = source.name
    plan["sourceSha256"] = file_sha256(source)
    save(out / "edl.json", plan)
    if args.command == "plan":
        print(out / "edl.json")
        return
    render_edit(source, out / "edited.mp4", plan, info, args.width, args.height)
    mapped = remap_captions(captions, plan["clips"])
    _, actual_duration = probe(out / "edited.mp4")
    job = {"title": args.title, "brand": BRAND, "width": args.width, "height": args.height, "fps": 30, "duration": actual_duration,
           "video": static_path(out / "edited.mp4"), "captions": mapped,
           "effects": [{"id": "title-reveal", "start": 0, "duration": min(2.5, actual_duration), "text": args.title}]}
    if args.brand:
        brand = load(args.brand)
        job["brand"] = brand.get("brand", brand)
    if args.walkthrough:
        walk = Path(args.walkthrough).resolve()
        probe(walk)
        dest = out / ("walkthrough" + walk.suffix.lower())
        if walk != dest:
            shutil.copyfile(walk, dest)
        job["walkthrough"] = static_path(dest)
    for index, asset in enumerate(args.broll or []):
        asset = Path(asset).resolve()
        if not asset.is_file() or asset.suffix.lower() not in (".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg"):
            raise ValueError(f"Unsupported or missing B-roll: {asset}")
        dest = out / f"broll-{index}{asset.suffix.lower()}"
        if asset != dest:
            shutil.copyfile(asset, dest)
        at = min(actual_duration - 0.1, 2.5 + index * 4)
        job["effects"].append({"id": "broll", "start": at, "duration": min(2.5, actual_duration - at), "src": static_path(dest), "mediaType": "image" if asset.suffix.lower() in (".png", ".jpg", ".jpeg") else "video"})
    save(out / "captions.json", mapped)
    save(out / "job.json", {"job": job})
    print(out / "job.json")


def command_demo(args):
    require_tools()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    text = "Build better stories. From idea to impact. Make every frame count."
    audio, spoken = out / "speech.wav", False
    if shutil.which("espeak"):
        run(["espeak", "-v", "en", "-s", "145", "-w", audio, text])
        spoken = True
    elif shutil.which("say"):
        aiff = out / "speech.aiff"
        result = run(["say", "-r", "145", "-o", aiff, text], check=False)
        if result.returncode == 0:
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", aiff, audio])
            aiff.unlink()
            spoken = True
    if not spoken:
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=330:duration=6", audio])
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=360x640:rate=30:duration=10", "-i", audio, "-af", "adelay=1000|1000,apad", "-t", "10", "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", out / "source.mp4"])
    # Fixture timings are authored for the synthetic demo, not represented as ASR.
    captions = []
    for i, word in enumerate(text.split()):
        start = 1100 + i * 430
        captions.append({"text": word, "startMs": start, "endMs": start + 390, "timestampMs": None, "confidence": None})
    save(out / "transcript.json", {"kind": "authored synthetic fixture, not ASR", "spokenAudio": spoken, "captions": captions})
    print(out / "source.mp4")


def command_reference(args):
    require_tools()
    source = Path(args.input).resolve()
    info, duration = probe(source)
    # Decode video for scene score, but do not use a browser or copy reference assets.
    result = run(["ffmpeg", "-hide_banner", "-i", source, "-an", "-vf", "select='gt(scene,0.32)',showinfo", "-f", "null", "-"])
    scenes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", result.stderr)]
    keys = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-skip_frame", "nokey", "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", source])
    frames = json.loads(keys.stdout).get("frames", [])
    save(args.out, {"source": source.name, "duration": duration, "video": next((s for s in info["streams"] if s["codec_type"] == "video"), None),
                    "sceneChangesSeconds": scenes, "silence": detect_silence(source, duration, has_audio(info)),
                    "keyframeTimesSeconds": [float(x["best_effort_timestamp_time"]) for x in frames if "best_effort_timestamp_time" in x],
                    "analysisType": "deterministic media metrics; requires an agent to inspect frames for typography, composition, easing, masks and audio storytelling",
                    "limitations": ["Scene thresholds miss subtle cuts and can misclassify flashes.", "Encoding keyframes do not imply editorial cuts.", "No identity, aesthetic quality, or exact style inference."]})
    if args.frames:
        dest = Path(args.frames).resolve()
        dest.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", source, "-vf", f"fps=1/{max(duration / 12, 0.25)},scale=480:-2", "-frames:v", "12", dest / "frame-%03d.jpg"])
    print(args.out)


def command_variants(args):
    props = load(args.job)
    job = props.get("job", props)
    styles = [("minimal", "title-reveal"), ("dynamic", "zoom-punch"), ("playful", "comic-burst")]
    for label, effect in styles:
        variant = copy.deepcopy(job)
        variant["title"] = f"{job['title']} / {label}"
        variant["effects"] = [{"id": effect, "start": 0, "duration": min(job["duration"], 3), "text": job["title"]}]
        save(Path(args.out) / f"{label}.json", {"job": variant})
    print(args.out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    demo = sub.add_parser("demo")
    demo.add_argument("--out", default="public/demo")
    trans = sub.add_parser("transcribe")
    trans.add_argument("input")
    trans.add_argument("--out", required=True)
    trans.add_argument("--language", choices=["nl", "en"])
    trans.add_argument("--model", default="tiny")
    for command in ("edit", "plan"):
        p = sub.add_parser(command)
        p.add_argument("input")
        p.add_argument("--out", required=True)
        p.add_argument("--transcript")
        p.add_argument("--edl", help="Agent-authored JSON cuts override automatic cuts, in source seconds")
        p.add_argument("--no-transcribe", action="store_true")
        p.add_argument("--keep-silence", action="store_true")
        p.add_argument("--remove-repeat-takes", action="store_true", help="Opt-in exact sentence dedup; heuristic, inspect EDL")
        p.add_argument("--language", choices=["nl", "en"])
        p.add_argument("--model", default="tiny")
        p.add_argument("--title", default="Make every frame count")
        p.add_argument("--brand")
        p.add_argument("--width", type=int, default=720)
        p.add_argument("--height", type=int, default=1280)
        p.add_argument("--walkthrough")
        p.add_argument("--broll", action="append")
    ref = sub.add_parser("analyze-reference")
    ref.add_argument("input")
    ref.add_argument("--out", required=True)
    ref.add_argument("--frames")
    variant = sub.add_parser("variants")
    variant.add_argument("job")
    variant.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            print(json.dumps({"python": sys.version.split()[0], "ffmpeg": shutil.which("ffmpeg"), "ffprobe": shutil.which("ffprobe"), "fasterWhisper": importlib.util.find_spec("faster_whisper") is not None, "paidAPIs": False}, indent=2))
            require_tools()
        elif args.command == "demo":
            command_demo(args)
        elif args.command == "transcribe":
            require_tools()
            probe(args.input)
            transcribe_file(args.input, args.out, args.language, args.model)
        elif args.command in ("edit", "plan"):
            if args.width < 16 or args.height < 16 or args.width % 2 or args.height % 2:
                raise ValueError("Dimensions must be even integers of at least 16 pixels")
            command_edit(args)
        elif args.command == "analyze-reference":
            command_reference(args)
        elif args.command == "variants":
            command_variants(args)
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"reel: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
