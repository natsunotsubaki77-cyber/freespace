"""
くるまくらべ の生成画像（マゼンタ背景）を透過し、車ぴったりに切り抜いて webp で保存する。
raw/<id>_<view>.png -> images/<id>_<view>.webp
切り抜きは process_size_images.py と同じやり方。窓ごしの背景のにじみは全車で消す。
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = os.path.join(os.path.dirname(__file__), "games", "car-compare")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "images")
MAX_SIDE = 800
EDGE = 3


def process(name):
    rgb = np.asarray(Image.open(os.path.join(RAW, name + ".png")).convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = np.minimum(r, b) - g
    edge_px = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bgc = np.median(edge_px, axis=0)
    dist = np.linalg.norm(rgb - bgc, axis=2)
    score = np.maximum(np.clip((m - 30) / 40, 0, 1), np.clip(1 - (dist - 30) / 50, 0, 1))

    cand = score > 0.5
    lab, _ = ndimage.label(cand)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    bg |= (dist < 20) | (m > 90)

    m_bg = max(60.0, float(np.median(np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]]))))
    mix = np.clip((m - 20) / (m_bg * 0.9 - 20), 0, 1)
    near = ndimage.binary_dilation(bg, iterations=EDGE) & ~bg
    alpha = np.where(bg, 0.0, np.where(near, 1 - mix, 1.0))
    a = np.maximum(alpha, 0.05)[..., None]
    out = np.where(near[..., None], (rgb - (1 - a) * bgc) / a, rgb)

    spill = np.clip(m, 0, None) * ~bg
    out[..., 0] -= spill * 1.0
    out[..., 2] -= spill * 1.0
    out = np.clip(out, 0, 255)

    rgba = np.dstack([out, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    box = Image.fromarray(((alpha > 0.5) * 255).astype(np.uint8)).getbbox()
    if box:
        im = im.crop(box)
    im = cut_shadow(im)
    w, h = im.size
    k = MAX_SIDE / max(w, h)
    if k < 1:
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=80, method=6)
    return im.size


def cut_shadow(im):
    """タイヤの下に描かれた 地面のかげを切る。
    下のほうで「タイヤだけの細い行」のすぐ下に「横いっぱいの行」が出てきたら、そこから下はかげ。"""
    a = np.asarray(im.getchannel("A")) > 128
    w, h = im.size
    cov = a.sum(axis=1) / w
    for y in range(int(h * 0.85), h):
        if cov[y] > 0.5 and cov[max(0, y - 6)] < 0.45:
            return im.crop((0, 0, w, y)).crop(im.crop((0, 0, w, y)).getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox())
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(RAW) if f.endswith(".png"))
    for n in names:
        print(f"  {n}: {process(n)}")


if __name__ == "__main__":
    main()
