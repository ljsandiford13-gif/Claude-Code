#!/usr/bin/env python3
"""Builds the showreel soundtrack from build/cues.json.

Everything is synthesised here, so there is nothing to license. 120 BPM, key of D.
The score follows the picture: bright chords at the surface, a muffled drop as the
page sinks into deep water, a half time groove under the work, light again on the
aqua report slide, and a low D major bloom under the sign off.

Each word reveal plays a soft droplet note from the current chord, panned to where
the word sits on screen, so the typography plays the melody.

    python3 audio.py            writes build/soundtrack.wav (48 kHz, stereo, float)
"""
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import minimum_filter1d
from scipy.signal import butter, fftconvolve, istft, lfilter, sosfilt, stft

HERE = Path(__file__).resolve().parent
SR = 48000
BEAT = 0.5
rng = np.random.default_rng(20261001)

cue_doc = json.loads((HERE / 'build' / 'cues.json').read_text())
DUR = float(cue_doc['meta']['DUR'])
CUES = cue_doc['cues']
N = int(round(DUR * SR))

dry = np.zeros((N, 2))      # direct mix
send = np.zeros((N, 2))     # reverb send


# ---------------------------------------------------------------- helpers
NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def hz(name):
    return 440.0 * 2 ** ((12 * (int(name[-1]) + 1) + NOTE[name[:-1]] - 69) / 12)


def pan_gains(p):
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.cos(a), np.sin(a)


def place(sig, t0, pan=0.0, gain=1.0, rev=0.0):
    """Add a mono or stereo signal at time t0 (s), with constant power pan and reverb send."""
    sig = np.asarray(sig, dtype=float)
    if sig.ndim == 1:
        gl, gr = pan_gains(pan)
        sig = np.stack([sig * gl, sig * gr], axis=1)
    i0 = int(round(t0 * SR))
    j0, j1 = max(0, -i0), min(len(sig), N - i0)
    if j1 <= j0:
        return
    seg = sig[j0:j1] * gain
    dry[i0 + j0:i0 + j1] += seg
    if rev:
        send[i0 + j0:i0 + j1] += seg * rev


def tt(dur):
    return np.arange(int(round(dur * SR))) / SR


def env_ad(t, a, d):
    return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / d)


def bandpass(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def highpass(x, f, order=2):
    return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x, axis=0)


def lowpass(x, f, order=2):
    return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x, axis=0)


def shaped_noise(dur, fc, bw=0.6, env=None):
    """Noise whose spectrum is a moving band. fc is a function of time (s) in Hz, bw in octaves."""
    n = int(round(dur * SR))
    x = rng.standard_normal(n + 2048)
    f, frames, Z = stft(x, fs=SR, nperseg=1024, noverlap=768)
    centres = np.array([fc(min(max(ti, 0), dur)) for ti in frames])
    lf = np.log2(np.maximum(f, 1.0))[:, None]
    mask = np.exp(-0.5 * ((lf - np.log2(centres)[None, :]) / bw) ** 2)
    _, y = istft(Z * mask, fs=SR, nperseg=1024, noverlap=768)
    y = y[:n]
    y /= np.max(np.abs(y)) + 1e-9
    if env is not None:
        y *= env(np.arange(n) / SR)
    return y


# ---------------------------------------------------------------- score
CHORDS = [  # start, end, voicing
    (0.0, 2.5, ['D3', 'A3', 'C#4', 'E4', 'F#4']),     # Dmaj9, surface
    (2.5, 6.0, ['B2', 'F#3', 'A3', 'C#4', 'D4']),     # Bm9, under
    (6.0, 8.0, ['G2', 'D3', 'F#3', 'A3', 'B3']),      # Gmaj9
    (8.0, 9.0, ['A2', 'E3', 'G3', 'B3', 'D4']),       # A9sus
    (9.0, 10.5, ['E3', 'B3', 'D4', 'F#4', 'G4']),     # Em9, aqua light
    (10.5, 12.0, ['A2', 'E3', 'G3', 'B3', 'F#4']),    # A13sus
    (12.0, DUR, ['D2', 'A2', 'F#3', 'C#4', 'E4']),    # Dmaj9, the deep
]


def chord_at(t):
    for a, b, v in CHORDS:
        if a <= t < b:
            return v
    return CHORDS[-1][2]


# brightness of the pad: open at the surface, muffled under water, light again on aqua
BRIGHT_T = [0.0, 2.45, 3.2, 6.0, 8.9, 9.6, 11.4, 12.3, DUR]
BRIGHT_F = [2600, 2600, 520, 1200, 1700, 3400, 3000, 480, 1100]


def brightness(t):
    return np.interp(t, BRIGHT_T, BRIGHT_F)


def pad():
    for ci, (a, b, voicing) in enumerate(CHORDS):
        start = max(0.0, a - 0.3)
        stop = min(DUR, b + 0.7)
        t = np.arange(int(start * SR), int(stop * SR)) / SR
        att = 0.6 if ci == 0 else 0.3
        e = np.clip((t - start) / att, 0, 1) ** 1.5
        e *= np.clip((b + 0.7 - t) / 0.7, 0, 1) if b < DUR else np.clip((DUR - t) / 1.2, 0, 1)
        fc = brightness(t)
        for ni, name in enumerate(voicing):
            f0 = hz(name)
            for vi, (cents, pan) in enumerate([(-7, -0.7), (0, 0.0), (7, 0.7)]):
                vib = 1 + 0.0012 * np.sin(2 * np.pi * (0.17 + 0.05 * vi) * t + rng.uniform(0, 6.28))
                ph = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200) * vib) / SR
                K = int(min(28, 7000 / f0))
                v = np.zeros_like(t)
                for k in range(1, K + 1):
                    g = (1.0 / k) / np.sqrt(1 + (k * f0 / fc) ** 4)
                    v += g * np.sin(k * ph + rng.uniform(0, 6.28))
                level = 0.022 * (0.8 if ni == 0 else 1.0)
                place(v * e * level, start, pan=pan * 0.8, rev=0.35)


def droplet(f, dur=1.1, bright=1.0):
    """Soft FM mallet with a tiny upward bend at the start, like a drop hitting water."""
    t = tt(dur)
    fb = f * (1 + 0.012 * np.exp(-t / 0.012))
    ph = 2 * np.pi * np.cumsum(fb) / SR
    idx = bright * 1.8 * np.exp(-t / 0.05)
    y = np.sin(ph + idx * np.sin(2 * ph))
    return y * env_ad(t, 0.002, 0.32)


def word_notes():
    """Words climb through the chord tones of their scene."""
    per_scene = {}
    for c in CUES:
        if c['k'] == 'word':
            per_scene.setdefault(c['scene'], []).append(c)
    ladders = {
        1: ['D5', 'F#5', 'A5', 'C#6'],
        2: ['B4', 'D5', 'F#5', 'A5', 'C#6', 'D6'],
        3: ['G5', 'A5', 'B5', 'D6'],
        4: ['E5', 'G5', 'B5', 'D6', 'E6', 'F#6', 'G6'],
    }
    for scene, cues in per_scene.items():
        for i, c in enumerate(cues):
            note = ladders[scene][min(i, len(ladders[scene]) - 1)]
            place(droplet(hz(note)), c['t'], pan=c['pan'] * 0.75, gain=0.1, rev=0.55)


def sign_shimmer():
    """The wordmark rises letter by letter: a fast D major run, then an echo an octave down."""
    run = ['D5', 'E5', 'F#5', 'A5', 'C#6', 'D6', 'E6', 'F#6', 'A6',
           'A4', 'C#5', 'D5', 'E5', 'F#5', 'A5', 'C#6', 'D6']
    chars = [c for c in CUES if c['k'] == 'char']
    for i, c in enumerate(chars):
        place(droplet(hz(run[i % len(run)]), dur=1.4, bright=0.7), c['t'], pan=c['pan'] * 0.8,
              gain=0.05 if i < 9 else 0.04, rev=0.7)


def kick(amp=1.0, f_hi=140, f_lo=46, dec=0.18):
    t = tt(0.6)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec)
    click = highpass(rng.standard_normal(len(t)) * np.exp(-t / 0.002), 1500) * 0.25
    return np.tanh(1.6 * (body + click)) * amp


def clap():
    t = tt(0.4)
    y = np.zeros(len(t))
    for k, d in enumerate([0.0, 0.011, 0.022, 0.034]):
        i = int(d * SR)
        n = rng.standard_normal(len(t) - i) * np.exp(-np.arange(len(t) - i) / SR / (0.006 if k < 3 else 0.12))
        y[i:] += n
    return bandpass(y, 900, 4200) * 0.8


def hat(open_=False):
    t = tt(0.3 if open_ else 0.08)
    y = highpass(rng.standard_normal(len(t)), 7000, order=4)
    return y * np.exp(-t / (0.09 if open_ else 0.018))


def groove():
    """Half time at 120 BPM: kick on the beat every second, clap between, hats in eighths."""
    start, stop = 3.0, 11.5
    for i in range(int((stop - start) / BEAT)):
        t = start + i * BEAT
        in_aqua = 9.0 <= t < 11.5
        if i % 2 == 0:
            place(kick(1.0 if t > 3.01 else 1.25), t, gain=0.42 if in_aqua else 0.5)
        else:
            place(clap(), t, pan=0.05, gain=0.09, rev=0.4)
    for i in range(int((stop - 3.5) / (BEAT / 2))):
        t = 3.5 + i * BEAT / 2
        off = (i % 2) == 1
        if 8.9 < t < 9.05:
            continue
        g = (0.05 if off else 0.028) * (1.15 if 6.0 <= t < 9.0 else 1.0)
        place(hat(open_=(off and i % 8 == 7)), t, pan=0.35 if off else -0.25, gain=g, rev=0.1)


def bass():
    """Sub bass on the chord roots, pumping against the kick. Upper harmonics so phones hear it."""
    roots = [(3.0, 6.0, 'B1'), (6.0, 8.0, 'G1'), (8.0, 9.0, 'A1'), (9.0, 10.5, 'E2'), (10.5, 11.5, 'A1')]
    for a, b, name in roots:
        t = np.arange(int(a * SR), int(b * SR)) / SR
        f = hz(name)
        ph = 2 * np.pi * f * t
        tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph) + 0.08 * np.sin(4 * ph)
        since_kick = (t - 3.0) % 1.0
        pump = 1 - 0.75 * np.exp(-since_kick / 0.09)
        gate = 0.6 + 0.4 * np.exp(-((t - 3.0) % 0.25) / 0.08)
        edge = np.clip((t - a) / 0.02, 0, 1) * np.clip((b - t) / 0.03, 0, 1)
        place(np.tanh(1.2 * tone) * pump * gate * edge, a, gain=0.085)


def bubble(f0, dur):
    t = tt(dur)
    f = f0 * (1 + 2.5 * t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(t, 0.001, dur * 0.3)


def sfx():
    for c in CUES:
        t0, k = c['t'], c['k']
        if k == 'click':
            t = tt(0.05)
            y = highpass(rng.standard_normal(len(t)) * np.exp(-t / 0.0015), 2000) * 0.6
            y += np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.008) * 0.5
            place(y, t0, pan=0.25, gain=0.12, rev=0.1)
        elif k == 'tap':
            t = tt(0.08)
            y = np.sin(2 * np.pi * 1250 * t) * np.exp(-t / 0.012)
            place(y, t0, pan=0.45, gain=0.1, rev=0.15)
        elif k == 'cursor':
            y = shaped_noise(0.45, lambda s: 2500 + 3000 * s, bw=0.5, env=lambda s: np.sin(np.pi * np.clip(s / 0.45, 0, 1)) ** 2)
            place(y, t0, pan=0.5, gain=0.018)
        elif k == 'restyle':
            d = c['d']
            y = shaped_noise(d + 0.1, lambda s: 1800 * 2 ** (2.2 * s / d), bw=0.35,
                             env=lambda s: np.sin(np.pi * np.clip(s / (d + 0.1), 0, 1)) ** 1.5)
            place(y, t0, pan=-0.2, gain=0.045, rev=0.4)
            place(droplet(hz('E6'), bright=0.6), t0 + d - 0.05, pan=0.3, gain=0.06, rev=0.6)
        elif k == 'descend':
            d = c['d']
            # rising breath into the plunge, a sinking wash, then the boom
            pre = shaped_noise(0.55, lambda s: 600 * 2 ** (3 * s / 0.55), bw=0.7, env=lambda s: (s / 0.55) ** 2.2)
            place(pre, t0 - 0.5, gain=0.07, rev=0.3)
            wash = shaped_noise(d + 0.4, lambda s: 3200 * 2 ** (-3.6 * min(s / d, 1)), bw=0.8,
                                env=lambda s: np.exp(-((s - d * 0.45) / (d * 0.35)) ** 2))
            place(np.stack([wash, np.roll(wash, 240)], axis=1), t0, gain=0.12, rev=0.35)
            boom_t = t0 + d * 0.5
            t = tt(1.6)
            sub = np.sin(2 * np.pi * np.cumsum(38 + 50 * np.exp(-t / 0.06)) / SR) * np.exp(-t / 0.45)
            place(np.tanh(1.8 * sub) * 0.9, boom_t, gain=0.45)
            for _ in range(10 if t0 < 5 else 6):
                bt = boom_t + rng.uniform(-0.1, 0.6)
                place(bubble(rng.uniform(380, 1300), rng.uniform(0.03, 0.07)), bt,
                      pan=rng.uniform(-0.8, 0.8), gain=rng.uniform(0.012, 0.03), rev=0.5)
        elif k == 'draw':
            y = shaped_noise(0.85, lambda s: 900 * 2 ** (1.5 * s / 0.85), bw=0.4, env=lambda s: np.sin(np.pi * np.clip(s / 0.85, 0, 1)))
            place(y, t0, pan=-0.3, gain=0.025, rev=0.3)
        elif k == 'grid':
            for i in range(12):
                t = tt(0.03)
                place(np.sin(2 * np.pi * 3200 * t) * np.exp(-t / 0.004), t0 + i * 0.025,
                      pan=-0.8 + i * 0.145, gain=0.03)
        elif k == 'wire':
            for i in range(7):
                y = shaped_noise(0.5, lambda s: 2600, bw=0.3, env=lambda s: np.sin(np.pi * np.clip(s / 0.5, 0, 1)) ** 3)
                place(y, t0 + i * 0.05, pan=-0.6 + i * 0.2, gain=0.006)
        elif k == 'snap':
            t = tt(0.12)
            y = np.sin(2 * np.pi * np.cumsum(180 + 400 * np.exp(-t / 0.01)) / SR) * np.exp(-t / 0.03)
            place(y, t0, pan=0.3, gain=0.16, rev=0.2)
        elif k == 'design':
            for i, n in enumerate(['A5', 'C#6', 'F#6', 'A6']):
                place(droplet(hz(n), bright=0.5), t0 + i * 0.05, pan=-0.4 + i * 0.27, gain=0.03, rev=0.7)
        elif k == 'skel':
            y = shaped_noise(0.3, lambda s: 1200 * 2 ** (-1.5 * s / 0.3), bw=0.6, env=lambda s: np.sin(np.pi * np.clip(s / 0.3, 0, 1)))
            place(y, t0, gain=0.03)
        elif k == 'morph':
            d = c['d']
            y = shaped_noise(d + 0.2, lambda s: 700 * 2 ** (2.0 * np.sin(np.pi * min(s / d, 1))), bw=0.5,
                             env=lambda s: np.sin(np.pi * np.clip(s / (d + 0.2), 0, 1)) ** 1.5)
            place(np.stack([y * 0.8, np.roll(y, 300)], axis=1), t0, gain=0.07, rev=0.3)
        elif k == 'roll':
            for i in range(2):
                t = tt(0.03)
                place(np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.005), t0 + i * 0.06, pan=0.6, gain=0.03)
        elif k in ('site', 'swap'):
            # a soft tom pitched to the chord root, and a short page turn
            root = hz(chord_at(t0 + 0.01)[0]) * 2
            t = tt(0.5)
            tom = np.sin(2 * np.pi * np.cumsum(root * (1 + 0.4 * np.exp(-t / 0.02))) / SR) * np.exp(-t / 0.16)
            place(tom, t0, gain=0.12, rev=0.25)
            if k == 'swap':
                y = shaped_noise(0.45, lambda s: 2000 * 2 ** (1.2 * s / 0.45), bw=0.5,
                                 env=lambda s: np.sin(np.pi * np.clip(s / 0.45, 0, 1)) ** 2)
                place(np.stack([y * 1.0, y * 0.6], axis=1), t0, gain=0.05, rev=0.2)
        elif k == 'wipe':
            d = c['d']
            y = shaped_noise(d + 0.2, lambda s: 1500 * 2 ** (2.2 * min(s / d, 1)), bw=0.6,
                             env=lambda s: np.sin(np.pi * np.clip(s / (d + 0.2), 0, 1)) ** 1.6)
            sweep = np.clip(np.arange(len(y)) / SR / d, 0, 1)
            gl, gr = pan_gains(-0.9 + 1.8 * sweep)
            place(np.stack([y * gl, y * gr], axis=1), t0, gain=0.09, rev=0.35)
            # surfacing: an airy shimmer of upper chord tones
            for i, n in enumerate(['B5', 'D6', 'F#6', 'G6', 'B6']):
                place(droplet(hz(n), bright=0.4), t0 + 0.25 + i * 0.07, pan=-0.6 + i * 0.3, gain=0.025, rev=0.8)
        elif k == 'chart':
            d = c['d']
            t = tt(d + 0.3)
            f = hz('E4') * 2 ** (np.clip(t / d, 0, 1) * 7 / 12) * (1 + 0.004 * np.sin(2 * np.pi * 5 * t))
            y = np.sin(2 * np.pi * np.cumsum(f) / SR)
            y = y * np.sin(np.pi * np.clip(t / (d + 0.3), 0, 1)) ** 1.2
            place(y, t0, pan=0.0, gain=0.03, rev=0.6)
        elif k == 'dot':
            place(droplet(hz('F#6'), dur=1.6, bright=1.2), t0, pan=0.75, gain=0.11, rev=0.6)
            place(droplet(hz('D6'), dur=1.6, bright=0.8), t0 + 0.08, pan=0.6, gain=0.06, rev=0.6)
        elif k == 'sign':
            # the bloom: deep sub, a soft kick, a swelling noise breath before it
            pre = shaped_noise(0.5, lambda s: 400 * 2 ** (3.5 * s / 0.5), bw=0.9, env=lambda s: (s / 0.5) ** 3)
            place(np.stack([pre, np.roll(pre, 200)], axis=1), t0 - 0.5, gain=0.06, rev=0.5)
            t = tt(3.0)
            sub = np.sin(2 * np.pi * hz('D2') * t) + 0.3 * np.sin(2 * np.pi * hz('D3') * t)
            place(np.tanh(1.4 * sub) * env_ad(t, 0.01, 0.9), t0, gain=0.16)
            place(kick(1.0, f_hi=120, f_lo=40, dec=0.3), t0, gain=0.45)
        elif k == 'cta':
            place(droplet(hz('A5'), dur=1.6, bright=0.9), t0, pan=-0.15, gain=0.08, rev=0.6)
            place(droplet(hz('D6'), dur=1.8, bright=0.9), t0 + 0.13, pan=0.15, gain=0.08, rev=0.6)


def reverb_ir(dur=2.6, rt60=2.1):
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = 10 ** (-3 * t / rt60)
    ir = np.zeros((n, 2))
    for ch in range(2):
        bright = lowpass(rng.standard_normal(n), 6500)
        dark = lowpass(rng.standard_normal(n), 1800)
        w = np.exp(-t / 0.5)
        ir[:, ch] = (bright * w + dark * (1 - w)) * env
    pre = int(0.022 * SR)
    ir = np.concatenate([np.zeros((pre, 2)), ir])
    for d, g in [(0.011, 0.5), (0.017, 0.35), (0.029, 0.3)]:
        i = int(d * SR)
        ir[i, 0] += g
        ir[i + 37, 1] += g
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def master(x):
    x = highpass(x, 28)
    # gentle glue: slow RMS compressor
    lvl = np.sqrt(lfilter([0.002], [1, -0.998], np.mean(x ** 2, axis=1)) + 1e-12)
    thr = 10 ** (-20 / 20)
    gain = np.where(lvl > thr, (lvl / thr) ** (1 / 2.0 - 1), 1.0)
    x = x * gain[:, None]
    # loudness to -14 LUFS for social, then a lookahead limiter at -1 dBFS
    try:
        import pyloudnorm as pyln
        meter = pyln.Meter(SR)
        loud = meter.integrated_loudness(x)
        x = x * 10 ** ((-14.0 - loud) / 20)
    except ImportError:
        x = x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 10 ** (-17 / 20)
    ceiling = 10 ** (-1.0 / 20)
    peak = np.max(np.abs(x), axis=1)
    need = np.minimum(1.0, ceiling / np.maximum(peak, 1e-9))
    look = int(0.004 * SR)
    need = minimum_filter1d(need, size=2 * look + 1)
    rel = np.exp(-1 / (0.08 * SR))
    smooth = lfilter([1 - rel], [1, -rel], need)
    g = np.minimum(need, smooth)
    x = x * g[:, None]
    # fades
    fi = int(0.01 * SR)
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo_t = np.arange(N) / SR
    x *= np.clip((DUR - fo_t) / 0.9, 0, 1)[:, None] ** 1.5
    return np.clip(x, -ceiling, ceiling)


def main():
    pad()
    word_notes()
    sign_shimmer()
    groove()
    bass()
    sfx()
    ir = reverb_ir()
    wet = np.stack([fftconvolve(send[:, ch], ir[:, ch])[:N] for ch in range(2)], axis=1)
    mix = master(dry + wet * 0.32)
    out = HERE / 'build' / 'soundtrack.wav'
    from scipy.io import wavfile
    wavfile.write(out, SR, mix.astype(np.float32))
    try:
        import pyloudnorm as pyln
        print(f'loudness {pyln.Meter(SR).integrated_loudness(mix):.1f} LUFS, peak {20 * np.log10(np.max(np.abs(mix))):.1f} dBFS')
    except ImportError:
        pass
    print(out)


if __name__ == '__main__':
    main()
