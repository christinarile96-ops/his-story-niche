"""Chroma-key the green-screen character renders into RGBA cutouts.

usage: python3 engine/key.py assets/01-grandpas-whistle  -> writes <dir>/cut/<name>.png
"""
import sys, glob, os
import numpy as np, cv2

def key(img):
    f = img.astype(np.float32) / 255.0
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    # sample the backdrop colour from the image border
    border = np.concatenate([f[:8].reshape(-1, 3), f[-8:].reshape(-1, 3), f[:, :8].reshape(-1, 3), f[:, -8:].reshape(-1, 3)])
    bg = np.median(border[border[:, 1] > border[:, [0, 2]].max(1) + 0.15], axis=0)
    # "greenness": how much G exceeds the stronger of R/B, relative to the backdrop's
    spill = g - np.maximum(r, b)
    ref = bg[1] - max(bg[0], bg[2])
    a = 1.0 - np.clip((spill - 0.08) / (ref * 0.55 - 0.08), 0, 1)
    a = cv2.GaussianBlur(a, (3, 3), 0)
    # kill specks: keep the largest connected blobs
    m = (a > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        keep = np.zeros(n, bool); big = st[1:, cv2.CC_STAT_AREA].max()
        keep[1:] = st[1:, cv2.CC_STAT_AREA] > big * 0.02
        solid = keep[lab]
        a = np.where(solid | (a < 0.5), a, 0)
        grow = cv2.dilate(solid.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
        a = np.where(grow, a, 0)
    # despill: clamp green to the max of red/blue
    g2 = np.minimum(g, np.maximum(r, b) * 1.02)
    out = np.dstack([b, g2, r, a])
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)

if __name__ == "__main__":
    d = sys.argv[1]; os.makedirs(f"{d}/cut", exist_ok=True)
    pre = ("gj_", "gjw_", "m6_", "m15_", "m17_", "friends_laugh")
    for p in sorted(glob.glob(f"{d}/*.png")):
        n = os.path.basename(p)
        if not n.startswith(pre): continue
        out = key(cv2.imread(p))
        ys, xs = np.where(out[..., 3] > 8)
        cv2.imwrite(f"{d}/cut/{n}", out)
        print(n, "bbox", xs.min(), ys.min(), xs.max(), ys.max())
