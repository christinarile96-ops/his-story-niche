#!/usr/bin/env python3
"""Synthesise the SFX + music for a project and mix them under the voiceover.

  python3 engine/sound.py <project>

Cues come from projects/<project>/shots.py:
  SFX(timing)   -> [(name, t, gain, {opts}), ...]
  MUSIC(timing) -> [(t, section), ...]   sections: warm, sad, hold, tension, suspense, swell, out
Writes projects/<project>/mix.wav at -14 LUFS. Everything is procedural (no samples)
with fixed seeds so renders repeat exactly.
"""
import importlib.util
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
rng = np.random.default_rng(11)


# ---------------------------------------------------------------- building blocks
def t_axis(d):
    return np.arange(int(d * SR)) / SR


def noise(d):
    return rng.standard_normal(int(d * SR))


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], btype='band', fs=SR, output='sos'), x)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, btype='low', fs=SR, output='sos'), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, btype='high', fs=SR, output='sos'), x)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (peak / m) if m > 0 else x


def env_adsr(n, a=0.01, r=0.1):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def reverb(x, secs=1.6, wet=0.35, tone=5000):
    ir = noise(secs) * np.exp(-t_axis(secs) * 6.9 / secs)
    ir = lp(ir, tone)
    ir[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    y = fftconvolve(x, ir)[: len(x) + len(ir) - 1]
    y = norm(y, np.max(np.abs(x)) + 1e-9)
    dry = np.pad(x, (0, len(y) - len(x)))
    return dry * (1 - wet) + y * wet


def thump(d, f0, f1, k, tau):
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t / k)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tau)


# ---------------------------------------------------------------- sfx
def whistle(opts):
    """Two-note human whistle (high, then low). opts: notes, dist (0 near .. 1 far), kid."""
    notes = opts.get('notes', [(1568, 0.34), (1175, 0.42)])
    if opts.get('kid'):
        notes = [(f * 1.12, d * 0.9) for f, d in notes]
    out = []
    prev = notes[0][0] * 0.94
    for f, d in notes:
        t = t_axis(d)
        glide = prev + (f - prev) * (1 - np.exp(-t / 0.035))
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.15, 0, 1)
        ph = 2 * np.pi * np.cumsum(glide * vib) / SR
        tone = np.sin(ph) + 0.04 * np.sin(2 * ph)
        breath = bp(noise(d), f * 0.8, f * 1.25) * 0.12
        e = np.clip(t / 0.03, 0, 1) * np.clip((d - t) / 0.06, 0, 1)
        out.append((tone + breath) * e)
        out.append(np.zeros(int(0.03 * SR)))
        prev = f
    x = np.concatenate(out)
    dist = opts.get('dist', 0.0)
    if dist > 0:
        x = lp(x, 6000 - 4000 * dist)
        x = reverb(x, 1.2 + 1.8 * dist, 0.3 + 0.55 * dist)
    else:
        x = reverb(x, 0.8, 0.18)
    if opts.get('weak'):
        x = x * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t_axis(len(x) / SR)))
        x += bp(noise(len(x) / SR), 1500, 5000) * 0.25 * np.exp(-t_axis(len(x) / SR) / 0.6)
    return norm(x)


def whoosh(opts):
    d = opts.get('d', 0.45)
    n = int(d * SR)
    x = noise(d)
    pos = np.linspace(0, 1, n)
    out = np.zeros(n)
    bands = np.geomspace(opts.get('lo', 300), opts.get('hi', 5000), 6)
    for i in range(5):
        c = i / 4
        out += bp(x, bands[i], bands[i + 1]) * np.exp(-((pos - c) ** 2) / 0.05)
    pk = 0.6
    e = np.where(pos < pk, np.sin(np.pi / 2 * pos / pk) ** 2, np.exp(-(pos - pk) / (1 - pk) * 4))
    return norm(out * e)


def birds(opts):
    d = opts.get('d', 5)
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 2.2)):
        st = rng.uniform(0, d - 0.4)
        n = rng.integers(2, 5)
        f0 = rng.uniform(2800, 4200)
        for k in range(n):
            cd = rng.uniform(0.05, 0.11)
            t = t_axis(cd)
            f = f0 * (1 + rng.uniform(-0.15, 0.25) * t / cd)
            c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / cd) ** 2
            i = int((st + k * (cd + 0.04)) * SR)
            x[i:i + len(c)] += c[: len(x) - i] * rng.uniform(0.3, 1)
    x = reverb(x, 1.0, 0.3)[: len(x)]
    e = env_adsr(len(x), 0.8, 0.8)
    return norm(x) * e


def wind(opts):
    d = opts.get('d', 6)
    t = t_axis(d)
    s = opts.get('strength', 0.6)
    x = noise(d)
    lo = lp(x, 400 + 500 * s) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.23 * t))
    howl = bp(x, 500, 900 + 900 * s, 2) * (0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + 1))) * s
    e = env_adsr(len(t), opts.get('a', 0.8), opts.get('r', 0.8))
    return norm(lo + howl) * e


def carve(opts):
    d = opts.get('d', 1.0)
    t = t_axis(d)
    x = noise(d)
    f = np.linspace(900, 2400, len(t))
    y = sum(bp(x, lo, lo * 1.6) * np.exp(-((f - lo) ** 2) / (2 * 400 ** 2)) for lo in (800, 1200, 1800, 2600))
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.7
    return norm(y * e)


def beeps(opts):
    out = []
    for f in (880, 660, 440):
        t = t_axis(0.12)
        out.append(np.sin(2 * np.pi * f * t) * env_adsr(len(t), 0.005, 0.03))
        out.append(np.zeros(int(0.07 * SR)))
    return norm(np.concatenate(out))


def radio(opts):
    d = opts.get('d', 2.4)
    x = np.zeros(int(d * SR))
    for st in np.arange(0.1, d - 0.5, 0.75):
        bl = rng.uniform(0.3, 0.55)
        burst = bp(noise(bl), 900, 3200) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * rng.uniform(7, 13) * t_axis(bl))))
        burst *= env_adsr(len(burst), 0.01, 0.05)
        i = int(st * SR)
        x[i:i + len(burst)] += burst[: len(x) - i]
        clk = int((st + bl) * SR)
        if clk < len(x) - 200:
            x[clk:clk + 200] += np.exp(-np.arange(200) / 30) * 1.5
    return norm(x)


def tick(opts):
    t = t_axis(0.05)
    return norm(hp(noise(0.05), 2500) * np.exp(-t / 0.006) + 0.5 * np.sin(2 * np.pi * 3000 * t) * np.exp(-t / 0.01))


def heartbeat(opts):
    d = opts.get('d', 3)
    x = np.zeros(int(d * SR))
    period = opts.get('period', 0.85)
    for st in np.arange(0, d - 0.4, period):
        for off, g in ((0, 1.0), (0.22, 0.7)):
            b = thump(0.25, 70, 40, 0.03, 0.07) * g
            i = int((st + off) * SR)
            x[i:i + len(b)] += b[: len(x) - i]
    return norm(lp(x, 300))


def crunch(opts):
    n = opts.get('n', 4)
    gap = opts.get('gap', 0.42)
    x = np.zeros(int((n * gap + 0.4) * SR))
    for k in range(n):
        d = 0.18
        t = t_axis(d)
        grains = (rng.random(len(t)) < 0.02).astype(float) * rng.uniform(0.3, 1, len(t))
        c = lp(bp(noise(d), 300, 4000) * 0.4 + lp(grains, 3000) * 3, 5000) * np.exp(-t / 0.06)
        g = opts.get('g0', 0.4) + (1 - opts.get('g0', 0.4)) * k / max(1, n - 1)
        i = int(k * gap * SR)
        x[i:i + len(c)] += c * g
    return norm(x)


def click(opts):
    t = t_axis(0.08)
    return norm(hp(noise(0.08), 1500) * np.exp(-t / 0.004) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.008))


def impact(opts):
    body = thump(1.4, 110, 30, 0.08, 0.45)
    air = lp(noise(1.4), 800) * np.exp(-t_axis(1.4) / 0.25) * 0.5
    return norm(reverb(np.tanh(1.5 * norm(body + air)), 1.8, 0.35))


def riser(opts):
    d = opts.get('d', 1.2)
    t = t_axis(d)
    x = noise(d)
    y = np.zeros_like(x)
    for k, f in enumerate(np.geomspace(400, 6000, 8)):
        y += bp(x, f, f * 1.4) * np.clip((t / d) * 8 - k, 0, 1)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 900, len(t))) / SR) * 0.3
    return norm((y + tone) * (t / d) ** 2)


def fire(opts):
    d = opts.get('d', 3)
    x = lp(noise(d), 600) * 0.3
    pops = (rng.random(int(d * SR)) < 0.0009).astype(float) * rng.uniform(0.3, 1, int(d * SR))
    x += hp(lp(pops, 6000), 800) * 6
    return norm(x) * env_adsr(int(d * SR), 0.4, 0.4)


def engine(opts):
    d = opts.get('d', 3)
    t = t_axis(d)
    f = 48 * (1 + 0.05 * np.sin(2 * np.pi * 0.7 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = sum(np.sin(k * ph) / k for k in range(1, 14))
    rough = lp(noise(d), 250) * 0.6
    return norm(lp(saw + rough, 900)) * env_adsr(len(t), 0.5, 0.6)


def laugh(opts):
    """A few overlapping 'ha' bursts from boys, dry and short."""
    d = opts.get('d', 1.8)
    x = np.zeros(int(d * SR))
    for voice in range(3):
        f0 = rng.uniform(170, 260)
        st = rng.uniform(0, 0.25)
        for k in range(int(rng.integers(4, 7))):
            hd = rng.uniform(0.11, 0.16)
            t = t_axis(hd)
            f = f0 * (1.15 - 0.25 * t / hd)
            ph = 2 * np.pi * np.cumsum(f) / SR
            buzz = sum(np.sin(h * ph) / h ** 1.2 for h in range(1, 18))
            breath = hp(noise(hd), 1200) * 0.6
            v = (bp(buzz, 300, 3200) + breath) * np.sin(np.pi * t / hd) ** 1.5
            i = int((st + k * rng.uniform(0.17, 0.22)) * SR)
            if i + len(v) < len(x):
                x[i:i + len(v)] += v * (1 - k * 0.1)
    return norm(reverb(x, 0.5, 0.15)[: len(x)])


SFX_BANK = dict(whistle=whistle, whoosh=whoosh, birds=birds, wind=wind, carve=carve, beeps=beeps, radio=radio,
                tick=tick, heartbeat=heartbeat, crunch=crunch, click=click, impact=impact, riser=riser,
                fire=fire, engine=engine, laugh=laugh)


# ---------------------------------------------------------------- music
def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def piano(f, d, vel=1.0):
    t = t_axis(d)
    x = np.zeros_like(t)
    for h, a, dec in ((1, 1, 1.6), (2, 0.45, 0.9), (3, 0.22, 0.6), (4, 0.12, 0.4), (5, 0.06, 0.3)):
        x += a * np.sin(2 * np.pi * f * h * (1 + 0.0004 * h * h) * t) * np.exp(-t / dec)
    x *= np.clip(t / 0.004, 0, 1)
    x[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return lp(x, 3500) * vel


def pad(freqs, d, bright=1200):
    t = t_axis(d)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.004, 0, 0.005):
            ph = 2 * np.pi * f * (1 + det) * t
            x += sum(np.sin(k * ph) / k for k in range(1, 7)) / 3
    return lp(x, bright) * env_adsr(len(t), min(1.2, d / 3), min(1.2, d / 3))


CHORDS = {  # I–V–vi–IV in C, voiced for warmth
    'C': [48, 55, 60, 64, 67], 'G': [43, 55, 59, 62, 67], 'Am': [45, 52, 57, 60, 64], 'F': [41, 53, 57, 60, 65],
    'Em': [40, 52, 55, 59, 64], 'Dm': [38, 50, 57, 62, 65],
}


def music(cues, total):
    """cues: [(t, section)], sorted."""
    out = np.zeros(int((total + 3) * SR))

    def add(x, at, g=1.0):
        i = int(at * SR)
        if i >= len(out):
            return
        out[i:i + len(x)] += x[: len(out) - i] * g

    beat = 60 / 72
    for k, (t0, sec) in enumerate(cues):
        t1 = cues[k + 1][0] if k + 1 < len(cues) else total
        if sec in ('warm', 'swell', 'sad'):
            prog = ['C', 'G', 'Am', 'F'] if sec != 'sad' else ['Am', 'F', 'C', 'G']
            bar = beat * 4 * (1.25 if sec == 'sad' else 1)
            t, ci = t0, 0
            while t < t1 - 0.05:
                ch = CHORDS[prog[ci % 4]]
                bd = min(bar, t1 - t)
                vel = {'warm': 0.5, 'sad': 0.35, 'swell': 0.75}[sec]
                if sec == 'swell':
                    vel *= 0.7 + 0.3 * min(1, (t - t0) / 6)
                add(pad([midi(n) for n in ch[1:4]], bd + 0.6, 900 if sec != 'swell' else 1800),
                    t, {'warm': 0.10, 'sad': 0.08, 'swell': 0.22}[sec])
                add(piano(midi(ch[0] - 12), bar * 1.2, 0.5), t, vel)
                arp = [ch[1], ch[2], ch[3], ch[4], ch[3], ch[2], ch[3], ch[4]]
                step = bar / 8
                for j, n in enumerate(arp):
                    if sec == 'sad' and j % 2:
                        continue
                    if t + j * step < t1 - 0.05:
                        add(piano(midi(n + 12), 1.4, 0.32 + 0.1 * (j == 0)), t + j * step, vel)
                if sec == 'swell':
                    top = [76, 74, 72, 72][ci % 4]
                    add(piano(midi(top), 2.0, 0.5), t, vel)
                    add(piano(midi(top - 2 if ci % 2 else top + 2), 1.5, 0.35), t + bar / 2, vel)
                t += bar
                ci += 1
        elif sec == 'hold':
            add(pad([midi(n) for n in CHORDS['Am'][1:4]], t1 - t0 + 0.8, 700), t0, 0.1)
        elif sec == 'tension':
            d = t1 - t0
            tt = t_axis(d)
            drone = sum(np.sin(2 * np.pi * midi(n) * tt) * a for n, a in ((33, 1), (40, 0.5), (45, 0.35)))
            add(lp(drone, 300) * env_adsr(len(tt), 0.8, 0.6) * (0.5 + 0.5 * tt / d), t0, 0.22)
            for j, tb in enumerate(np.arange(t0, t1 - 0.2, beat / 2)):
                add(piano(midi(45 if (j // 8) % 2 == 0 else 44), 0.4, 0.4) * (0.5 + 0.5 * (tb - t0) / d), tb, 0.45)
            hi = sum(np.sin(2 * np.pi * midi(n) * tt) for n in (76, 77)) * (0.5 + 0.5 * np.sin(2 * np.pi * 6 * tt))
            add(lp(hi, 3000) * np.clip((tt - d * 0.5) / (d * 0.5), 0, 1) ** 2, t0, 0.05)
        elif sec == 'suspense':
            d = t1 - t0
            tt = t_axis(d)
            drone = np.sin(2 * np.pi * midi(33) * tt) + 0.4 * np.sin(2 * np.pi * midi(40) * tt)
            add(lp(drone, 200) * env_adsr(len(tt), 0.3, 0.3), t0, 0.12)
    return out


# ---------------------------------------------------------------- mix
def read_wav(p):
    data = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                          capture_output=True, check=True).stdout
    return np.frombuffer(data, np.float32).astype(np.float64)


def main():
    project = sys.argv[1]
    pdir = ROOT / 'projects' / project
    timing = json.loads((pdir / 'timing.json').read_text())
    spec = importlib.util.spec_from_file_location('shots', pdir / 'shots.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build(timing)
    total = mod.DURATION
    n = int(total * SR)

    voice = read_wav(pdir / 'voiceover.wav')
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    voice = voice / (np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2)) + 1e-9) * 0.12

    sfx = np.zeros(n + 5 * SR)
    for name, t, gain, opts in mod.SFX(timing):
        x = SFX_BANK[name](opts)
        i = int(t * SR)
        sfx[i:i + len(x)] += x[: len(sfx) - i] * gain
    sfx = sfx[:n]

    mus = music(mod.MUSIC(timing), total)[:n]
    # duck the music under speech (fast attack, slow release)
    env = np.abs(voice)
    k = int(0.05 * SR)
    env = np.convolve(env, np.ones(k) / k, mode='same')
    speaking = np.clip(env / 0.02, 0, 1)
    sm = np.zeros_like(speaking)
    a_up, a_dn = 1 - np.exp(-1 / (0.03 * SR)), 1 - np.exp(-1 / (0.35 * SR))
    acc = 0.0
    for i in range(0, n, 64):
        target = speaking[i]
        acc += (target - acc) * (a_up if target > acc else a_dn) * 64
        acc = min(max(acc, 0), 1)
        sm[i:i + 64] = acc
    mus *= 1 - 0.45 * sm
    mus_level = 0.055
    mix = voice + sfx * 0.075 + mus / (np.max(np.abs(mus)) + 1e-9) * mus_level * 4
    fade = int(0.3 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)

    raw = pdir / 'tmp' / 'mix_raw.wav'
    raw.parent.mkdir(exist_ok=True)
    with wave.open(str(raw), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((np.clip(mix / max(1.0, np.max(np.abs(mix))), -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(raw), '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11',
                    '-ar', str(SR), '-ac', '2', str(pdir / 'mix.wav')], check=True)
    print('wrote', pdir / 'mix.wav')


if __name__ == '__main__':
    main()
