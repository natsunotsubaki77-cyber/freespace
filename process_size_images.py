"""
おおきさくらべ の生成画像（マゼンタ背景）を透過し、被写体ぴったりに切り抜いて webp で保存する。
raw/<name>.png -> images/<name>.webp
"""
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

BASE = os.path.join(os.path.dirname(__file__), "games", "size-compare")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(BASE, "images")
MAX_SIDE = 900
EDGE = 5  # 境目からこのpx以内は マゼンタのにじみを消す
SPILL_ALL = {"freed", "jumbo", "shinkansen", "skybus"}  # 窓ごしに背景が写る絵は 全体のにじみを消す


def process(name):
    rgb = np.asarray(Image.open(os.path.join(RAW, name + ".png")).convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # マゼンタらしさ: 赤と青がそろって緑より強い
    m = np.minimum(r, b) - g
    # ふちの色（実際の背景色）にどれだけ近いか
    edge_px = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bgc = np.median(edge_px, axis=0)
    dist = np.linalg.norm(rgb - bgc, axis=2)
    score = np.maximum(np.clip((m - 30) / 40, 0, 1), np.clip(1 - (dist - 30) / 50, 0, 1))

    # 外側からつながるマゼンタだけを背景にする
    cand = score > 0.5
    lab, _ = ndimage.label(cand)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    # しっぽの輪の中など、とじこめられた背景色も消す
    bg |= (dist < 20) | (m > 90)
    # 背景のすきまの小さな点も背景に
    bg = ndimage.binary_closing(bg, iterations=2) | bg

    near = ndimage.binary_dilation(bg, iterations=EDGE) & ~bg
    alpha = np.where(bg, 0.0, 1.0)
    alpha = np.where(near, 1 - score * 0.9, alpha)
    alpha = ndimage.gaussian_filter(alpha, 0.7)
    alpha[bg] = 0

    # にじみ消し（境目の近くだけ）
    spill = np.clip(m, 0, None) * (True if name in SPILL_ALL else near)
    out = rgb.copy()
    out[..., 0] -= spill * 0.9
    out[..., 2] -= spill * 0.9
    out = np.clip(out, 0, 255)

    rgba = np.dstack([out, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    box = Image.fromarray(((alpha > 0.25) * 255).astype(np.uint8)).getbbox()
    if box:
        im = im.crop(box)
    w, h = im.size
    k = MAX_SIDE / max(w, h)
    if k < 1:
        im = im.resize((round(w * k), round(h * k)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + ".webp"), "WEBP", quality=82, method=6)
    print(f"  {name}: {im.size}")


def main():
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(RAW) if f.endswith(".png"))
    for n in names:
        process(n)


if __name__ == "__main__":
    main()
