"""
公園づくりゲーム の遊具の絵（マゼンタ背景）を透過して webp にする。
切り抜きのしかたは おおきさくらべ と同じ。 raw/<name>.png -> images/<name>.webp
"""
import os
import sys
import numpy as np
from PIL import Image
import process_size_images as p

BASE = os.path.join(os.path.dirname(__file__), "games", "park-builder")
p.RAW = os.path.join(BASE, "raw")
p.OUT = os.path.join(BASE, "images")


def paint_layer(name):
    """赤くぬった所だけを取り出した かげの絵 images/<name>_paint.webp を作る。
    ゲームの中で柄や色をこれにかけて、もとの絵の上にかさねる。"""
    src = os.path.join(p.OUT, f"{name}.webp")
    a = np.array(Image.open(src).convert("RGBA")).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    ch = r - np.minimum(g, b)
    red = (r >= 100) & (r >= g) & (r >= b) & (ch >= 50) & (np.abs(g - b) * 3 <= ch)  # 光ったピンクもふくむ
    shade = np.minimum(1, r / 225 + np.maximum(0, g - 80) / 425) * 255
    out = np.zeros_like(a)
    out[..., 0] = out[..., 1] = out[..., 2] = shade
    out[..., 3] = np.where(red, a[..., 3], 0)
    Image.fromarray(out.astype("uint8")).save(os.path.join(p.OUT, f"{name}_paint.webp"), lossless=True)
    print(f"  {name}_paint")


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(p.RAW) if f.endswith(".png"))
    for n in names:
        p.process(n)
        if not n.startswith(("bg_", "kid_")):  # 子どもは色をかえない
            paint_layer(n)
