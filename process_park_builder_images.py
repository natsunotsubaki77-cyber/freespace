"""
公園づくりゲーム の遊具の絵（マゼンタ背景）を透過して webp にする。
切り抜きのしかたは おおきさくらべ と同じ。 raw/<name>.png -> images/<name>.webp
"""
import os
import sys
import process_size_images as p

BASE = os.path.join(os.path.dirname(__file__), "games", "park-builder")
p.RAW = os.path.join(BASE, "raw")
p.OUT = os.path.join(BASE, "images")

if __name__ == "__main__":
    names = sys.argv[1:] or sorted(f[:-4] for f in os.listdir(p.RAW) if f.endswith(".png"))
    for n in names:
        p.process(n)
