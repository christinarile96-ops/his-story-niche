#!/usr/bin/env python3
"""2.5D compositor: green-screen cutouts + environment plates -> 1080x1920 Short.

  python3 engine/render.py <project> [--fps 60] [--workers 4] [--stills 1.2,3.4] [--scale 0.5]

Reads projects/<project>/{timing.json,script.json,shots.py,voiceover.wav} and the
images in assets/<project>/ (cutouts in assets/<project>/cut/, made by key.py).
Each shot is a stack of layers placed in screen space; a per-shot camera zooms,
pans and shakes them, with less motion for layers further back (parallax).
"""
import argparse
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1080, 1920
YELLOW = (0, 184, 246)  # BGR of #F6B800
FONT = str(ROOT / 'engine/fonts/Montserrat-ExtraBold.ttf')


# ---------------------------------------------------------------- easing
def ease(u, kind='inout'):
    u = min(max(u, 0.0), 1.0)
    if kind == 'linear':
        return u
    if kind == 'out':
        return 1 - (1 - u) ** 3
    if kind == 'in':
        return u ** 3
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def val(v, u, kind='inout'):
    """A layer/camera value: a number, [a, b] eased over the shot, or [[u, v], ...] keys."""
    if isinstance(v, (int, float)):
        return v
    if len(v) == 2 and not isinstance(v[0], (list, tuple)):
        return v[0] + (v[1] - v[0]) * ease(u, kind)
    keys = v
    if u <= keys[0][0]:
        return keys[0][1]
    for (u0, a), (u1, b) in zip(keys, keys[1:]):
        if u <= u1:
            return a + (b - a) * ease((u - u0) / (u1 - u0), kind)
    return keys[-1][1]


# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self, adir):
        self.adir = Path(adir)
        self.cache = {}

    def get(self, name):
        if name not in self.cache:
            p = self.adir / f'{name}.png'
            img = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
            if img is None:
                raise SystemExit(f'missing asset {p}')
            if img.shape[2] == 3:
                img = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
            self.cache[name] = img
        return self.cache[name]

    def shadow(self, name):
        key = name + '#shadow'
        if key not in self.cache:
            a = self.get(name)[..., 3]
            ys, xs = np.where(a > 128)
            sh = np.zeros(a.shape, np.float32)
            if len(ys):
                foot = ys.max()
                cols = xs[ys > foot - 40]
                cx = int(cols.mean()) if len(cols) else int(xs.mean())
                rx = int((xs.max() - xs.min()) * 0.42)
                cv2.ellipse(sh, (cx, foot - 6), (max(rx, 20), max(rx // 7, 8)), 0, 0, 360, 1.0, -1)
                sh = cv2.GaussianBlur(sh, (0, 0), 18)
            img = np.zeros(a.shape + (4,), np.uint8)
            img[..., 3] = (sh * 150).astype(np.uint8)
            self.cache[key] = img
        return self.cache[key]


# ---------------------------------------------------------------- fx helpers
_vig = None
_fog = None
_grain = None


def vignette(strength):
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
        _vig = np.clip(d, 0, 1.4) ** 2.2
    return 1 - np.clip(_vig * strength, 0, 0.9)[..., None]


def fog_tex():
    global _fog
    if _fog is None:
        rng = np.random.default_rng(3)
        acc = np.zeros((H, W * 2), np.float32)
        for k, amp in [(6, 1.0), (14, 0.5), (32, 0.25)]:
            small = rng.random((k * 2, k * 2)).astype(np.float32)
            acc += cv2.resize(small, (W * 2, H), interpolation=cv2.INTER_CUBIC) * amp
        acc = (acc - acc.min()) / (acc.max() - acc.min())
        _fog = cv2.GaussianBlur(acc, (0, 0), 25)
    return _fog


def grain(i):
    global _grain
    if _grain is None:
        rng = np.random.default_rng(5)
        _grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
    return cv2.resize(_grain[i % 6], (W, H))[..., None]


def snow(frame, t, seed, amount, wind=40, night=False):
    rng = np.random.default_rng(seed)
    n = int(260 * amount)
    x0 = rng.random(n) * (W + 400) - 200
    y0 = rng.random(n) * H
    z = rng.random(n)  # 0 = far, 1 = near
    speed = 70 + 260 * z
    x = (x0 + wind * (0.4 + z) * t + 25 * np.sin(t * (0.6 + z) + x0)) % (W + 400) - 200
    y = (y0 + speed * t) % (H + 40) - 20
    r = 1.2 + 5.5 * z ** 2
    over = np.zeros((H, W), np.float32)
    for xi, yi, ri, zi in zip(x, y, r, z):
        cv2.circle(over, (int(xi), int(yi)), max(1, int(ri)), 0.5 + 0.5 * zi, -1, cv2.LINE_AA)
    over = cv2.GaussianBlur(over, (0, 0), 1.6)
    col = np.array([0.95, 0.92, 0.88] if night else [1, 1, 1], np.float32)
    a = np.clip(over, 0, 1)[..., None] * (0.75 if night else 0.9)
    return frame * (1 - a) + col * a


def glow(frame, cx, cy, radius, power, color=(0.85, 0.95, 1.0)):
    y, x = np.ogrid[0:H, 0:W]
    d2 = ((x - cx) ** 2 + (y - cy) ** 2) / float(radius ** 2)
    g = (np.exp(-d2 * 2.2) * power).astype(np.float32)[..., None]
    return frame + g * np.array(color, np.float32)


def bloom(frame, thresh=0.82, amount=0.35):
    small = cv2.resize(frame, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(small - thresh, 0, None)
    hi = cv2.GaussianBlur(hi, (0, 0), 9)
    return frame + cv2.resize(hi, (W, H)) * amount


def note_icon(frame, cx, cy, size, alpha):
    """A yellow eighth note with a soft glow (the whistle motif)."""
    if alpha <= 0.01:
        return frame
    over = np.zeros((H, W), np.float32)
    s = size
    cv2.ellipse(over, (int(cx), int(cy)), (int(s * 0.34), int(s * 0.25)), -25, 0, 360, 1, -1, cv2.LINE_AA)
    sx = int(cx + s * 0.29)
    cv2.line(over, (sx, int(cy)), (sx, int(cy - s * 1.25)), 1, max(2, int(s * 0.1)), cv2.LINE_AA)
    pts = np.array([[sx, cy - s * 1.25], [sx + s * 0.45, cy - s * 0.85], [sx + s * 0.42, cy - s * 0.6],
                    [sx, cy - s * 0.95]], np.int32)
    cv2.fillPoly(over, [pts], 1, cv2.LINE_AA)
    halo = cv2.GaussianBlur(over, (0, 0), s * 0.35) * 0.8
    col = np.array([0, 184, 246], np.float32) / 255
    a = np.clip(over + halo, 0, 1)[..., None] * alpha
    return frame * (1 - a) + col * a


# ---------------------------------------------------------------- text
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


def text_img(parts, size, stroke):
    """parts: [(text, is_key)] -> RGBA numpy (premultiplied later)."""
    f = font(size)
    space = f.getlength(' ')
    widths = [f.getlength(t) for t, _ in parts]
    tw = int(sum(widths) + space * (len(parts) - 1)) + stroke * 4
    asc, desc = f.getmetrics()
    th = asc + desc + stroke * 4
    img = Image.new('RGBA', (tw + 30, th + 30), (0, 0, 0, 0))
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shadow)
    x = stroke * 2 + 15
    for (t, key), w in zip(parts, widths):
        fill = (246, 184, 0, 255) if key else (255, 255, 255, 255)
        ds.text((x + 4, 15 + stroke * 2 + 7), t, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        d.text((x, 15 + stroke * 2), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
        x += w + space
    from PIL import ImageFilter
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    out = Image.alpha_composite(shadow, img)
    return np.array(out)


def caption_cards(timing):
    """Group words into 1–3 word cards, breaking at punctuation and keeping them short."""
    words = [w for line in timing['lines'] for w in line['words']]
    cards, cur = [], []

    def flush():
        if cur:
            cards.append(list(cur))
            cur.clear()

    for i, w in enumerate(words):
        cur.append(w)
        txt = ' '.join(x['w'].replace('*', '') for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        end_punct = re.search(r'[.,!?;:"]$', w['w'].replace('*', ''))
        if len(cur) >= 3 or len(txt) >= 13 or end_punct or nxt is None:
            flush()
        elif nxt and len(txt + ' ' + nxt['w']) > 16:
            flush()
    out = []
    for k, c in enumerate(cards):
        parts = [(x['w'].replace('*', ''), x['w'].count('*') >= 2) for x in c]
        start = c[0]['s']
        end = cards[k + 1][0]['s'] if k + 1 < len(cards) else c[-1]['e'] + 0.5
        out.append({'start': start, 'end': end, 'parts': parts})
    return out


class Captions:
    def __init__(self, timing, y=0.70):
        self.cards = caption_cards(timing)
        self.y = int(H * y)
        self.cache = {}

    def img(self, k):
        if k not in self.cache:
            c = self.cards[k]
            size = 104
            while True:
                im = text_img(c['parts'], size, 7)
                if im.shape[1] <= W - 90 or size <= 60:
                    break
                size -= 6
            self.cache[k] = im.astype(np.float32) / 255
        return self.cache[k]

    def draw(self, frame, t):
        for k, c in enumerate(self.cards):
            if c['start'] <= t < c['end']:
                im = self.img(k)
                age = t - c['start']
                u = min(age / 0.08, 1)
                sc = 0.85 + 0.15 * ease(u, 'out') + 0.03 * math.sin(min(age / 0.16, 1) * math.pi)
                hh, ww = im.shape[:2]
                im2 = cv2.resize(im, (max(1, int(ww * sc)), max(1, int(hh * sc))), interpolation=cv2.INTER_LINEAR)
                return paste(frame, im2, W // 2, self.y, min(1, age / 0.05))
        return frame


def paste(frame, rgba, cx, cy, alpha=1.0):
    hh, ww = rgba.shape[:2]
    x0, y0 = int(cx - ww / 2), int(cy - hh / 2)
    x1, y1 = x0 + ww, y0 + hh
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if fx1 <= fx0 or fy1 <= fy0:
        return frame
    src = rgba[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = src[..., 3:4] * alpha
    rgb = src[..., 2::-1]  # RGBA -> BGR
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + rgb * a
    return frame


def label(text, size, color=(255, 255, 255)):
    f = font(size)
    tw = int(f.getlength(text)) + 40
    asc, desc = f.getmetrics()
    img = Image.new('RGBA', (tw, asc + desc + 30), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((20, 10), text, font=f, fill=color + (255,), stroke_width=6, stroke_fill=(0, 0, 0, 255))
    return np.array(img).astype(np.float32) / 255


# ---------------------------------------------------------------- shot render
def layer_matrix(img_w, img_h, x, y, s, cam, depth, flip=False):
    k = s * W / img_w
    zf = 1 + (cam['z'] - 1) * depth
    cx, cy = cam['cx'], cam['cy']
    # image -> layer screen space
    a = k * (-1 if flip else 1)
    tx = x - a * img_w / 2
    ty = y - k * img_h / 2
    # camera zoom about (cx, cy), then pan and shake scaled by depth
    rot = math.radians(cam['rot'] * depth)
    c, sn = math.cos(rot) * zf, math.sin(rot) * zf
    M = np.array([[c * a, -sn * k, 0], [sn * a, c * k, 0]], np.float64)
    # translation: R*(p - centre) + centre + pan
    px, py = tx - cx, ty - cy
    M[0, 2] = c * px - sn * py + cx + cam['px'] * depth
    M[1, 2] = sn * px + c * py + cy + cam['py'] * depth
    return M


def grade(img, g, u=0.0):
    if not g:
        return img
    out = img
    if 'exp' in g:
        out = out * val(g['exp'], u)
    if 'sat' in g:
        lum = out @ np.array([0.114, 0.587, 0.299], np.float32)
        out = lum[..., None] + (out - lum[..., None]) * val(g['sat'], u)
    if 'tint' in g:
        out = out * np.array(g['tint'], np.float32)
    if 'lift' in g:
        out = out + np.array(g['lift'], np.float32)
    return out


def render_shot(shot, t, assets, idx_frame):
    u = (t - shot['t0']) / max(1e-6, shot['t1'] - shot['t0'])
    lt = t - shot['t0']
    cam_def = shot.get('cam', {})
    ek = cam_def.get('ease', 'inout')
    cam = {
        'z': val(cam_def.get('z', 1.0), u, ek),
        'px': val(cam_def.get('x', 0), u, ek),
        'py': val(cam_def.get('y', 0), u, ek),
        'rot': val(cam_def.get('rot', 0), u, ek),
        'cx': W / 2 + cam_def.get('fx', 0),
        'cy': H / 2 + cam_def.get('fy', 0),
    }
    sh = cam_def.get('shake', 0)
    if sh:
        amp = val(sh, u) if not isinstance(sh, (int, float)) else sh
        cam['px'] += amp * (math.sin(t * 23.1) + 0.6 * math.sin(t * 41.7 + 1.3))
        cam['py'] += amp * (math.sin(t * 19.3 + 0.7) + 0.6 * math.sin(t * 37.9))
    hand = cam_def.get('hand', 3)  # gentle handheld drift on everything
    cam['px'] += hand * math.sin(t * 0.9 + shot['t0'])
    cam['py'] += hand * 0.8 * math.sin(t * 0.7 + 2 + shot['t0'])

    frame = np.zeros((H, W, 3), np.float32)
    frame[:] = shot.get('clear', (0, 0, 0))
    for L in shot['layers']:
        img = assets.get(L['img'])
        ih, iw = img.shape[:2]
        x = val(L.get('x', W / 2), u, L.get('ease', ek))
        y = val(L.get('y', H / 2), u, L.get('ease', ek))
        s = val(L.get('s', 1.08), u, L.get('ease', ek))
        if L.get('bob'):
            y += L['bob'] * math.sin(lt * 2.2 + x)
            s *= 1 + 0.004 * math.sin(lt * 1.6)
        depth = L.get('depth', 1.0)
        M = layer_matrix(iw, ih, x, y, s, cam, depth, L.get('flip', False))
        op = val(L.get('op', 1.0), u)
        if op <= 0.003:
            continue
        if L.get('shadow'):
            shw = cv2.warpAffine(assets.shadow(L['img']), M, (W, H), flags=cv2.INTER_LINEAR)
            a = shw[..., 3:4].astype(np.float32) / 255 * op * L.get('shadow_op', 1)
            frame *= (1 - a)
        warped = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        rgb = warped[..., :3].astype(np.float32) / 255
        a = warped[..., 3:4].astype(np.float32) / 255 * op
        blur = L.get('blur', 0)
        if blur:
            b = val(blur, u)
            if b > 0.3:
                rgb = cv2.GaussianBlur(rgb, (0, 0), b)
                a = cv2.GaussianBlur(a, (0, 0), b)[..., None] if a.ndim == 3 else a
                if a.ndim == 2:
                    a = a[..., None]
        rgb = grade(rgb, L.get('grade'), u)
        frame = frame * (1 - a) + rgb * a

    fx = shot.get('fx', {})
    if 'fog' in fx:
        f = fog_tex()
        off = int((t * 30) % W)
        fl = f[:, off:off + W][..., None]
        amt = val(fx['fog'], u)
        col = np.array(fx.get('fog_col', (0.86, 0.88, 0.9)), np.float32)
        a = np.clip(amt * (0.55 + 0.6 * fl), 0, 1)
        frame = frame * (1 - a) + col * a
    if 'snow' in fx:
        frame = snow(frame, t, hash(shot['id']) % 1000, val(fx['snow'], u), fx.get('wind', 40), fx.get('night', False))
    if 'glow' in fx:
        gx, gy, gr, gp = fx['glow']
        frame = glow(frame, val(gx, u), val(gy, u), val(gr, u), val(gp, u))
    if 'notes' in fx:
        for (nt, nx, ny, size) in fx['notes']:
            age = t - nt
            if 0 <= age < 1.4:
                al = min(1, age / 0.12) * (1 - max(0, age - 0.9) / 0.5)
                frame = note_icon(frame, nx + 30 * math.sin(age * 3), ny - age * 120, size * (0.8 + 0.2 * ease(age / 0.2, 'out')), al)
    if 'counter' in fx:
        c0, c1, ct0, ct1, cx, cy = fx['counter']
        k = ease((t - ct0) / (ct1 - ct0), 'inout')
        hours = c0 + (c1 - c0) * k
        frame = paste(frame, label(f'HOUR {max(1, int(round(hours)))}', 120, (246, 184, 0)), cx, cy, min(1, max(0, (t - ct0) / 0.15)))
    if fx.get('bloom'):
        frame = bloom(frame, amount=fx['bloom'])
    frame = grade(frame, shot.get('grade'), u)
    if 'flash' in fx:
        for ft, fd in fx['flash']:
            if ft - 0.04 <= t < ft + fd:
                a = 1 - max(0, t - ft) / fd if t >= ft else (t - ft + 0.04) / 0.04
                frame = frame * (1 - a) + a
    if 'dark' in fx:
        frame = frame * (1 - val(fx['dark'], u))
    v = shot.get('vignette', 0.55)
    if v:
        frame = frame * vignette(v)
    return frame


def render_frame(shots, t, assets, caps, i):
    cur = next((s for s in shots if s['t0'] <= t < s['t1']), shots[-1])
    frame = render_shot(cur, t, assets, i)
    tr = cur.get('in')
    k = shots.index(cur)
    if tr and k > 0:
        prev = shots[k - 1]
        dur = {'fade': 0.35, 'whip': 0.2, 'flash': 0.25, 'dip': 0.5}.get(tr, 0)
        lt = t - cur['t0']
        if tr == 'fade' and lt < dur:
            a = ease(lt / dur)
            frame = render_shot(prev, t, assets, i) * (1 - a) + frame * a
        elif tr == 'whip' and lt < dur:
            a = ease(lt / dur)
            other = render_shot(prev, t, assets, i)
            shift = int(W * a)
            mix = np.zeros_like(frame)
            mix[:, :W - shift] = other[:, shift:]
            mix[:, W - shift:] = frame[:, :shift]
            kern = np.zeros((1, 61), np.float32)
            kern[0, :] = 1 / 61
            frame = cv2.filter2D(mix, -1, kern) if 0.1 < a < 0.9 else mix
        elif tr == 'dip' and lt < dur:
            frame = frame * ease(lt / dur)
    # dip/flash out of the previous shot's tail
    nxt = shots[k + 1] if k + 1 < len(shots) else None
    if nxt and nxt.get('in') == 'dip' and cur['t1'] - t < 0.25:
        frame = frame * ease((cur['t1'] - t) / 0.25)
    if nxt and nxt.get('in') == 'flash' and cur['t1'] - t < 0.12:
        a = 1 - (cur['t1'] - t) / 0.12
        frame = frame * (1 - a) + a
    if tr == 'flash' and t - cur['t0'] < 0.25:
        a = 1 - (t - cur['t0']) / 0.25
        frame = frame * (1 - a) + a
    frame = frame + grain(i) * 0.012
    frame = caps.draw(frame, t)
    return np.clip(frame * 255, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- project loading
def load(project):
    pdir = ROOT / 'projects' / project
    timing = json.loads((pdir / 'timing.json').read_text())
    spec = importlib.util.spec_from_file_location('shots', pdir / 'shots.py')
    mod = importlib.util.module_from_spec(spec)
    mod.TIMING = timing
    sys.modules['shots'] = mod
    spec.loader.exec_module(mod)
    shots = mod.build(timing)
    for i, s in enumerate(shots):
        s.setdefault('id', f's{i}')
        if i + 1 < len(shots):
            s['t1'] = shots[i + 1]['t0']
    shots[-1]['t1'] = mod.DURATION
    return pdir, timing, shots, mod


_ctx = {}


def _init(project):
    pdir, timing, shots, mod = load(project)
    _ctx.update(shots=shots, assets=Assets(ROOT / 'assets' / project), caps=Captions(timing))


def _chunk(args):
    project, a, b, fps, out = args
    sh, assets, caps = _ctx['shots'], _ctx['assets'], _ctx['caps']
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                            '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '15',
                            '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(render_frame(sh, i / fps, assets, caps, i).tobytes())
    enc.stdin.close()
    enc.wait()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--fps', type=int, default=60)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--stills', default='')
    ap.add_argument('--scale', type=float, default=0.4)
    ap.add_argument('--out', default='')
    args = ap.parse_args()
    pdir, timing, shots, mod = load(args.project)
    if args.stills:
        _init(args.project)
        sdir = pdir / 'stills'
        sdir.mkdir(exist_ok=True)
        for s in args.stills.split(','):
            t = float(s)
            fr = render_frame(_ctx['shots'], t, _ctx['assets'], _ctx['caps'], int(t * 60))
            fr = cv2.resize(fr, (int(W * args.scale), int(H * args.scale)), interpolation=cv2.INTER_AREA)
            cv2.putText(fr, f'{t:.2f}', (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imwrite(str(sdir / f'{t:07.2f}.png'), fr)
        print('stills ->', sdir)
        return
    n = int(round(mod.DURATION * args.fps))
    tmp = pdir / 'tmp'
    tmp.mkdir(exist_ok=True)
    k = args.workers * 3
    bounds = [round(n * j / k) for j in range(k + 1)]
    jobs = [(args.project, bounds[j], bounds[j + 1], args.fps, str(tmp / f'part{j:02}.mp4')) for j in range(k)]
    with Pool(args.workers, initializer=_init, initargs=(args.project,)) as pool:
        for done in pool.imap_unordered(_chunk, jobs):
            print('done', Path(done).name, flush=True)
    (tmp / 'list.txt').write_text(''.join(f"file '{Path(j[4]).name}'\n" for j in jobs))
    silent = tmp / 'video.mp4'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(tmp / 'list.txt'),
                    '-c', 'copy', str(silent)], check=True)
    # audio
    subprocess.run([sys.executable, str(ROOT / 'engine/sound.py'), args.project], check=True)
    out = args.out or str(pdir / 'render.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(silent), '-i', str(pdir / 'mix.wav'), '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out)


if __name__ == '__main__':
    main()
