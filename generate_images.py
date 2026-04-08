"""
おかいものゲーム用イラスト一括生成スクリプト
Gemini Nanobanana API を使用
"""
import os
import base64
import json
import time
from google import genai

API_KEY = "AIzaSyDTfUP2Uug3s2T5HiN-6pDdeyDPikcOgKs"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.1-flash-image-preview"

# 共通スタイル指示
STYLE = (
    "Cute kawaii illustration style for a children's shopping game app. "
    "Flat design with soft pastel colors, rounded shapes, thick outlines, "
    "simple and adorable. White or transparent background. "
    "Studio Ghibli meets modern app icon style. High quality, 512x512px."
)

# 生成する画像リスト
images_to_generate = {
    # キャラクター
    "shopkeeper": "A friendly cute kawaii shopkeeper character, wearing an apron and chef hat, smiling warmly, waving hand. Full body, chibi proportions.",

    # 背景
    "bg_title": "A cute kawaii shop storefront exterior, warm colors, wooden sign, bunting flags, flowers. Wide landscape format, cozy atmosphere.",
    "bg_shop": "Inside of a cute kawaii shop with wooden shelves, warm lighting, cozy atmosphere. Wide landscape format.",

    # おかしコーナー (Sweets)
    "chocolate": "A cute kawaii chocolate bar with a happy face, wrapped in colorful foil",
    "cookie": "A cute kawaii round cookie with chocolate chips and a happy face",
    "candy": "A cute kawaii wrapped candy/bonbon with a happy face, colorful wrapper",
    "cake": "A cute kawaii slice of strawberry shortcake with a happy face",
    "donut": "A cute kawaii donut with pink frosting and sprinkles, happy face",
    "icecream": "A cute kawaii ice cream cone with two scoops, happy face, pastel colors",
    "birthday_cake": "A cute kawaii birthday cake with candles and strawberries, happy face",
    "lollipop": "A cute kawaii swirl lollipop, rainbow colors, happy face",
    "melon_pan": "A cute kawaii melon bread/melon pan with grid pattern, happy face",

    # フルーツコーナー (Fruits)
    "apple": "A cute kawaii red apple with a happy face, small leaf on top",
    "banana": "A cute kawaii banana with a happy face, slightly curved",
    "orange": "A cute kawaii mandarin orange/mikan with a happy face, small leaf",
    "grape": "A cute kawaii bunch of purple grapes with a happy face",
    "strawberry": "A cute kawaii strawberry with a happy face, green leaves on top",
    "peach": "A cute kawaii peach with a happy face, soft pink color, small leaf",
    "melon": "A cute kawaii whole melon with net pattern and a happy face",
    "kiwi": "A cute kawaii kiwi fruit cut in half showing green inside, happy face",
    "pineapple": "A cute kawaii pineapple with a happy face, green crown leaves",

    # パンやさん (Bakery)
    "croissant": "A cute kawaii golden croissant with a happy face, flaky layers",
    "french_bread": "A cute kawaii French baguette with a happy face, golden brown",
    "bread": "A cute kawaii loaf of white bread/shokupan with a happy face",
    "bagel": "A cute kawaii bagel with a happy face, golden brown",
    "cupcake": "A cute kawaii cupcake with pink frosting and a cherry on top, happy face",
    "pretzel": "A cute kawaii pretzel with a happy face, golden brown, salt crystals",
    "onigiri": "A cute kawaii onigiri/rice ball with nori seaweed and a happy face",
    "sandwich": "A cute kawaii sandwich with lettuce and tomato visible, happy face",
    "apple_pie": "A cute kawaii apple pie with lattice crust, happy face, golden brown",

    # UI要素
    "coin_1": "A cute kawaii bronze coin showing number 1, shiny metallic",
    "coin_5": "A cute kawaii bronze coin with a hole in center showing number 5, shiny",
    "coin_10": "A cute kawaii bronze coin showing number 10, shiny metallic",
    "coin_50": "A cute kawaii silver coin with a hole showing number 50, shiny",
    "coin_100": "A cute kawaii silver coin showing number 100, shiny metallic",
    "coin_500": "A cute kawaii gold coin showing number 500, shiny metallic",
    "bill_1000": "A cute kawaii 1000 yen banknote, simplified design, green tint",
    "basket": "A cute kawaii shopping basket, woven pattern, warm brown color",
    "scanner": "A cute kawaii barcode scanner device, modern and friendly looking",
    "register": "A cute kawaii cash register, retro style with buttons, happy face",
    "wallet": "A cute kawaii brown leather wallet, slightly open showing coins",

    # スター・バッジ
    "star_empty": "A cute kawaii empty/gray star outline, simple",
    "star_filled": "A cute kawaii golden star, shiny and sparkling, happy face",
    "badge_first": "A cute kawaii achievement badge with a shopping bag icon, text 'はじめて', golden",
    "badge_perfect": "A cute kawaii achievement badge with a bullseye icon, text 'ぴったり', rainbow",
}

def generate_image(name, prompt):
    """1枚の画像を生成して保存"""
    filepath = os.path.join(OUTPUT_DIR, f"{name}.png")
    if os.path.exists(filepath):
        print(f"  [SKIP] {name}.png already exists")
        return True

    full_prompt = f"{STYLE}\n\nSubject: {prompt}"

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                with open(filepath, "wb") as f:
                    f.write(image_data)
                print(f"  [OK] {name}.png saved ({len(image_data)} bytes)")
                return True

        print(f"  [WARN] {name}: No image in response")
        # テキストレスポンスがあれば表示
        for part in response.candidates[0].content.parts:
            if part.text:
                print(f"         Response: {part.text[:100]}")
        return False

    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def main():
    total = len(images_to_generate)
    success = 0
    fail = 0

    print(f"=== おかいものゲーム イラスト生成 ===")
    print(f"生成対象: {total}枚")
    print(f"出力先: {OUTPUT_DIR}")
    print(f"モデル: {MODEL}")
    print()

    for i, (name, prompt) in enumerate(images_to_generate.items(), 1):
        print(f"[{i}/{total}] {name}...")
        ok = generate_image(name, prompt)
        if ok:
            success += 1
        else:
            fail += 1

        # レート制限対策（十分な間隔を空ける）
        if i < total:
            time.sleep(5)

    print()
    print(f"=== 完了 ===")
    print(f"成功: {success} / 失敗: {fail} / 合計: {total}")

    # 生成した画像のBase64 JSONも作成（HTML埋め込み用）
    print()
    print("Base64 JSON を生成中...")
    b64_data = {}
    for name in images_to_generate:
        filepath = os.path.join(OUTPUT_DIR, f"{name}.png")
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                b64_data[name] = base64.b64encode(f.read()).decode("utf-8")

    json_path = os.path.join(OUTPUT_DIR, "images_b64.json")
    with open(json_path, "w") as f:
        json.dump(b64_data, f)
    print(f"保存: {json_path} ({len(b64_data)}枚)")


if __name__ == "__main__":
    main()
