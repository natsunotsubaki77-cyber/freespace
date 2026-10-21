"""
くるまくらべ 用の車の画像（横・前）を一括生成するスクリプト
Gemini 画像生成 API を使用。背景はマゼンタ単色で作り、process_car_images.py で透過する。
使い方: python -u generate_car_images.py [id ...]   （id を省くと全車。できている絵はとばす）
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("環境変数 GEMINI_API_KEY を .env ファイルに設定してください")

BASE = os.path.join(os.path.dirname(__file__), "games", "car-compare")
OUTPUT_DIR = os.path.join(BASE, "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.1-flash-image-preview"

STYLE = (
    "Photorealistic studio photograph, high quality, soft even lighting. "
    "Orthographic-like view with no perspective distortion, as if shot with a long telephoto lens from far away. "
    "The ENTIRE car is fully visible, nothing cropped, centered with a small margin around it. "
    "No license plate text, no badges with readable text, no people. "
    "Background: one completely flat solid pure magenta color (#FF00FF) filling everything behind the car. "
    "No ground, no floor, no shadow, no reflection, no scenery, no text, no watermark."
)
VIEWS = {
    "side": "Seen exactly from the side (pure profile, 90 degrees), the FRONT of the car pointing to the LEFT of the image, wheels level.",
    "front": "Seen exactly from the front (straight head-on view, 0 degrees), symmetric, both side mirrors visible, NOT a three-quarter angle, the side panels of the car must not be visible.",
}
COLORS = ["pearl white", "silver metallic", "dark gray metallic", "black", "deep blue metallic",
          "red", "light beige", "dark green metallic", "white", "sky blue"]


def generate(car, view, color):
    path = os.path.join(OUTPUT_DIR, f"{car['id']}_{view}.png")
    if os.path.exists(path):
        return
    prompt = (f"Body color: {color}. A {color} {car['makerEn']} {car['en']} ({car['look']}), Japanese-market model. "
              f"{VIEWS[view]} {STYLE}")
    for attempt in range(2):
        try:
            res = client.models.generate_content(model=MODEL, contents=prompt)
            for part in res.candidates[0].content.parts:
                if part.inline_data:
                    with open(path, "wb") as f:
                        f.write(part.inline_data.data)
                    print("  ok", car["id"], view, flush=True)
                    return
            print("  no image", car["id"], view, flush=True)
        except Exception as e:
            print("  error", car["id"], view, e, flush=True)
            time.sleep(10 * (attempt + 1))


def main():
    with open(os.path.join(BASE, "cars.json"), encoding="utf-8") as f:
        cars = json.load(f)
    want = set(sys.argv[1:])
    jobs = []
    for i, car in enumerate(cars):
        if want and car["id"] not in want:
            continue
        color = car.get("color") or COLORS[i % len(COLORS)]
        for view in VIEWS:
            jobs.append((car, view, color))
    # 横と前で同じ色にする
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(lambda j: generate(*j), jobs))


if __name__ == "__main__":
    main()
