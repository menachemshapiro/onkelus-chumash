import json, re, subprocess, sys
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
src = open(SP + 'bereishit-onkelos.html').read()

# hand-aligned v9 data for 1:1-1:10
a = src.index('const VERSES = ['); b = src.index('\n];', a) + 3
import os
V9F = SP + 'build/v9-first10.json'
if not os.path.exists(V9F):
    lines = src[a:b].split('\n')[1:-1]
    json.dump([json.loads(l.rstrip(',')) for l in lines[:10]], open(V9F, 'w'), ensure_ascii=False)
v9 = json.load(open(V9F))

def heb_num(n):
    if n == 15: return 'טו'
    if n == 16: return 'טז'
    tens = ['', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ']; ones = ['', 'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט']
    return tens[n // 10] + ones[n % 10]

AL = ['ראשון','שני','שלישי','רביעי','חמישי','שישי','שביעי','מפטיר']
def almap(als):  # merge aliyot that start on the same pasuk (e.g. Eikev: shevi'i = maftir)
    m = {}
    for k, cv in enumerate(als): m[cv] = (m[cv] + ' ו' + AL[k]) if cv in m else AL[k]
    return m
sys.path.insert(0, SP + 'build'); import parshiyot as PM
import reorder as RO
import fixes as FX
GEN_FN = {'bereishit': 'data.json', 'lechlecha': 'data-lech.json', 'chayeisarah': 'data-chayei.json'}
PARS = []
for pid, he, book, en, hk in PM.P:
    fn = GEN_FN.get(pid, f'data-{pid}.json')
    if not os.path.exists(SP + 'build/' + fn): continue
    PARS.append((pid, fn, PM.aliyot(hk), book, he, en))
RAS = {}
V, R = [], []
for pr, fn, als, book, _he, _en in PARS:
    if book not in RAS: RAS[book] = json.load(open('/root/.claude/uploads/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/' + PM.RASHI[book]))['text']
    RA = RAS[book]
    ALIYOT = almap(als)
    for x in json.load(open(SP + 'build/' + fn)):
        c, v = x['c'], x['v']
        if book == 'Genesis' and c == 1 and v <= 10:
            h, t, e = v9[v-1]['h'], v9[v-1]['t'], v9[v-1]['e']
        else:
            h, t, e = x['h'], x['t'], x['e']
        e0 = e
        h, t, e = RO.apply(pr, c, v, h, t, e)
        reord = e is not e0
        eb = e
        h, t, e = FX.apply(pr, c, v, h, t, e)
        fixed = list(e) != list(eb)
        h = [re.sub(r'\((פ|ס)\)\s*', r'<span class="pet">{\1}</span> ', c_) for c_ in h]
        o = {'pr': pr, 'c': c, 'v': v, 'n': heb_num(v), 'h': h, 't': t, 'e': e}
        if reord: o['oe'], o['ok'] = FX.fix_en(' '.join(e0)).replace('</b> <b>', ' '), 'order'  # original English order
        elif fixed or x.get('oe'): o['oe'], o['ok'] = (x.get('oe') or ' '.join(eb)).replace('</b> <b>', ' '), 'text'  # source text before corrections
        if x['p']: o['p'] = x['p']
        if (c, v) in ALIYOT: o['a'] = ALIYOT[(c, v)]
        V.append(o)
        com = RA[c-1][v-1] if v-1 < len(RA[c-1]) else []
        R.append([re.sub(r'([֑-ׇ])\1+', r'\1', s_) for s_ in com])

FX.check()
# verse data goes to one file per parsha (p/<id>.json); the page fetches them as needed
os.makedirs(SP + 'p', exist_ok=True)
by, META = {}, {}
for o, r in zip(V, R): by.setdefault(o['pr'], ([], []))[0].append(o); by[o['pr']][1].append(r)
for pid, (vv, rr) in by.items():
    json.dump({'V': vv, 'R': rr}, open(SP + f'p/{pid}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    META[pid] = [vv[0]['c'], vv[0]['v'], vv[-1]['c'], vv[-1]['v']]
import eo_merge; eo_merge.merge()   # English as Onkelos reads it (build/eo/), added to the parsha files
src = src[:a] + 'const VERSES = [\n];' + src[b:]
a = src.index('const RASHI = '); b = src.index('\n', a)
src = src[:a] + 'const RASHI = [];' + src[b:]
if 'const META = ' in src:
    a = src.index('const META = '); b = src.index('\n', a); src = src[:a] + src[b + 1:]
a = src.index('const PARSHIYOT = [')
src = src[:a] + 'const META = ' + json.dumps(META) + ';  // first and last perek:pasuk of each parsha\n' + src[a:]
a = src.index('const PARSHIYOT = ['); b = src.index('\n];', a) + 3
PJ = []
have = {p[0] for p in PARS}
for p in PARS:
    PJ.append({'id': p[0], 'name': p[4], 'book': PM.BOOKS[p[3]], 'en': p[5]})
    for cid, che, cen, chk, parts in PM.COMBINED:
        if parts[1] == p[0] and parts[0] in have:
            PJ.append({'id': cid, 'name': che, 'book': PM.BOOKS[p[3]], 'en': cen, 'parts': list(parts),
                       'al': [[c, v, n] for (c, v), n in almap(PM.aliyot(chk)).items()]})
src = src[:a] + 'const PARSHIYOT = [\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in PJ) + '\n];' + src[b:]
open(SP + 'bereishit-onkelos.html', 'w').write(src)
print(len(V), sum(len(r) for r in R), 'rashi comments')
