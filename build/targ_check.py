"""targ_check.py : for every Jastrow entry (2018 file) that cites Onkelos on a pasuk, find the Aramaic word in that pasuk
it is about, and compare with our glossary: is that word linked to this entry, and do the meanings agree?
Writes build/targ-check.txt (one line per word/entry pair that needs a look) and prints a summary."""
import json, glob, re, collections, unicodedata as u
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
E = json.load(open(SP + 'jastrow/jastrow-2018.json', encoding='utf8'))
for f in ['jastrow-lookups.json', 'jastrow-lookups-2.json']:          # Sefaria's current text where we have it
    E.update(json.load(open(SP + 'jastrow/' + f, encoding='utf8'))['entries'])
CITES = json.load(open(SP + 'jastrow/targ-o-cites.json', encoding='utf8'))
IX = json.load(open(SP + 'j/index.json', encoding='utf8'))
BOOKS = {'Genesis': 'bereishit', 'Exodus': 'shemot', 'Leviticus': 'vayikra', 'Numbers': 'bamidbar', 'Deuteronomy': 'devarim'}
N = lambda s: u.normalize('NFC', s)
def key(h):
    t = re.sub(r'\s*([IVX]+|[¹²³⁴⁵])$', '', (h or '').strip().lstrip('*'))
    c = re.sub(r'[^א-ת]', '', u.normalize('NFD', t)).translate(str.maketrans('ךםןףץ', 'כמנפצ'))
    return c[:-1] + 'ה' if len(c) > 2 and c[-1] in 'אהי' else c
def loose(h):
    k = key(h)
    if len(k) > 2: k = k[0] + re.sub('[וי]', '', k[1:])     # plene/defective spelling
    k = re.sub('(תה|ת|ה|ין|ן)$', '', k) if len(k) > 3 else k   # emphatic, feminine and plural endings
    return k
def plain(e):
    return re.sub(r'<[^>]+>', ' ', json.dumps(e.get('content', {}), ensure_ascii=False) + ' ' + (e.get('language_reference') or ''))
def gl(e): return '; '.join(re.findall(r'<i>(.*?)</i>', json.dumps(e.get('content', {}), ensure_ascii=False)))[:110]
# pasuk -> parsha, words with their glossary entries
G, LEX, VER = {}, {}, {}
for f in sorted(glob.glob(SP + 'g/*.json')):
    pid = f.split('/')[-1][:-5]; g = json.load(open(f, encoding='utf8')); G[pid] = g; LEX.update(g['lex'])
    p = json.load(open(SP + f'p/{pid}.json', encoding='utf8'))
    for v in p['V']:
        words = re.sub(r'<[^>]+>|\([^)]*\)|[:׃,.;]', ' ', ' '.join(v['t'])).split()
        VER[(pid, v['c'], v['v'])] = words
BYCV = {}
for (pid, c, v), w in VER.items():
    bk = None
    BYCV.setdefault((c, v), []).append(pid)
def book_of(pid):
    order = list(G)
    i = order.index(pid)
    return 'Genesis' if i < 12 else 'Exodus' if i < 23 else 'Leviticus' if i < 33 else 'Numbers' if i < 43 else 'Deuteronomy'
PBOOK = {}
_m = re.search(r'\{"bereishit": \[\d[^}]*\}', open(SP + 'bereishit-onkelos.html', encoding='utf8').read())
_order = re.findall(r'"(\w+)": \[', _m.group(0)); _bk = 'Genesis'
for _p in _order:
    _bk = {'shemot': 'Exodus', 'vayikra': 'Leviticus', 'bamidbar': 'Numbers', 'devarim': 'Deuteronomy'}.get(_p, _bk); PBOOK[_p] = _bk
rows, stat = [], collections.Counter(); NEW = {}
seen = set()
for rid, book, c, v, onk in CITES:
    if rid not in E: continue
    pids = [p for p in BYCV.get((c, v), []) if PBOOK.get(p) == book]
    if not pids: stat['pasuk not found'] += 1; continue
    pid = pids[0]; g = G[pid]; at = g['at'].get(f'{c}:{v}', {})
    e = E[rid]; ek = {key(h) for h in [e['headword']] + (e.get('alt_headwords') or []) if "'" not in h and '׳' not in h} - {''}
    hits = []
    for w in VER[(pid, c, v)]:
        fm = at.get(N(w)) or g['forms'].get(N(w)) or at.get(w) or g['forms'].get(w)
        if not fm or fm.get('l') in (None, 'name', 'ednote', 'yy', 'yat'): continue
        lx = LEX.get(fm['l'], {})
        cand = {key(lx.get('h')), key(fm.get('stem')), key(lx.get('r'))} - {''}
        if ek & cand: hits.append((w, fm, lx))
        elif {loose(x) for x in ek} & {loose(x) for x in cand if x}: hits.append((w, fm, lx))
    k0 = (rid, pid, c, v)
    if k0 in seen: continue
    seen.add(k0)
    if not hits: stat['no matching word in the pasuk'] += 1; continue
    w, fm, lx = hits[0]; l = fm['l']
    cur = IX.get(l); exact = key(lx.get('h')) in ek or loose(lx.get('h')) in {loose(x) for x in ek}
    curexact = bool(cur and cur[0] in E and key(lx.get('h')) in {key(h) for h in [E[cur[0]]['headword']] + (E[cur[0]].get('alt_headwords') or [])})
    if exact and not curexact and not (cur and cur[0] == rid):
        NEW.setdefault(l, []).append(rid); stat['new link (cited entry is this exact word)'] += 1
    if cur and cur[0] == rid: stat['linked to this entry'] += 1; continue
    if cur and (rid in cur[3] or rid in cur[2]): stat['in the tabs / other entries'] += 1; kind = 'TAB'
    else: stat['not linked'] += 1; kind = 'NOT'
    curtxt = f"{cur[0]} {E[cur[0]]['headword']}: {gl(E[cur[0]])[:60]}" if cur and cur[0] in E else 'no entry'
    rows.append(f"{kind} | {pid} {c}:{v} | {w} [{l}: {lx.get('h','')} = {lx.get('g','')[:50]}] here: {fm.get('here','')[:45]} || cites {rid} {e['headword']}: {gl(e)} || now {curtxt}")
json.dump({l: collections.Counter(r).most_common(1)[0][0] for l, r in NEW.items()}, open(SP + 'build/jas-targ.proposed.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
open(SP + 'build/targ-check.txt', 'w', encoding='utf8').write('\n'.join(sorted(rows)))
print(stat, len(rows), 'to look at')
