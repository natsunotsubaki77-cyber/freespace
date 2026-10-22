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
EDGE = 3  # 境目からこのpx以内は 背景色の混ざりを取りのぞく
CROP_BOTTOM = {"h3": 0.135}  # 発射台など、大きさに入れない下の部分（割合）
KEEP_INSIDE = {"roomy"}  # 窓の中は穴をあけず、外とつながる背景だけ消す
FLIP = {"roomy"}  # 左むきに できた絵は 右むきに なおす
SPILL_ALL = {"freed", "roomy", "jumbo", "shinkansen", "shinkansen_mid", "skybus"}  # 窓ごしに背景が写る絵は 全体のにじみを消す


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

    # 外側からつながるマゼンタだけを背景にする（鉄骨などの細い線を消さないよう、すきま埋めはしない）
    cand = score > 0.5
    lab, _ = ndimage.label(cand)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, border[border > 0])
    # しっぽの輪の中など、とじこめられた背景色も消す
    if name not in KEEP_INSIDE:
        bg |= (dist < 20) | (m > 90)

    # 境目は「背景色がどれだけ混ざっているか」から透明度を出し、背景色を差し引いて色を戻す
    m_bg = max(60.0, float(np.median(np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]]))))
    mix = np.clip((m - 20) / (m_bg * 0.9 - 20), 0, 1)
    near = ndimage.binary_dilation(bg, iterations=EDGE) & ~bg
    alpha = np.where(bg, 0.0, np.where(near, 1 - mix, 1.0))
    a = np.maximum(alpha, 0.05)[..., None]
    out = np.where(near[..., None], (rgb - (1 - a) * bgc) / a, rgb)

    # 窓ごしに背景が写る絵は 全体のにじみも消す
    if name in SPILL_ALL:
        spill = np.clip(m, 0, None) * ~bg
        out[..., 0] -= spill * 0.9
        out[..., 2] -= spill * 0.9
    out = np.clip(out, 0, 255)

    rgba = np.dstack([out, alpha * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, "RGBA")
    box = Image.fromarray(((alpha > 0.25) * 255).astype(np.uint8)).getbbox()
    if box:
        im = im.crop(box)
    if name in CROP_BOTTOM:
        im = im.crop((0, 0, im.width, round(im.height * (1 - CROP_BOTTOM[name]))))
        im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 64 else 0).getbbox())
    if name in FLIP:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
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
