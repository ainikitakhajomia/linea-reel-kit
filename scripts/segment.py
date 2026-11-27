#!/usr/bin/env python3
"""Offline foreground PNG extraction; FFmpeg chromakey or optional MediaPipe portrait."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True)
    if result.returncode:
        raise ValueError(f"{args[0]} failed: {result.stderr.decode(errors='replace')[-2000:]}")
    return result


def inspect_video(source):
    info = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                           '-show_streams', '-of', 'json', source]).stdout)
    streams = info.get('streams', [])
    if not streams:
        raise ValueError('Input has no video stream')
    video = streams[0]
    rate = Fraction(video.get('avg_frame_rate', '0/1'))
    if rate <= 0:
        rate = Fraction(video.get('r_frame_rate', '0/1'))
    if rate <= 0 or rate > 240:
        raise ValueError('Cannot determine a supported input frame rate (0–240 fps)')
    return int(video['width']), int(video['height']), rate


def chromakey(source, output, fps, color, similarity, blend):
    # YUV alpha keying; retained pixels become an RGBA PNG, no solid matte baked in.
    filters = f'fps={fps},format=yuva444p,chromakey={color}:{similarity}:{blend},format=rgba'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', source, '-an',
         '-vf', filters, '-start_number', '0', '-threads', '1', output / '%06d.png'])


def portrait(source, output, fps, width, height, threshold, feather):
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
    except ImportError as exc:
        raise ValueError('Portrait mode requires Python 3.10–3.12 and requirements-segmentation.txt; '
                         'chromakey mode needs only FFmpeg.') from exc
    if not hasattr(mp, 'solutions'):
        raise ValueError('This adapter requires mediapipe==0.10.21 (legacy bundled selfie model)')
    # Decode the same normalized fps as the chromakey path. No file/network/model download occurs here.
    process = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(source),
                                '-vf', f'fps={fps}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-an', '-'],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    index = 0
    try:
        with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as model:
            while True:
                required = width * height * 3
                data = bytearray()
                while len(data) < required:
                    chunk = process.stdout.read(required - len(data))
                    if not chunk:
                        break
                    data.extend(chunk)
                if not data:
                    break
                if len(data) != required:
                    raise ValueError('Incomplete decoded portrait frame')
                rgb = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
                mask = model.process(rgb).segmentation_mask
                # Soft threshold maintains hair edges; feather controls confidence transition width.
                alpha = np.clip((mask - threshold) / feather + .5, 0, 1)
                rgba = np.dstack((rgb, np.round(alpha * 255).astype(np.uint8)))
                if not cv2.imwrite(str(output / f'{index:06d}.png'), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)):
                    raise ValueError('Could not write foreground PNG')
                index += 1
        if process.wait() != 0:
            raise ValueError('FFmpeg portrait decode failed')
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()


def segment(source, output, *, mode='chromakey', color='0x00ff00', similarity=.15,
            blend=.05, fps=None, threshold=.5, feather=.1):
    for tool in ['ffmpeg', 'ffprobe']:
        if not shutil.which(tool):
            raise ValueError(f'Missing {tool}; install FFmpeg first')
    source, output = Path(source).resolve(), Path(output).resolve()
    if not source.is_file():
        raise ValueError(f'Input does not exist: {source}')
    if mode not in ['chromakey', 'portrait']:
        raise ValueError('Mode must be chromakey or portrait')
    if not re.fullmatch(r'0x[0-9a-fA-F]{6}', color):
        raise ValueError('Color must be a hexadecimal RGB value such as 0x00ff00')
    if not all(math.isfinite(value) for value in [similarity, blend, threshold, feather]):
        raise ValueError('Parameters must be finite')
    if not .01 <= similarity <= 1 or not 0 <= blend <= 1 or not 0 <= threshold <= 1 or not 0 < feather <= 1:
        raise ValueError('Invalid similarity, blend, threshold or feather')
    width, height, source_fps = inspect_video(source)
    rate = Fraction(str(fps)) if fps is not None else source_fps
    if not 0 < rate <= 240:
        raise ValueError('fps must be between 0 and 240')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output folder must be empty; use a new folder to prevent stale foreground frames')
    output.mkdir(parents=True, exist_ok=True)
    try:
        if mode == 'chromakey':
            chromakey(source, output, rate, color, similarity, blend)
        else:
            portrait(source, output, rate, width, height, threshold, feather)
        frames = len(list(output.glob('[0-9][0-9][0-9][0-9][0-9][0-9].png')))
        if frames == 0:
            raise ValueError('No foreground frames generated')
        public = ROOT / 'public'
        try:
            frame_pattern = (output.relative_to(public) / '%06d.png').as_posix()
        except ValueError:
            frame_pattern = str(output / '%06d.png')
        metadata = {'mode': mode, 'source': str(source), 'width': width, 'height': height,
                    'fps': float(rate), 'frames': frames, 'duration': frames / float(rate),
                    'foregroundFrames': frame_pattern, 'alpha': True,
                    'implementation': 'FFmpeg chromakey' if mode == 'chromakey' else 'MediaPipe selfie segmentation 0.10.21',
                    'parameters': {'color': color, 'similarity': similarity, 'blend': blend} if mode == 'chromakey'
                    else {'threshold': threshold, 'feather': feather, 'model_selection': 1}}
        (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        return metadata
    except Exception:
        # Remove only files this fresh job could have created; never modify source media.
        for path in output.glob('[0-9][0-9][0-9][0-9][0-9][0-9].png'):
            path.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--out', required=True)
    parser.add_argument('--mode', choices=['chromakey', 'portrait'], default='chromakey')
    parser.add_argument('--color', default='0x00ff00')
    parser.add_argument('--similarity', type=float, default=.15)
    parser.add_argument('--blend', type=float, default=.05)
    parser.add_argument('--fps', type=float, help='Match job fps; default: source frame rate')
    parser.add_argument('--threshold', type=float, default=.5)
    parser.add_argument('--feather', type=float, default=.1)
    args = parser.parse_args()
    try:
        print(json.dumps(segment(args.input, args.out, mode=args.mode, color=args.color,
                                 similarity=args.similarity, blend=args.blend, fps=args.fps,
                                 threshold=args.threshold, feather=args.feather), indent=2))
    except (ValueError, OSError, ZeroDivisionError) as exc:
        parser.exit(1, f'Segmentation failed: {exc}\n')


if __name__ == '__main__':
    main()
