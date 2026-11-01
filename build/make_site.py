"""Build the home-screen web app (GitHub Pages) from the same page that is published on claude.ai.

Writes into the repository checkout given as argv[1]:
  index.html             the page, wrapped as a full document with app (PWA) tags
  p/<parsha>.json        verse data, one file per parsha
  g/<parsha>.json        Targum glossary, one file per parsha
  manifest.webmanifest   app name, icon, colours
  sw.js                  service worker: keeps every parsha on the phone for offline use
  icons/                 app icons
  build/, sources/       everything needed to rebuild the page (scripts, alignment fixes, Sefaria texts)
"""
import hashlib, json, os, shutil, sys, glob
from PIL import Image, ImageDraw, ImageFont

SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
UP = '/root/.claude/uploads/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/'
OUT = sys.argv[1]
os.makedirs(OUT + '/p', exist_ok=True)
os.makedirs(OUT + '/icons', exist_ok=True)

# ---- icons: ת״א (Targum Onkelos) in Mekorot Vilna, white on teal ----
FONT = SP + 'fonts-src/Mekorot (LPPL)/Vilna/Mekorot-Vilna-Bold.ttf'
def icon(size, path, pad=0.0):
    im = Image.new('RGB', (size, size), (31, 90, 90))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, int(size * (0.5 - pad)))
    text = 'ת"א'[::-1]  # PIL draws left to right: reversed so it reads ת״א
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    d.text(((size - (r - l)) / 2 - l, (size - (b - t)) / 2 - t), text, font=f, fill=(255, 255, 255))
    im.save(path)
icon(180, OUT + '/icons/apple-touch-icon.png')
icon(192, OUT + '/icons/icon-192.png')
icon(512, OUT + '/icons/icon-512.png')
icon(512, OUT + '/icons/icon-maskable-512.png', pad=0.12)
# link preview picture for WhatsApp, iMessage etc. (Open Graph)
import subprocess
subprocess.run([sys.executable, SP + 'build/og_image.py', OUT + '/icons/og.png'], check=True)

# ---- data files ----
for old in glob.glob(OUT + '/p/*.json'): os.remove(old)
for f in sorted(glob.glob(SP + 'p/*.json')): shutil.copy(f, OUT + '/p/')
pfiles = sorted(os.path.basename(f) for f in glob.glob(OUT + '/p/*.json'))
# Targum glossary, one file per parsha
os.makedirs(OUT + '/g', exist_ok=True)
for old in glob.glob(OUT + '/g/*.json'): os.remove(old)
for f in sorted(glob.glob(SP + 'g/*.json')): shutil.copy(f, OUT + '/g/')
gfiles = sorted(os.path.basename(f) for f in glob.glob(OUT + '/g/*.json'))
# Jastrow entries for the glossary (index + one file per first letter), loaded when an entry is opened
if os.path.isdir(OUT + '/j'): shutil.rmtree(OUT + '/j')
shutil.copytree(SP + 'j', OUT + '/j')
jfiles = sorted(os.path.basename(f) for f in glob.glob(OUT + '/j/*.json'))

# ---- index.html ----
page = open(SP + 'bereishit-onkelos.html', encoding='utf8').read()
head = '''<!doctype html>
<html lang="he">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#1f5a5a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="אונקלוס">
<meta name="description" content="Chumash with Targum Onkelos, clause by clause: Hebrew, Onkelos and English side by side, with Rashi, a tap-a-word Aramaic glossary and Jastrow.">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Chumash with Onkelos">
<meta property="og:title" content="Chumash with Onkelos · חומש עם אונקלוס">
<meta property="og:description" content="Hebrew, Targum Onkelos and English side by side, clause by clause. Tap any Aramaic word for its meaning; Rashi and Jastrow included.">
<meta property="og:url" content="https://menachemshapiro.github.io/onkelos-chumash/">
<meta property="og:image" content="https://menachemshapiro.github.io/onkelos-chumash/icons/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Bereishis 49:10 in Hebrew, Onkelos and English, with the Onkelos wording highlighted">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" href="icons/icon-192.png">
<style>html,body{margin:0;padding:0}</style>
</head>
<body>
'''
tail = '''
<script>
// home-screen app: keep the page and every parsha on the device (not used inside claude.ai)
if ("serviceWorker" in navigator && !/claude/i.test(location.hostname)) {
  addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
  // when a new version has been installed, reload once so it shows
  // (only when replacing an older version, not on the very first install)
  const hadOld = !!navigator.serviceWorker.controller; let reloaded = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (hadOld && !reloaded) { reloaded = true; location.reload(); } });
}
</script>
</body>
</html>
'''
index = head + page + tail
open(OUT + '/index.html', 'w', encoding='utf8').write(index)

# ---- manifest ----
json.dump({
    'name': 'Chumash with Onkelos', 'short_name': 'אונקלוס', 'lang': 'he', 'dir': 'rtl',
    'start_url': './', 'scope': './', 'display': 'standalone',
    'background_color': '#f7f8f6', 'theme_color': '#1f5a5a',
    'icons': [{'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
              {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
              {'src': 'icons/icon-maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}],
}, open(OUT + '/manifest.webmanifest', 'w', encoding='utf8'), ensure_ascii=False, indent=1)

# ---- service worker (version = hash of the site's contents, so every update installs fresh) ----
h = hashlib.sha256(index.encode())
for f in pfiles: h.update(open(OUT + '/p/' + f, 'rb').read())
for f in gfiles: h.update(open(OUT + '/g/' + f, 'rb').read())
for f in jfiles: h.update(open(OUT + '/j/' + f, 'rb').read())
version = h.hexdigest()[:12]
precache = ['./', 'index.html', 'manifest.webmanifest', 'icons/apple-touch-icon.png', 'icons/icon-192.png'] + ['p/' + f for f in pfiles] + ['g/' + f for f in gfiles] + ['j/index.json']
sw = f'''// generated by build/make_site.py
const VERSION = "{version}";
const CACHE = "onkelos-" + VERSION, RUNTIME = "onkelos-runtime";
const PRECACHE = {json.dumps(precache)};
self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== RUNTIME).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
self.addEventListener("fetch", e => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {{
    if (req.mode === "navigate") {{
      // the page: fresh when online, saved copy when offline
      e.respondWith(fetch(req).then(r => {{ const c = r.clone(); caches.open(CACHE).then(x => x.put("index.html", c)); return r; }})
        .catch(() => caches.match("index.html")));
      return;
    }}
    // Jastrow letter files are saved the first time they are opened, so they work offline after that
    e.respondWith(caches.match(req, {{ ignoreSearch: true }}).then(hit => hit || fetch(req).then(r => {{
      if (r.ok && url.pathname.includes("/j/")) {{ const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); }}
      return r;
    }})));
    return;
  }}
  // fonts and export libraries from other sites: use the saved copy, refresh it in the background
  if (/fonts\\.(googleapis|gstatic)\\.com|cdn\\.jsdelivr\\.net/.test(url.hostname)) {{
    e.respondWith(caches.open(RUNTIME).then(c => c.match(req).then(hit => {{
      const net = fetch(req).then(r => {{ if (r.ok || r.type === "opaque") c.put(req, r.clone()); return r; }}).catch(() => hit);
      return hit || net;
    }})));
  }}
}});
'''
open(OUT + '/sw.js', 'w', encoding='utf8').write(sw)
open(OUT + '/.nojekyll', 'w').write('')

# ---- build sources: scripts, alignment fixes, data, source texts ----
B = OUT + '/build'
if os.path.isdir(B): shutil.rmtree(B)
os.makedirs(B)
keep = ['*.py', 'ovr-*.json', 'data*.json', 'v9-first10.json', 'overrides*.json', 't17.js', 'trep.js', 'tgoto.js', 'tpdf.js', 'trc.js', 'ttypo.js', 'tperf.js', 'eotest.js', 'package.json', 'jas-map.json', 'jas-map.prev.json', 'jas-override.json', 'jas-targ.json', 'glfix.tsv', 'glapply.sh', 'jastrow-links-oct23.md', 'jas-girsa.json', 'jas_fix.py', 'meteg_test.js', 'jas7.js', 'jas11.js', 'jas13.js', 'jas15.js', 'jas16.js']
for pat in keep:
    for f in glob.glob(SP + 'build/' + pat):
        if f.endswith('.bak') or '.before' in f or os.path.basename(f).startswith('data-') and '.prev.' in f: continue
        shutil.copy(f, B)
shutil.copy(SP + 'bereishit-onkelos.html', B + '/page-template.html')
# glossary sources: dictionary, per-aliyah word lists, aliyah index, log of lookups on the CAL site
shutil.copytree(SP + 'build/gl', B + '/gl')
# "as Onkelos reads it": worksheets, hand-written word-by-word matches, merged output
for d in ['ws', 'ws-full', 'eo-align', 'eo', 'test-fonts']: shutil.copytree(SP + 'build/' + d, B + '/' + d)
# Jastrow: the fetch script and what it brought back from Sefaria
shutil.copytree(SP + 'jastrow', B + '/jastrow', ignore=shutil.ignore_patterns('__pycache__', '*progress*', 'html', 'separate', 'Jastrow-full.xml', 'jastrow-2018.json', 'jastrow-all.json', 'jastrow-complete*', '*.zip'))
for f in ['gl-aliyot.json', 'gl-stats.json', 'cal-log.json']:
    if os.path.exists(SP + 'build/' + f): shutil.copy(SP + 'build/' + f, B)
shutil.copy(SP + 'decisions.md', OUT + '/DECISIONS.md')
S = OUT + '/sources'
os.makedirs(S, exist_ok=True)
for f in glob.glob(UP + '*.json'):
    name = os.path.basename(f).split('-', 1)[1]
    shutil.copy(f, S + '/' + name)
print('site version', version, '·', len(pfiles), 'parsha files ·', len(gfiles), 'glossary files')
