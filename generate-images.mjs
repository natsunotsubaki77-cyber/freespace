import { GoogleGenAI } from "@google/genai";
import { writeFileSync, readFileSync, mkdirSync, existsSync } from "fs";

const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error("環境変数 GEMINI_API_KEY を設定してください");
  process.exit(1);
}

const ai = new GoogleGenAI({ apiKey: API_KEY });
const MODEL = "gemini-2.5-flash-image";

const outDir = "C:/Users/ando/freespace/images";
if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

const STYLE = `子供向け絵本の1ページのような温かい手描き風イラスト。水彩画風、パステルカラー、太い手描きアウトライン、丸みのあるかわいいフォルム。キャラクターにはかわいい顔(目・ほっぺ・口)つき。横長16:9。テキストや文字は絶対に含めない。`;

const levels = [
  {
    name: "おはなばたけ",
    original: `${STYLE}
春のお花畑。青空、にっこり笑う黄色い太陽(左上)、白い雲が2つ、きれいな虹。
緑の丘にピンク・青・紫のお花がたくさん。左側に大きな濃い緑の木。木のベンチ。
白いうさぎ1匹、オレンジのちょうちょ1匹、黄色い小鳥1羽。キラキラエフェクト。`,
    changes: [
      "太陽の色を黄色からオレンジに変えて",
      "雲を2つから1つに減らして",
      "左の木の色を濃い緑から明るい黄緑に変えて",
      "右寄りのピンクの花を1つだけ黄色に変えて",
      "ちょうちょの色をオレンジから水色に変えて",
    ],
    diffs: [
      { label: "たいようのいろ", hint: "たいようをみて" },
      { label: "くもがない", hint: "そらをみて" },
      { label: "きのいろ", hint: "ひだりのきをみて" },
      { label: "おはなのいろ", hint: "みぎのおはなをみて" },
      { label: "ちょうちょのいろ", hint: "ちょうちょをみて" },
    ],
  },
  {
    name: "うみべ",
    original: `${STYLE}
夏の海辺。水色の空、ウインクする太陽、小さい雲1つ。
青い海に波。小さな白いヨットが浮かんでいる。黄色い砂浜。まっすぐ立つヤシの木(左)。赤いパラソル。ピンクの貝殻2つ。オレンジのカニ(顔つき)。小鳥2羽。水面キラキラ。`,
    changes: [
      "雲を大きくして",
      "ヨットを消して(海にヨットがない)",
      "ヤシの木を右に傾けて",
      "パラソルの色を赤から水色に変えて",
      "右の貝殻をピンクから水色に変えて",
    ],
    diffs: [
      { label: "くものおおきさ", hint: "くもをみて" },
      { label: "ヨットがない", hint: "うみのうえをみて" },
      { label: "ヤシのきのかたむき", hint: "ヤシのきをみて" },
      { label: "パラソルのいろ", hint: "パラソルをみて" },
      { label: "かいがらのいろ", hint: "かいがらをみて" },
    ],
  },
  {
    name: "まちなみ",
    original: `${STYLE}
夕焼けの街。オレンジのグラデーション空、おねむ顔の赤い夕陽。
カラフルな家5軒が横一列: (左から)クリーム壁+赤い屋根、薄紫壁+オレンジ屋根、薄緑壁+緑屋根、薄オレンジ壁+茶屋根、薄黄壁+緑屋根。
灰色の道路。赤い車1台。座っている黒猫1匹。街灯2本(光つき)。オレンジの鳥と水色の鳥。`,
    changes: [
      "一番左の家の屋根を赤から水色に変えて",
      "左から2番目の家の壁を薄紫から薄オレンジに変えて",
      "一番右の家の屋根を緑から黄色に変えて",
      "車の色を赤から青に変えて",
      "黒猫を消して",
      "水色の鳥を消して",
    ],
    diffs: [
      { label: "やねのいろ(ひだり)", hint: "いちばんひだりのいえ" },
      { label: "おうちのいろ", hint: "ひだりから2ばんめのいえ" },
      { label: "やねのいろ(みぎ)", hint: "いちばんみぎのいえ" },
      { label: "くるまのいろ", hint: "くるまをみて" },
      { label: "ねこがいない", hint: "どうろのあたりをみて" },
      { label: "ことりがいない", hint: "そらをみて" },
    ],
  },
  {
    name: "すいぞくかん",
    original: `${STYLE}
海の中。深い青のグラデーション。上から光が差す。砂の海底。
右向きの大きいオレンジの魚(顔つき)。水色の小魚3匹。紫のクラゲ2匹(顔つき)。
ピンクのタコ(顔つき)。緑のカメ(顔つき)。左右に赤いサンゴ。緑の海藻2箇所(同じ高さ)。赤いヒトデ(顔つき)。泡6個。`,
    changes: [
      "泡を6個から3個に減らして",
      "右のサンゴを赤から黄色に変えて",
      "右の海藻を短くして",
      "大きいオレンジの魚を左向きに変えて",
      "クラゲを1匹消して(1匹だけにして)",
      "ヒトデの色を赤からピンクに変えて",
    ],
    diffs: [
      { label: "あわのかず", hint: "あわをかぞえて" },
      { label: "サンゴのいろ", hint: "みぎのサンゴ" },
      { label: "かいそうのながさ", hint: "みぎのかいそう" },
      { label: "さかなのむき", hint: "おおきいさかな" },
      { label: "クラゲがいない", hint: "クラゲをかぞえて" },
      { label: "ヒトデのいろ", hint: "ヒトデをみて" },
    ],
  },
  {
    name: "うちゅう",
    original: `${STYLE}
宇宙。暗い紺色の背景。たくさんの小さな星。
にっこり顔の青い地球(中くらいの大きさ)。おねむ顔の黄色い三日月。茶色の土星(輪つき)。
まっすぐ上向きの白いロケット(炎つき)。カラフルなUFO1機。
ゆるい角度の黄色い流れ星。赤紫の星雲。緑の宇宙人1人。キラキラ星。`,
    changes: [
      "地球を大きくして",
      "土星の色を茶色から金色に変えて",
      "ロケットを斜めに傾けて",
      "UFOを消して",
      "流れ星の角度を急にして(もっと縦に近く)",
      "星雲の色を赤紫から紫に変えて",
    ],
    diffs: [
      { label: "ちきゅうのおおきさ", hint: "ちきゅうをみて" },
      { label: "どせいのいろ", hint: "どせいをみて" },
      { label: "ロケットのかたむき", hint: "ロケットをみて" },
      { label: "UFOがいない", hint: "UFOをさがして" },
      { label: "ながれぼしのかくど", hint: "ながれぼしをみて" },
      { label: "せいうんのいろ", hint: "せいうんをみて" },
    ],
  },
];

async function generateOriginal(prompt, filename) {
  console.log(`  生成中: ${filename}...`);
  const r = await ai.models.generateContent({
    model: MODEL,
    contents: [{ role: "user", parts: [{ text: prompt }] }],
    generationConfig: {
      responseModalities: ["image", "text"],
      imageMimeType: "image/png",
    },
  });
  for (const p of r.candidates[0].content.parts) {
    if (p.inlineData) {
      writeFileSync(`${outDir}/${filename}`, Buffer.from(p.inlineData.data, "base64"));
      console.log(`  ✓ ${filename} (${Math.round(p.inlineData.data.length / 1024)}KB)`);
      return p.inlineData.data;
    }
  }
  throw new Error("画像が返されませんでした");
}

async function generateModified(originalBase64, changes, filename) {
  console.log(`  編集中: ${filename}...`);
  const changeText = changes.map((c, i) => `${i + 1}. ${c}`).join("\n");
  const r = await ai.models.generateContent({
    model: MODEL,
    contents: [
      {
        role: "user",
        parts: [
          {
            inlineData: {
              mimeType: "image/png",
              data: originalBase64,
            },
          },
          {
            text: `この絵本風イラストを以下の点だけ変更してください。構図・配置・スタイルは完全に同じままで、指定箇所だけ変えてください。テキストや文字は絶対に含めないでください。

変更点:
${changeText}

重要: 上記以外の部分は一切変えないでください。全体のレイアウト、キャラクターの位置、背景は同じに保ってください。`,
          },
        ],
      },
    ],
    generationConfig: {
      responseModalities: ["image", "text"],
      imageMimeType: "image/png",
    },
  });
  for (const p of r.candidates[0].content.parts) {
    if (p.inlineData) {
      writeFileSync(`${outDir}/${filename}`, Buffer.from(p.inlineData.data, "base64"));
      console.log(`  ✓ ${filename} (${Math.round(p.inlineData.data.length / 1024)}KB)`);
      return p.inlineData.data;
    }
  }
  throw new Error("画像が返されませんでした");
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  const results = [];

  for (let i = 0; i < levels.length; i++) {
    const level = levels[i];
    console.log(`\n====== レベル ${i + 1}: ${level.name} ======`);

    try {
      const origB64 = await generateOriginal(level.original, `level${i + 1}_original.png`);
      await sleep(3000);

      const modB64 = await generateModified(origB64, level.changes, `level${i + 1}_modified.png`);
      await sleep(3000);

      results.push({
        name: level.name,
        original: origB64,
        modified: modB64,
        diffs: level.diffs,
      });
    } catch (e) {
      console.error(`  ✗ レベル${i + 1}でエラー:`, e.message);
      results.push({ name: level.name, original: null, modified: null, diffs: level.diffs });
    }
  }

  // levels.json 生成
  const jsonOut = results.map((r) => ({
    name: r.name,
    originalSrc: r.original ? `data:image/png;base64,${r.original}` : null,
    modifiedSrc: r.modified ? `data:image/png;base64,${r.modified}` : null,
    diffs: r.diffs,
  }));
  writeFileSync(`${outDir}/levels.json`, JSON.stringify(jsonOut));
  console.log(`\n✓ levels.json 保存完了 (${Math.round(JSON.stringify(jsonOut).length / 1024 / 1024)}MB)`);
}

main();
