#!/usr/bin/env python3
"""Turns rendered sub-frames into the finished video.

1. Averages each frame's motion blur samples in linear light.
2. Adds the brand's film grain: monochrome, soft light blend, 5 percent.
3. Encodes H.264 (BT.709, yuv420p, faststart) with the soundtrack, plus a silent cut.

    python3 compose.py            frames, then both MP4s, then the cover if build/cover_raw.png exists
    python3 compose.py --encode   skip straight to encoding existing frames
"""
import subprocess
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
SUB = HERE / 'build' / 'sub'
FRAMES = HERE / 'build' / 'frames'
FPS = 30
GRAIN = 0.05          # soft light opacity
OUT = HERE / 'Sandiford_Digital_Showreel_15s.mp4'
OUT_SILENT = HERE / 'Sandiford_Digital_Showreel_15s_silent.mp4'

_lin = (np.arange(256) / 255.0)
_lin = np.where(_lin <= 0.04045, _lin / 12.92, ((_lin + 0.055) / 1.055) ** 2.4).astype(np.float32)


def to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def soft_light(cb, cs):
    d = np.where(cb <= 0.25, ((16 * cb - 12) * cb + 4) * cb, np.sqrt(cb))
    return np.where(cs <= 0.5, cb - (1 - 2 * cs) * cb * (1 - cb), cb + (2 * cs - 1) * (d - cb))


def grain(img, seed):
    rng = np.random.default_rng(seed)
    g = gaussian_filter(rng.standard_normal(img.shape[:2]).astype(np.float32), 0.65)
    g = np.clip(0.5 + g / (g.std() + 1e-6) * 0.2, 0, 1)[..., None]
    return img + GRAIN * (soft_light(img, g) - img)


def save(img, path):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, compress_level=1)


def compose(args):
    f, files = args
    acc = None
    for p in files:
        a = _lin[np.asarray(Image.open(p).convert('RGB'))]
        acc = a if acc is None else acc + a
    save(grain(to_srgb(acc / len(files)), 1000 + f), FRAMES / f'f{f:04d}.png')
    return f


def cover():
    raw = HERE / 'build' / 'cover_raw.png'
    if raw.exists():
        img = np.asarray(Image.open(raw).convert('RGB')) / 255.0
        save(grain(img, 7), HERE / 'cover.png')
        print('cover.png')


def frames():
    groups = defaultdict(list)
    for p in sorted(SUB.glob('f*_*.png')):
        groups[int(p.name[1:5])].append(p)
    missing = [f for f in range(15 * FPS) if f not in groups]
    if missing:
        sys.exit(f'missing frames: {missing[:10]}{"..." if len(missing) > 10 else ""}')
    FRAMES.mkdir(parents=True, exist_ok=True)
    with Pool(4) as pool:
        for i, f in enumerate(pool.imap_unordered(compose, sorted(groups.items()), chunksize=4)):
            if i % 50 == 0:
                print(f'composed {i} frames')


def encode():
    video = ['-framerate', str(FPS), '-i', str(FRAMES / 'f%04d.png')]
    vcodec = ['-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
              '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-level', '4.1',
              '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
              '-movflags', '+faststart']
    wav = HERE / 'build' / 'soundtrack.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *video, '-i', str(wav), *vcodec,
                    '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', str(OUT)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *video, *vcodec, '-an', str(OUT_SILENT)], check=True)
    for p in (OUT, OUT_SILENT):
        print(p.name, f'{p.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    if '--encode' not in sys.argv:
        frames()
    encode()
    cover()
