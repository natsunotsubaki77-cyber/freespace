// 一度ひらけば オフラインでも あそべるように ファイルを ためておく
const CACHE = 'size-compare-v8';
const FILES = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png',
  './images/adult.webp','./images/bear.webp','./images/cat.webp','./images/elephant.webp','./images/ferris.webp','./images/freed.webp','./images/fuji.webp','./images/giraffe.webp','./images/hamster.webp','./images/h3.webp','./images/harukas.webp','./images/himeji.webp','./images/jumbo.webp','./images/kid.webp','./images/mirai.webp','./images/nara_daibutsu.webp','./images/penguin.webp','./images/rabbit.webp','./images/shiba.webp','./images/shinkansen.webp','./images/skybus.webp','./images/skytree.webp','./images/toji.webp','./images/tokyotower.webp','./images/torii.webp','./images/trex.webp','./images/ushiku.webp','./images/vending.webp','./images/whale.webp','./images/pyramid.webp','./images/everest.webp','./images/burj.webp','./images/umeda.webp','./images/shinkansen_mid.webp','./images/roomy.webp'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))));
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))));
self.addEventListener('fetch', e => {
  // 新しい版があれば それを使い、つながらないときは ためた ファイルを使う
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok && e.request.method === 'GET') { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  }).catch(() => caches.match(e.request)));
});
