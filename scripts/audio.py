#!/usr/bin/env python3
"""Local speech/music ducking and original synthesized motion sound effects."""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import struct
import subprocess
import tempfile
import wave

RATE = 48000


def run(args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True)
    if result.returncode:
        raise ValueError(f'{args[0]} failed: {result.stderr.decode(errors="replace")[-2500:]}')
    return result


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]).stdout)


def sound_events(path, duration):
    if path is None:
        return []
    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError('SFX job must be a JSON object')
    job = data.get('job', data)
    if not isinstance(job, dict):
        raise ValueError('SFX job must contain an object')
    effects = job.get('effects', [])
    if not isinstance(effects, list):
        raise ValueError('SFX job effects must be a list')
    events = []
    for effect in effects:
        if not isinstance(effect, dict):
            raise ValueError('Every SFX effect must be an object')
        start = effect.get('start', 0)
        if not isinstance(start, (int, float)) or not math.isfinite(start) or start < 0:
            raise ValueError('Every effect start must be finite and nonnegative')
        if start < duration:
            events.append((float(start), str(effect.get('id', 'motion'))))
    return events


def synthesize(path, duration, events):
    """Original seeded noise + descending sine sweep, soft envelope, low gain."""
    samples = array('f', [0]) * int(math.ceil(duration * RATE))
    for start, identity in events:
        seed = int.from_bytes(hashlib.sha256(f'{identity}:{start}'.encode()).digest()[:8], 'big')
        rng = random.Random(seed)
        offset, length = round(start * RATE), round(.18 * RATE)
        phase = 0.0
        for index in range(min(length, len(samples) - offset)):
            progress = index / length
            frequency = 1450 * (350 / 1450) ** progress
            phase += 2 * math.pi * frequency / RATE
            envelope = min(1, progress / .08) * (1 - progress) ** 2
            samples[offset + index] += .035 * envelope * (.7 * math.sin(phase) + .3 * rng.uniform(-1, 1))
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        # Bounded chunking avoids a giant argument list for a long soundtrack.
        for start in range(0, len(samples), RATE):
            chunk = samples[start:start + RATE]
            output.writeframes(struct.pack('<' + 'h' * len(chunk), *(round(max(-1, min(1, value)) * 32767) for value in chunk)))


def mix(source, output, music=None, sfx_job=None):
    for tool in ['ffmpeg', 'ffprobe']:
        if not shutil.which(tool):
            raise ValueError(f'Missing {tool}')
    source, output = Path(source).resolve(), Path(output).resolve()
    music = Path(music).resolve() if music else None
    if output == source or (music and output == music):
        raise ValueError('Output must differ from all source media')
    if output.exists():
        raise ValueError('Output already exists; choose a new output file')
    if output.suffix.lower() != '.mp4':
        raise ValueError('Output must be an .mp4 file')
    if not source.is_file() or (music and not music.is_file()):
        raise ValueError('Source or music file does not exist')
    info = probe(source)
    video = next((stream for stream in info['streams'] if stream['codec_type'] == 'video'), None)
    if video is None or not any(stream['codec_type'] == 'audio' for stream in info['streams']):
        raise ValueError('Input must contain video and narration audio')
    duration = float(info['format']['duration'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Input duration must be positive and finite')
    events = sound_events(sfx_job, duration)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.linea-audio-', dir=output.parent) as folder:
        folder = Path(folder)
        args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', source]
        filters = ['[0:a:0]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[voice0]']
        inputs, next_index = [], 1
        if music:
            args += ['-stream_loop', '-1', '-i', music]
            filters += ['[voice0]asplit=2[voice][sidechain]',
                        f'[{next_index}:a:0]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,volume=0.12[music]',
                        '[music][sidechain]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=250[ducked]']
            inputs += ['[voice]', '[ducked]']
            next_index += 1
        else:
            inputs.append('[voice0]')
        if events:
            synthesize(folder / 'sfx.wav', duration, events)
            args += ['-i', folder / 'sfx.wav']
            inputs.append(f'[{next_index}:a:0]')
        filters.append(''.join(inputs) + f'amix=inputs={len(inputs)}:duration=first:normalize=0,atrim=duration={duration}[mixed]')
        run(args + ['-filter_complex', ';'.join(filters), '-map', '[mixed]', '-t', duration,
                    '-c:a', 'pcm_s24le', folder / 'mix.wav'])
        measured = run(['ffmpeg', '-hide_banner', '-i', folder / 'mix.wav', '-af',
                        'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
        blocks = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', measured.stderr.decode(errors='replace'), flags=re.S)
        if not blocks:
            raise ValueError('FFmpeg did not return loudness measurements')
        loudness = json.loads(blocks[-1])
        fields = {'measured_I': 'input_i', 'measured_TP': 'input_tp', 'measured_LRA': 'input_lra',
                  'measured_thresh': 'input_thresh', 'offset': 'target_offset'}
        finite = all(math.isfinite(float(loudness[key])) for key in fields.values())
        normalize = 'loudnorm=I=-16:TP=-1.5:LRA=11'
        if finite:
            normalize += ':' + ':'.join(f'{key}={loudness[value]}' for key, value in fields.items()) + ':linear=true'
        codec = 'copy' if video['codec_name'] == 'h264' else 'libx264'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', source, '-i', folder / 'mix.wav',
             '-map', '0:v:0', '-map', '1:a:0', '-c:v', codec, '-c:a', 'aac', '-b:a', '192k',
             '-af', normalize, '-ar', RATE, '-t', duration, '-movflags', '+faststart', folder / 'final.mp4'])
        # Atomic exclusive publication; a concurrently created output is never overwritten.
        os.link(folder / 'final.mp4', output)
    return {'output': str(output), 'duration': duration, 'videoCodec': 'h264', 'videoCopy': codec == 'copy',
            'musicDucked': bool(music), 'sfxEvents': len(events), 'sfxSource': 'original procedural synthesis',
            'loudnessTargetLUFS': -16, 'truePeakTargetDBTP': -1.5, 'twoPass': finite,
            'measuredInput': loudness}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    command = sub.add_parser('mix')
    command.add_argument('input')
    command.add_argument('--out', required=True)
    command.add_argument('--music')
    command.add_argument('--sfx-job')
    args = parser.parse_args()
    try:
        print(json.dumps(mix(args.input, args.out, args.music, args.sfx_job), indent=2))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f'Audio mix failed: {exc}\n')


if __name__ == '__main__':
    main()
