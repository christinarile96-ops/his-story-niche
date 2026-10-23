#!/usr/bin/env python3
"""Tighten a voiceover and sync it to the script.

  python3 engine/align.py <project> [--gap 0.06] [--tail 0.6] [--noise -40]

Reads projects/<project>/voiceover_raw.(mp3|wav|m4a), cuts every pause down to
--gap seconds (fast pacing), writes voiceover.wav, then force-aligns each script
word against that audio (pocketsphinx, offline) and writes timing.json, which
drives the word-by-word captions and every animation beat.

Needs: pip install pocketsphinx
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from pocketsphinx import Decoder

ROOT = Path(__file__).resolve().parent.parent
FADE = 0.008  # tiny fades at each cut so splices never click


def probe_duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout)


def silences(path, noise, min_len):
    log = subprocess.run(['ffmpeg', '-i', str(path), '-af', f'silencedetect=noise={noise}dB:d={min_len}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    return list(zip(starts, ends + [None] * (len(starts) - len(ends))))


def tighten(src, dst, gap, noise):
    total = probe_duration(src)
    cuts = []
    for a, b in silences(src, noise, 0.06):
        b = total if b is None else b
        if a <= 0.01:
            cuts.append((0, max(0, b - 0.04)))           # lead-in
        elif b >= total - 0.01:
            cuts.append((a + 0.12, total))                # tail
        elif b - a > gap:
            cuts.append((a + gap / 2, b - gap / 2))       # pause -> gap
    keep, cur = [], 0.0
    for a, b in cuts:
        if a > cur + 0.01:
            keep.append((cur, a))
        cur = max(cur, b)
    if total > cur + 0.01:
        keep.append((cur, total))

    parts, labels = [], []
    for i, (a, b) in enumerate(keep):
        fo = max(0, b - a - FADE)
        parts.append(f'[0:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,'
                     f'afade=t=in:d={FADE},afade=t=out:st={fo:.4f}:d={FADE}[s{i}]')
        labels.append(f'[s{i}]')
    graph = ';'.join(parts) + ';' + ''.join(labels) + f'concat=n={len(keep)}:v=0:a=1[out]'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(src), '-filter_complex', graph, '-map', '[out]',
                    '-ar', '48000', str(dst)], check=True)
    return total, probe_duration(dst)


def script_words(script):
    words = []
    for line_i, line in enumerate(script['lines']):
        text = line if isinstance(line, str) else line['text']
        for w in text.split():
            words.append((line_i, w))
    return words


def align(audio, words, spoken=None, pronounce=None):
    """spoken: caption word -> what is actually said ("27" -> "twenty-seven").
    pronounce: extra dictionary entries in CMU phones ("pak" -> "P AA K")."""
    spoken = {k.lower(): v for k, v in (spoken or {}).items()}
    tokens = []  # (word index, dictionary token)
    for wi, (_, w) in enumerate(words):
        said = spoken.get(re.sub(r"[^a-z0-9'\-]", '', w.lower()), w).replace('*', '')
        for part in re.sub(r"[^a-z'\- ]", '', said.lower()).replace('-', ' ').split():
            tokens.append((wi, part))
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(audio), '-ac', '1', '-ar', '16000', '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    dec = Decoder(samprate=16000, bestpath=False)
    for word, phones in (pronounce or {}).items():
        if dec.lookup_word(word) is None:
            dec.add_word(word, phones, True)
    missing = [t for _, t in tokens if dec.lookup_word(t) is None]
    if missing:
        raise SystemExit(f'Not in the pronunciation dictionary: {missing}')
    dec.set_align_text(' '.join(t for _, t in tokens))
    dec.start_utt()
    dec.process_raw(pcm, full_utt=True)
    dec.end_utt()
    segs = [s for s in dec.seg() if not s.word.startswith(('<', '[', '('))]
    if len(segs) != len(tokens):
        raise SystemExit(f'Alignment failed: got {len(segs)} words, expected {len(tokens)}. '
                         'Check the voiceover matches script.json word for word.')
    starts, ends = {}, {}
    for (wi, _), s in zip(tokens, segs):
        starts.setdefault(wi, s.start_frame / 100)
        ends[wi] = (s.end_frame + 1) / 100
    return [starts[i] for i in range(len(words))], [ends[i] for i in range(len(words))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--gap', type=float, default=0.06, help='longest pause kept, seconds')
    ap.add_argument('--tail', type=float, default=0.6, help='hold after the last word, seconds')
    ap.add_argument('--noise', type=float, default=-40, help='silence threshold, dB')
    args = ap.parse_args()

    pdir = ROOT / 'projects' / args.project
    raw = next((p for e in ('mp3', 'wav', 'm4a', 'aac', 'flac') if (p := pdir / f'voiceover_raw.{e}').exists()), None)
    if not raw:
        raise SystemExit(f'Put the recording at {pdir}/voiceover_raw.mp3 (or .wav/.m4a)')
    script = json.loads((pdir / 'script.json').read_text())
    out = pdir / 'voiceover.wav'

    before, after = tighten(raw, out, args.gap, args.noise)
    words = script_words(script)
    starts, ends = align(out, words, script.get('spoken'), script.get('pronounce'))

    lines = []
    for li in range(len(script['lines'])):
        idx = [i for i, (l, _) in enumerate(words) if l == li]
        lines.append({
            'start': round(starts[idx[0]], 3),
            'end': round(ends[idx[-1]], 3),
            'words': [{'w': words[i][1], 's': round(starts[i], 3), 'e': round(ends[i], 3)} for i in idx],
        })
    duration = round(max(after, lines[-1]['end']) + args.tail, 3)
    (pdir / 'timing.json').write_text(json.dumps({'duration': duration, 'lines': lines}, indent=2) + '\n')

    for li, l in enumerate(lines):
        text = ' '.join(w for (i, w) in words if i == li)
        print(f'{li:2}  {l["start"]:6.2f}–{l["end"]:6.2f}  {text}')
    print(f'\nVoiceover {before:.1f}s -> {after:.1f}s after cutting pauses. Video length {duration:.1f}s.')
    print(f'Wrote {out.name} and timing.json.')


if __name__ == '__main__':
    main()
