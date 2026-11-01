"""eo_review.py ALIGNFILE PARSHA TITLE OUT.html : a readable review page of a word-by-word alignment."""
import json, re, sys, html, unicodedata as u
N = lambda s: u.normalize('NFC', s)
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
path, pid, title, out = sys.argv[1:5]
P = {f"{v['c']}:{v['v']}": v for v in json.load(open(SP + f'p/{pid}.json', encoding='utf8'))['V']}
verses, cur = {}, None
for line in open(path, encoding='utf8'):
    line = line.rstrip('\n')
    if not line.strip() or line.startswith('#'): continue
    if line.startswith('@ '): cur = line[2:].strip(); verses[cur] = []; continue
    if line == '= same': verses[cur].append(None); continue
    if line.startswith('E: '): verses[cur].append({'E': line[3:], 'map': [], 'plus': [], 'notes': []}); continue
    cl = verses[cur][-1]
    if line.startswith('+'): cl['plus'].append(line[1:].strip())
    elif line.startswith('!'): cl['notes'].append(line[1:].strip())
    else: a, _, e = line.partition('='); cl['map'].append((a.strip(), e.strip()))
hl = lambda s: html.escape(s).replace('&lt;b&gt;', '<mark>').replace('&lt;/b&gt;', '</mark>')
plain = lambda s: re.sub(r'<[^>]+>', '', s)
nclauses = sum(1 for c in verses.values() for x in c if x)
nnotes = sum(len(x['notes']) for c in verses.values() for x in c if x)
body = []
for cv, cls in verses.items():
    v = P[cv]
    rows = []
    for j, cl in enumerate(cls):
        if cl is None:
            rows.append(f'<div class="cl same"><p class="tg" dir="rtl" lang="arc">{html.escape(plain(v["t"][j]))}</p><p class="unch">Unchanged: {hl(v["e"][j])}</p></div>')
            continue
        words = ''.join(f'<tr><td dir="rtl" lang="arc">{html.escape(a)}</td><td>{html.escape(e) if e else "<span class=nt>not translated</span>"}</td></tr>' for a, e in cl['map'])
        words += ''.join(f'<tr class="plus"><td>—</td><td>{html.escape(p)} <span class=nt>English only</span></td></tr>' for p in cl['plus'] if p)
        notes = ''.join(f'<li>{html.escape(n)}</li>' for n in cl['notes'])
        rows.append(f'''<div class="cl"><p class="tg" dir="rtl" lang="arc">{html.escape(plain(v["t"][j]))}</p>
<div class="pair"><div><span class="lab">Combined (as printed)</span><p>{hl(v["e"][j])}</p></div>
<div class="onk"><span class="lab">As Onkelos reads it</span><p>{hl(cl["E"])}</p></div></div>
<details><summary>Word by word ({len(cl["map"])} Aramaic words)</summary><div class="tw"><table><thead><tr><th>Targum</th><th>English used</th></tr></thead><tbody>{words}</tbody></table></div></details>
{f'<ul class="notes">{notes}</ul>' if notes else ''}</div>''')
    body.append(f'<section id="v{cv.replace(":", "-")}"><h2>{cv.replace(":", " : ")}</h2>{"".join(rows)}</section>')
page = f'''<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Hebrew:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#f7f8f6; --surface:#ffffff; --ink:#1d2424; --muted:#5f6b6b; --rule:#dfe4e2; --tg:#1f5a5a; --mark:#f3dfa8; --markink:#3b2d06; --onk:#eef5f4; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#141a1a; --surface:#1b2323; --ink:#e3e8e6; --muted:#9aa7a5; --rule:#2c3737; --tg:#7cc4bd; --mark:#5c4a1a; --markink:#f6e7bd; --onk:#1d2d2c; color-scheme: dark; }} }}
:root[data-theme="dark"] {{ --bg:#141a1a; --surface:#1b2323; --ink:#e3e8e6; --muted:#9aa7a5; --rule:#2c3737; --tg:#7cc4bd; --mark:#5c4a1a; --markink:#f6e7bd; --onk:#1d2d2c; color-scheme: dark; }}
body {{ background:var(--bg); color:var(--ink); font-family:"Source Serif 4", Georgia, serif; font-size:17px; line-height:1.55; }}
main {{ max-width:880px; margin:0 auto; padding-block:28px 64px; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }}
h1 {{ font-size:1.7rem; line-height:1.2; margin:0 0 6px; text-wrap:balance; }}
.lede {{ color:var(--muted); font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.92rem; margin:0 0 8px; max-width:65ch; }}
.key {{ font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.85rem; color:var(--muted); margin:0 0 24px; }}
mark {{ background:var(--mark); color:var(--markink); border-radius:3px; padding:0 2px; }}
section {{ border-top:1px solid var(--rule); padding-top:16px; margin-top:24px; }}
h2 {{ font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.8rem; letter-spacing:.08em; color:var(--tg); margin:0 0 10px; }}
.cl {{ background:var(--surface); border:1px solid var(--rule); border-radius:10px; padding:12px 14px; margin:0 0 12px; }}
.cl.same {{ padding:8px 14px; }}
.tg {{ font-family:"Noto Serif Hebrew", serif; font-size:1.3rem; color:var(--tg); margin:0 0 8px; text-align:right; }}
.unch {{ color:var(--muted); font-size:.95rem; margin:0; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.pair > div {{ min-width:0; }}
.pair p {{ margin:2px 0 0; }}
.onk {{ background:var(--onk); border-radius:8px; padding:6px 10px; }}
.lab {{ font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.72rem; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
details {{ margin-top:10px; font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.88rem; }}
summary {{ cursor:pointer; color:var(--tg); }}
.tw {{ overflow-x:auto; }}
table {{ border-collapse:collapse; margin-top:6px; width:100%; }}
td, th {{ border-bottom:1px solid var(--rule); padding:4px 8px; text-align:left; vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; font-size:.78rem; }}
td[dir=rtl] {{ font-family:"Noto Serif Hebrew", serif; font-size:1.1rem; text-align:right; white-space:nowrap; color:var(--tg); }}
.nt {{ color:var(--muted); font-style:italic; font-size:.8rem; }}
tr.plus td {{ color:var(--muted); }}
.notes {{ margin:10px 0 0; padding-left:18px; font-family:"IBM Plex Sans", system-ui, sans-serif; font-size:.86rem; color:var(--ink); }}
.notes li {{ margin:3px 0; }}
.notes li::marker {{ color:#c08a2c; }}
@media (max-width: 640px) {{ .pair {{ grid-template-columns:1fr; }} }}
</style>
<main>
<h1>{html.escape(title)}</h1>
<p class="lede">Each pasuk where Onkelos departs from the plain meaning, clause by clause: the Metsudah English as printed, the English as Onkelos reads it, and the word-by-word match that checks nothing was lost. {nclauses} clauses changed; {nnotes} notes for review.</p>
<p class="key"><mark>Highlighted</mark> = Onkelos's wording. Orange-bulleted notes are points to look at.</p>
{"".join(body)}
</main>'''
open(out, 'w', encoding='utf8').write(page)
print('wrote', out)
