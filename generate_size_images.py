"""
おおきさくらべ 用のリアルな画像を一括生成するスクリプト
Gemini 画像生成 API を使用。背景はマゼンタ単色で作り、process_size_images.py で透過する。
"""
import os
import sys
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("環境変数 GEMINI_API_KEY を .env ファイルに設定してください")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "games", "size-compare", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.1-flash-image-preview"

STYLE = (
    "Photorealistic, high quality, natural lighting, like a professional photograph. "
    "The ENTIRE subject is fully visible from top to bottom and left to right, nothing cropped, "
    "centered with a small margin around it. "
    "Background: one completely flat solid pure magenta color (#FF00FF) filling everything behind the subject. "
    "No ground, no floor, no shadow, no scenery, no other objects, no text, no watermark."
)
FLAT = " Viewed from very far away at the height of its middle, straight-on flat front elevation, no perspective distortion, not looking up from below."
SIDE = " Seen exactly from the side (profile view), facing right."

images = {
    "hamster": "A golden Syrian hamster standing on all fours." + SIDE,
    "cat": "A gray tabby cat sitting upright, facing the viewer, tail curled beside it.",
    "rabbit": "A white Japanese rabbit sitting upright with long ears standing straight up." + SIDE,
    "shiba": "A red Shiba Inu dog standing on all four legs, curled tail." + SIDE,
    "penguin": "An adult emperor penguin (Aptenodytes forsteri, NOT a king penguin) standing upright, body turned slightly, full body, standing directly on nothing (no rock, no ice).",
    "kid": "A cheerful Japanese elementary school child standing straight, arms relaxed at the sides, facing the viewer, full body from head to shoes, wearing a t-shirt, shorts and sneakers.",
    "adult": "A Japanese adult man standing straight, arms relaxed at the sides, facing the viewer, full body from head to shoes, navy casual jacket, white shirt and gray trousers. Soft even studio lighting on the face, no harsh shadows.",
    "mirai": "Chubu Electric Power MIRAI TOWER (former Nagoya TV Tower) in Nagoya, the steel lattice tower with its four legs, observation decks and antenna, seen from the front, complete tower from base to top.",
    "skybus": "The red open-top double-decker sightseeing bus SKY BUS TOKYO, with the upper deck open air, no text on the body." + SIDE,
    "h3": "The JAXA H3 rocket standing upright on its launch pad base, white body with orange-brown first stage insulation, two solid rocket boosters, seen from the side, complete rocket from bottom to nose tip, no launch tower, no text.",
    "ferris": "The Diamond and Flower Ferris Wheel at Kasai Rinkai Park in Tokyo, a giant white ferris wheel with colorful gondolas and its support legs, seen from the front, complete wheel including the base." + FLAT,
    "vending": "A typical Japanese drink vending machine with rows of colorful drink bottles behind glass, seen from the front.",
    "bear": "A large brown bear (Ussuri brown bear) standing up on its hind legs, facing the viewer, full body.",
    "elephant": "An African elephant with tusks standing on all four legs." + SIDE,
    "freed": "A white Honda Freed compact minivan (third generation, 2024 model), no license plate text." + SIDE,
    "roomy": "A red Toyota Roomy compact tall-wagon (2020 facelift model) with sliding rear doors, no license plate text." + SIDE,
    "giraffe": "A giraffe standing with its long neck straight up, full body including legs." + SIDE,
    "trex": "A realistic Tyrannosaurus rex dinosaur walking, full body from head to tip of tail, horizontal posture." + SIDE,
    "nara_daibutsu": "The Great Buddha of Todai-ji in Nara, a huge bronze seated Buddha statue on a lotus pedestal with a golden halo behind it, seen from the front, full statue.",
    "torii": "The Great Torii gate of Itsukushima Shrine (Miyajima), large vermilion red wooden torii with its supporting side pillars, seen from the front, complete gate including the bottom of the pillars.",
    "whale": "A blue whale swimming, full body from head to tail flukes." + SIDE,
    "shinkansen": "The lead car of a JR Central N700A Shinkansen bullet train (Tokaido Shinkansen), white with a blue stripe, long aerodouble-wing nose, one single car only including bogies and wheels, no rails, no track." + SIDE,
    "shinkansen_mid": "One single intermediate passenger car of a JR Central N700A Shinkansen bullet train (Tokaido Shinkansen), white with a blue stripe below the windows, a long straight box-shaped car with flat vertical ends on both left and right (no nose), a row of small passenger windows, including bogies and wheels, no pantograph, no rails, no track." + SIDE,
    "himeji": "Himeji Castle in Japan, the white main keep tower on its stone wall base, seen from the front, complete building.",
    "toji": "The five-story pagoda of Toji temple in Kyoto, dark wooden pagoda with its tall spire, seen from the front, complete building.",
    "jumbo": "A Boeing 787-9 Dreamliner airliner parked with landing gear down, plain white livery with no airline logo or text, raked wingtips, chevron engine nacelles." + SIDE,
    "ushiku": "The Ushiku Daibutsu, a giant standing bronze Buddha statue in Japan, on its pedestal, seen from the front, full statue from pedestal to head.",
    "harukas": "Abeno Harukas skyscraper in Osaka, tall glass tower with setbacks on one side, seen from the front, complete building from base to top.",
    "tokyotower": "Tokyo Tower, the red and white lattice steel tower, seen from the front, complete tower from the four legs to the antenna.",
    "skytree": "Tokyo Skytree, the tall slender white-blue tower with two observation decks, seen from the front, complete tower from base to antenna tip, very tall and thin.",
    "pyramid": "The Great Pyramid of Giza (Pyramid of Khufu) in Egypt, sandy limestone stepped surface with no smooth casing stones left anywhere (not the Khafre pyramid), flat-ish top, seen from the front, complete pyramid from base to the top, no sphinx, no other pyramids.",
    "everest": "Mount Everest, the rocky Himalayan peak with snow and ice, sharp summit pyramid, clear sky with no clouds or snow plume, complete mountain from the wide base to the summit, wide shape.",
    "burj": "Burj Khalifa skyscraper in Dubai, very tall slender silver glass tower with stepped setbacks and a long spire, seen from the front, complete building from base to spire tip, very tall and thin.",
    "umeda": "The Umeda Sky Building in Osaka, two tall slender glass skyscraper towers standing side by side, connected at the very top by the Floating Garden Observatory with its big circular opening, seen from the front, complete building from base to top." + FLAT,
    "fuji": "Mount Fuji,the symmetrical volcano with a snow-capped peak and blue-purple slopes, complete mountain from the summit down to the very ends of its long gentle foothills, both left and right slopes curve smoothly all the way down to flat ground level and taper to nothing, nothing cut off at the sides, very wide shape with magenta space beyond both ends.",
}


def generate(name, prompt):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    if os.path.exists(path):
        print(f"  [SKIP] {name}")
        return True
    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=f"{STYLE}\n\nSubject: {prompt}",
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
    ok = 0
    for i, name in enumerate(names, 1):
        print(f"[{i}/{len(names)}] {name}")
        ok += generate(name, images[name])
        time.sleep(3)
    print(f"=== 完了 {ok}/{len(names)} ===")


if __name__ == "__main__":
    main()
