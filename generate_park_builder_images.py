"""
公園づくりゲーム 用のイラストを作るスクリプト
Gemini 画像生成 API を使用。1日5まいくらいずつ作る。
"""
import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("環境変数 GEMINI_API_KEY を .env ファイルに設定してください")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "games", "park-builder", "raw")  # 切り抜き前。process_park_builder_images.py で images/ へ
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.1-flash-image-preview"

STYLE = (
    "Hand-painted picture book illustration for a toddler game, soft watercolor and gouache textures, "
    "warm gentle colors, rounded friendly shapes, delicate details, cozy and charming. "
    "No text, no letters, no logos."
)
# 背景：遊具を置けるよう、まん中に広い空き地をのこす
PARK = (
    " Wide 16:9 landscape, seen from slightly above at a gentle angle so the ground is visible like a stage. "
    "The large center and lower half is an open flat empty lawn with nothing on it, ready for playground equipment to be placed later. "
    "No playground equipment, no people, no animals, no buildings, no benches."
)
# 遊具：あとで切り抜くので背景はマゼンタ。色を変えやすいよう、おもな部分は1色にする
ITEM = (
    " A single object only, seen from slightly above at a gentle three-quarter angle, matching a park background drawn the same way. "
    "The main painted parts are all one bright red color so the color can be changed later; metal parts are light gray. "
    "Background: one completely flat solid pure magenta color (#FF00FF) filling everything behind the object. "
    "No ground, no grass, no shadow, no scenery, no people."
)
# 遊ぶ子ども：遊具の上にかさねるので、子どもだけを描く
KID = (
    " Only the one child, full body, no playground equipment, no seat, no ropes, no chains, no ground, no shadow, no other objects."
    " Background: one completely flat solid pure magenta color (#FF00FF) filling everything behind the child. Do not use magenta or pink on the child."
)
SLIDE_KID = "A cute small child about four years old with short black hair in two little pigtails, a yellow T-shirt and blue shorts, white sneakers. "
SWING_KID = "A cute small boy about four years old with short brown hair, a light green T-shirt and navy shorts, white sneakers. "

images = {
    "bg_forest": "A park surrounded by a lush forest: rows of big round leafy trees of varied greens along the back and both sides, "
                 "a few small bushes and wildflowers at the edges, soft dappled sunlight, blue sky with a couple of fluffy clouds peeking above the trees." + PARK,
    "bg_hills": "A park among gentle rolling green hills: soft round grassy hills and little mounds along the back and both sides, "
                "a few scattered small trees and clover patches, a winding path over a hill, blue sky with fluffy clouds." + PARK,
    "bg_sea": "A park by the sea: a calm sparkling blue ocean and sandy beach visible along the back, a few palm-like and pine trees at the sides, "
              "a low white fence at the far edge of the lawn, a small sailboat far away, blue sky with fluffy clouds and a couple of seagulls far away." + PARK,
    # ホーム画面のアイコン。正方形いっぱいに描く
    "icon": "A square app icon for a toddler park-building game: a cozy little park on a round green lawn, a red slide, a small round tree, colorful tulips and a fluffy cloud in a light blue sky, "
            "the whole scene filling the square edge to edge, bold simple shapes that stay clear when very small, square 1:1 image.",
    "slide": "A cute playground slide: a short ladder on the left, a small platform with a little roof, and a smooth wide slide going down to the right. Nothing hangs from the roof: no chains, no ropes, no swings." + ITEM,
    "swing": "A cute playground swing set: a sturdy frame with two swings hanging on chains, with flat seats." + ITEM,
    "seesaw": "A cute playground seesaw: one long board balanced on a center pivot, with a small handle and a round seat at each end, tilted slightly." + ITEM,
    "jungle_gym": "A cute playground jungle gym (climbing frame): a cube-shaped grid of bars, three bars tall and three wide, with round red joints and some red bars, simple and tidy. Nothing hangs from the bars: no chains, no ropes, no swings." + ITEM,
    "sandbox": "A cute playground sandbox: a low square wooden-edged frame painted red, filled with smooth light beige sand, with a small bucket and a shovel on the sand." + ITEM,
    "spring_rider": "A cute playground spring rider shaped like a round friendly horse with handles and a seat, standing on a big coiled metal spring." + ITEM,
    "flowerbed": "A cute small park flower bed: a low rounded oval border of light gray stones, filled with dark brown soil, green leaves and many round red tulip-like flowers." + ITEM,
    "water_tap": "A cute park drinking fountain and water tap: a short round red pillar with a small light gray metal faucet on top and a little round basin, a tiny drop of water falling from the faucet." + ITEM,
    "bench": "A cute park bench: a seat and backrest made of red wooden slats, with simple light gray metal legs and armrests, facing slightly to the right." + ITEM,
    # すべり台：上でまつ → 手をあげてすべる（2まい目は1まい目と同じ子）
    "kid_slide_1": SLIDE_KID + "Sitting with both legs stretched straight out forward to the right, seen from the side at a gentle three-quarter angle facing right, "
                   "both hands resting on the ground beside the hips, excited smile, ready to go." + KID,
    "kid_slide_2": "The exact same child as in the reference picture, same face, hair and clothes, same size and angle. Still sitting with both legs stretched straight out forward to the right, "
                   "now leaning back a little with both arms raised high in the air, laughing happily." + KID,
    # ブランコ：足をぶらぶら → 足を前にけり出す
    "kid_swing_1": SWING_KID + "Seen from the front at a gentle three-quarter angle, sitting as if on a small seat, both arms raised to shoulder height with hands loosely closed as if holding two ropes, "
                   "knees bent and lower legs hanging straight down, big happy smile." + KID,
    "kid_swing_2": "The exact same boy as in the reference picture, same face, hair and clothes, same size and angle, hands in the same place as if holding two ropes. "
                   "Now leaning back a little and kicking both legs straight out forward toward the viewer, laughing." + KID,
}
# 2まい目は1まい目の絵を見せて、同じ子に描いてもらう
REFS = {"kid_slide_2": "kid_slide_1", "kid_swing_2": "kid_swing_1"}


def generate(name, prompt):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    if os.path.exists(path):
        print(f"  [SKIP] {name}")
        return True
    contents = [f"{STYLE}\n\nSubject: {prompt}"]
    if name in REFS:
        contents.insert(0, Image.open(os.path.join(OUTPUT_DIR, f"{REFS[name]}.png")))
    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=genai.types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
        )
        for part in res.candidates[0].content.parts:
            if part.inline_data is not None:
                with open(path, "wb") as f:
                    f.write(part.inline_data.data)
                print(f"  [OK] {name}")
                return True
        print(f"  [WARN] {name}: no image")
        return False
    except Exception as e:
        print(f"  [ERROR] {name}: {e}")
        return False


def main():
    names = sys.argv[1:] or list(images)
    for i, name in enumerate(names, 1):
        print(f"[{i}/{len(names)}] {name}")
        generate(name, images[name])
        time.sleep(3)


if __name__ == "__main__":
    main()
