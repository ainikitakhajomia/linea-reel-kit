#!/usr/bin/env python3
"""Measure an actual media export using ffprobe and FFmpeg, without a browser."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def run(args):
    result = subprocess.run([str(x) for x in args], text=True, capture_output=True)
    if result.returncode:
        raise ValueError(f"{args[0]} failed ({result.returncode}): {result.stderr[-1800:]}")
    return result


def number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (ValueError, TypeError):
        return None


def fraction(value):
    try:
        return float(Fraction(value))
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_black(log):
    return [{"start": float(start), "end": float(end), "duration": float(duration)}
            for start, end, duration in re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", log)]


def parse_freezes(log, duration):
    spans, start, pending_duration = [], None, None
    for kind, raw in re.findall(r"freeze_(start|duration|end):\s*([\d.]+)", log):
        value = float(raw)
        if kind == "start":
            start, pending_duration = value, None
        elif kind == "duration":
            pending_duration = value
        elif start is not None:
            spans.append({"start": start, "end": value, "duration": pending_duration if pending_duration is not None else value - start})
            start, pending_duration = None, None
    if start is not None:
        spans.append({"start": start, "end": duration, "duration": max(0, duration - start), "reachesEnd": True})
    return spans


def parse_loudness(log):
    candidates = re.findall(r'\{\s*"input_i".*?\}', log, re.S)
    if not candidates:
        raise ValueError("FFmpeg did not emit loudnorm measurement JSON")
    values = json.loads(candidates[-1])
    return {"integratedLUFS": number(values.get("input_i")), "truePeakDBTP": number(values.get("input_tp")),
            "loudnessRangeLU": number(values.get("input_lra")), "gatingThresholdLUFS": number(values.get("input_thresh")),
            "method": "FFmpeg loudnorm input measurements; EBU R128 integrated loudness and true peak",
            "nonFiniteMeasurementMeans": "digital silence or signal below the loudness measurement gate"}


def validate_media(path, *, black_min=0.2, freeze_min=1.0):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError(f"Input does not exist: {path.name}")
    for name in ("ffmpeg", "ffprobe"):
        if not shutil.which(name):
            raise ValueError(f"Missing dependency: {name}")
    info = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", path]).stdout)
    duration = number(info.get("format", {}).get("duration"))
    if duration is None or duration <= 0:
        raise ValueError("Input must have finite positive duration")
    videos = [s for s in info.get("streams", []) if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not videos:
        raise ValueError("Input has no video stream")
    video = videos[0]
    visual = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:v:0", "-an", "-vf",
                  f"blackdetect=d={black_min}:pix_th=0.10:pic_th=0.98,freezedetect=n=-50dB:d={freeze_min}", "-f", "null", "-"])
    black, freeze = parse_black(visual.stderr), parse_freezes(visual.stderr, duration)
    warnings = []
    loudness = None
    if audios:
        measured = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-vn", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"])
        loudness = parse_loudness(measured.stderr)
        integrated, peak = loudness["integratedLUFS"], loudness["truePeakDBTP"]
        if integrated is None:
            warnings.append({"code": "silence-or-below-gate", "message": "Integrated loudness is non-finite; audio may be silent or below the gate."})
        elif not -18 <= integrated <= -14:
            warnings.append({"code": "loudness-outside-social-target", "message": "Integrated loudness is outside the advisory -16 ±2 LUFS social-video target."})
        if peak is not None and peak > -1:
            warnings.append({"code": "true-peak-high", "message": "Measured true peak exceeds -1 dBTP; inspect for clipping/codec headroom."})
    else:
        warnings.append({"code": "missing-audio", "message": "No audio stream. This can be intentional for a silent slideshow; a talking head should contain audio."})
    if black:
        warnings.append({"code": "black-intervals", "message": "Near-black intervals detected. Inspect against intentional fades or dark designs."})
    if freeze:
        warnings.append({"code": "static-intervals", "message": "Static intervals detected. Expected for slides/end cards; inspect unexpected freezes in moving footage."})
    audio = audios[0] if audios else None
    video_start, audio_start = number(video.get("start_time")), number(audio.get("start_time")) if audio else None
    skew = round((audio_start - video_start) * 1000, 3) if audio_start is not None and video_start is not None else None
    if skew is not None and abs(skew) > 100:
        warnings.append({"code": "stream-start-skew", "message": "Audio/video stream starts differ by more than 100 ms. This measures container timing, not lip synchronization."})
    return {"schemaVersion": 1, "source": path.name, "sourceSha256": sha256(path), "durationSeconds": duration,
            "video": {"codec": video.get("codec_name"), "width": video.get("width"), "height": video.get("height"), "pixelFormat": video.get("pix_fmt"),
                      "averageFPS": fraction(video.get("avg_frame_rate")), "declaredFPS": fraction(video.get("r_frame_rate")), "startSeconds": video_start},
            "audio": {"present": bool(audio), "codec": audio.get("codec_name") if audio else None, "sampleRate": int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
                      "channels": audio.get("channels") if audio else None, "startSeconds": audio_start, "loudness": loudness},
            "containerAudioMinusVideoStartMs": skew, "blackIntervals": black, "staticIntervals": freeze,
            "thresholds": {"blackMinimumSeconds": black_min, "blackPixelLumaThreshold": 0.10, "blackPictureFraction": 0.98, "freezeMinimumSeconds": freeze_min, "freezeNoiseDB": -50},
            "status": "review-required" if warnings else "measurements-clear", "warnings": warnings,
            "limitations": ["Advisory measurements do not prove visual or editorial quality.", "Black and static intervals can be intentional; no content-aware defect inference.",
                            "Lip sync cannot be inferred from these measurements; inspect/listen to the actual moving export.", "Container stream start alignment does not prove speech/lip alignment.",
                            "Caption correctness, spelling, safe margins, masking edges and reference parity need visual/audio review."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--out", required=True)
    parser.add_argument("--black-min", type=float, default=0.2)
    parser.add_argument("--freeze-min", type=float, default=1.0)
    args = parser.parse_args(argv)
    try:
        if not all(math.isfinite(v) and v > 0 for v in (args.black_min, args.freeze_min)):
            raise ValueError("Threshold durations must be finite and positive")
        if Path(args.input).resolve() == Path(args.out).resolve():
            raise ValueError("Report cannot overwrite source media")
        report = validate_media(args.input, black_min=args.black_min, freeze_min=args.freeze_min)
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        print(f"Media QA: {report['status']} → {dest}")
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(f"validate-media: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
