"""jas_build.py : write the Jastrow pop-up data from jastrow/jastrow-lookups.json and build/jas-map.json.
  j/index.json      {glossary lex id: [rid, "word"|"root", [other rids]]}
  j/<A..Z>.json     {rid: {"h": headword, "html": entry as safe HTML}}, grouped by the first letter of the rid"""
import json, os, re, html, collections, glob
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
E = json.load(open(SP + 'jastrow/jastrow-2018.json', encoding='utf8'))      # Sefaria-Data 2018 copy: fills gaps only
for _f in ['jastrow-all.json', 'jastrow-extra.json', 'jastrow-lookups.json', 'jastrow-lookups-2.json', 'jastrow-lookups-3.json', 'jastrow-pages.json']:   # Sefaria's current text wins
    if os.path.exists(SP + 'jastrow/' + _f): E.update(json.load(open(SP + 'jastrow/' + _f, encoding='utf8'))['entries'])
import sys; sys.path.insert(0, SP + 'build'); import jas_fix
SPLITOFF = jas_fix.apply(E)   # hand fixes checked against the 1903 scans (build/jas_fix.py)
DEPTH = int(os.environ.get('JDEPTH', '9'))   # how many link-steps away from a glossary word an entry is still included
M = json.load(open(SP + 'build/jas-map.json', encoding='utf8'))
TAG = re.compile(r'<(/?)(\w+)([^>]*)>')
import urllib.parse
HW2RID = {}
for _r, _e in sorted(E.items(), key=lambda x: x[1].get('src') == '2018'): HW2RID.setdefault(_e['headword'].strip(), _r)
def hwkey(h):
    h = u.normalize('NFD', h.replace('²', ' II').replace('³', ' III').replace('⁴', ' IV').replace('¹', ' I')); num = re.search(r'\s([IVX]+)$', h.strip())
    return re.sub(r'[^\u05d0-\u05ea]', '', h) + (' ' + num.group(1) if num else '')
import unicodedata as u
HW2KEY, _seen = {}, collections.Counter()
for _r, _e in E.items(): _seen[hwkey(_e['headword'])] += 1
for _r, _e in E.items():
    if _seen[hwkey(_e['headword'])] == 1: HW2KEY[hwkey(_e['headword'])] = _r
def clean(s):
    """keep <i>, <b>, <sup>, rtl spans and Sefaria reference links; drop every other tag"""
    def fix(m):
        close, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if tag in ('i', 'b', 'sup', 'sub'): return f'<{close}{tag}>'
        if tag == 'span': return '</span>' if close else ('<span dir="rtl">' if 'rtl' in attrs else '<span>')
        if tag == 'a':
            if close: return '</a>'
            j18 = re.search(r'data-r="([^"]+)"', attrs)
            if 'jx2018' in attrs and j18:
                jx = j18.group(1)
                if jx not in E: return '<a>'
                LINKED.add(jx)
                return f'<a dir="rtl" class="jx" data-r="{jx}" role="link" tabindex="0">'   # opened inside the pop-up; no link out to Sefaria
            h = re.search(r'href="([^"]*)"', attrs)
            if not h: return '<a>'
            href = h.group(1); href = href if href.startswith('/') else '/' + href
            rtl = ' dir="rtl"' if 'rtl' in attrs else ''
            m = re.match(r'^/Jastrow,_(.+)\.\d+$', urllib.parse.unquote(href))
            tgt = m.group(1).replace('_', ' ').strip() if m else ''
            if m and re.fullmatch(r'[\u05d0-\u05ea]׳', tgt): return '<a>'       # Sefaria links abbreviations like נ׳ to nowhere
            jx = (HW2RID.get(tgt) or HW2KEY.get(hwkey(tgt))) if m else None
            if jx:   # a link to another Jastrow entry we have: opened inside the pop-up
                LINKED.add(jx)
                return f'<a{rtl} class="jx" data-r="{jx}" role="link" tabindex="0">'
            return f'<a{rtl} href="https://www.sefaria.org{html.escape(href, quote=True)}" target="_blank" rel="noopener">'
        return ''
    s = TAG.sub(fix, s or '')
    return re.sub(r'<a>(.*?)</a>', r'\1', s)
def senses(lst):
    out = []
    for s in lst or []:
        if not isinstance(s, dict): continue
        part = ''
        if s.get('number'): part += f'<b class="jn">{html.escape(s["number"])}</b> '
        g = s.get('grammar')
        if g:
            part += f'<b class="jg">{html.escape(g.get("verbal_stem", ""))}</b> ' + ', '.join(f'<span dir="rtl">{html.escape(x)}</span>' for x in g.get('binyan_form', [])) + ' '
        if s.get('definition'): part += clean(s['definition'])
        if s.get('senses'): part += '<div class="jsub">' + senses(s['senses']) + '</div>'
        if part.strip(): out.append(f'<p>{part}</p>')
    return ''.join(out)
def render(e):
    head = ' '.join(x for x in [clean(e.get('language_code', '')), clean(e.get('language_reference', '')), html.escape((e.get('content') or {}).get('morphology', ''))] if x and x.strip())
    body = senses((e.get('content') or {}).get('senses'))
    return (f'<p class="jhead">{head}</p>' if head else '') + body
import unicodedata as u
def base(h): return re.sub(r'\s*([IVX]+|[¹²³⁴⁵])$', '', h.strip().lstrip('*'))
def voc(h): return re.sub(r'[^\u05b0-\u05bc\u05c1\u05c2\u05c7\u05d0-\u05ea]', '', u.normalize('NFD', base(h)))
BYV = collections.defaultdict(list)
for r, e in E.items(): BYV[voc(e['headword'])].append(r)
def key(h, dots=False):
    """letters only, final forms normalised, a weak last letter (א ה י) read as ה: צְלֵי, צְלָא, צָלָה, צָלִי all give צלה.
    With dots=True, shin and sin stay apart (שׁ → ש1, שׂ → ש2)."""
    t = u.normalize('NFD', base(h))
    if dots: t = re.sub(r'ש([\u0591-\u05c7]*?)\u05c1', r'1\1', re.sub(r'ש([\u0591-\u05c7]*?)\u05c2', r'2\1', t))
    c = re.sub(r'[^\u05d0-\u05ea12]', '', t).translate(str.maketrans('ךםןףץ', 'כמנפצ'))
    return c[:-1] + 'ה' if len(c) > 2 and c[-1] in 'אהי' else c
def alts(e): return [a for a in (e.get('alt_headwords') or []) if '׳' not in a and "'" not in a]   # skip abbreviated forms like צִלְ׳
BYK = collections.defaultdict(set)
for r, e in E.items():
    for h in [e['headword']] + alts(e): BYK[key(h)].add(r)
def clash(a, b):
    """True when both forms mark shin/sin and they differ"""
    da, db = re.sub(r'[^12]', '', a), re.sub(r'[^12]', '', b)
    return bool(da and db and da != db)
def related(rid, word):
    """every entry with the same letters as the matched entry or the glossary word (headword or alternative form), in dictionary order"""
    e = E[rid]; forms = [e['headword']] + alts(e) + [word]
    ks = {key(h) for h in forms}; dk = [key(h, True) for h in forms]
    out = set()
    for r in set().union(*(BYK[k] for k in ks)):
        fr = [key(h, True) for h in [E[r]['headword']] + alts(E[r])]
        if any(not clash(a, b) and key_eq(a, b) for a in dk for b in fr): out.add(r)
    return sorted(out | {rid})
def key_eq(a, b): return re.sub(r'[12]', 'ש', a) == re.sub(r'[12]', 'ש', b)
os.makedirs(SP + 'j', exist_ok=True)
for f in glob.glob(SP + 'j/[A-Z].json') + glob.glob(SP + 'j/index.json'): os.remove(f)   # j/abbr.json comes from jas_abbr.py
LEX = {}
for f in glob.glob(SP + 'g/*.json'):
    for k, v in json.load(open(f, encoding='utf8'))['lex'].items(): LEX.setdefault(k, v)
LINKED = set()
NOTSEF = set(json.load(open(SP + 'jastrow/not-in-word-search.json'))) if os.path.exists(SP + 'jastrow/not-in-word-search.json') else set()
EXTRA = {}
GIRSA = {k: v for k, v in json.load(open(SP + 'build/jas-girsa.json', encoding='utf8')).items() if not k.startswith('_')}
def stub(r): return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', render(E[r])))) < 60
def same_as(r):
    """Jastrow's "ch. same": an Aramaic entry whose meaning is the entry right before it. Returns that entry's id."""
    e = E[r]
    lead = re.sub(r'<[^>]+>', '', (e.get('language_reference') or '')).strip(' .,;')
    first = next((x.get('definition', '') for x in (e.get('content') or {}).get('senses', []) if isinstance(x, dict) and x.get('definition')), '')
    first = re.sub(r'<[^>]+>', '', first).strip(' .,;')
    if not (lead.startswith('same') or re.match(r'^(ch\.\s*)?same\b', first)): return None
    p = r[0] + '%05d' % (int(r[1:]) - 1)
    return p if p in E else None
def plain_text(r):
    e = E[r]; return re.sub(r'<[^>]+>', ' ', (e.get('language_reference') or '') + ' ' + json.dumps(e.get('content') or {}, ensure_ascii=False))
def preced(r):
    """Jastrow's "preced." / "preced. wds.": the entry refers to the one right before it ("(preced.)" = derived from it,
    "v. preced.", "= preced.", "fem. of preced." ...; every linked use points to the entry right before). Returns that entry's id."""
    p = r[0] + '%05d' % (int(r[1:]) - 1)
    return p if p in E and re.search(r'\bpreced\.', plain_text(r)) else None
def next_w(r):
    """Jastrow's "next w." / "next ws." / "next art.": the entry refers to the one right after it. Returns that entry's id."""
    n = r[0] + '%05d' % (int(r[1:]) + 1)
    return n if n in E and re.search(r'\bnext\s+(?:w|ws|art)\.', plain_text(r)) else None
def before(r):
    """the entry r is shown after: the one it calls "same" or "preced.", or the one before it that says "next w." """
    b = same_as(r) or preced(r)
    if b: return b
    p = r[0] + '%05d' % (int(r[1:]) - 1)
    return p if p in E and next_w(p) == r else None
def nxt(r):
    n = r[0] + '%05d' % (int(r[1:]) + 1)
    return n if n in E else None
GMAX = 8
def group(r):
    """the entry plus the entries it is tied to, in dictionary order: an entry marked "same" or "preced." comes after
    the entry it refers to. [first, the next tied one, ...]; long chains are cut to GMAX entries around r."""
    if not re.fullmatch(r'[A-Z]\d{5}', r): return [r]   # an entry split off by jas_fix (no place in the numbering)
    first, seen = r, {r}
    while before(first) and before(first) not in seen: first = before(first); seen.add(first)
    out = [first]
    while nxt(out[-1]) and before(nxt(out[-1])) == out[-1] and len(out) < 60: out.append(nxt(out[-1]))
    if len(out) > GMAX:
        i = out.index(r) if r in out else 0
        lo = max(0, min(i - 2, len(out) - GMAX)); out = out[lo:lo + GMAX]
    return out
def ent(r):
    d = {'h': E[r]['headword'], 'a': alts(E[r])[:2], 'html': jas_fix.fix_html(r, render(E[r]))}
    if E[r].get('src') == '2018': d['s'] = 2018
    g = group(r)
    if len(g) > 1:   # shown together, one under the other (the page puts each entry's title above it)
        d['g'] = g; LINKED.update(g)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', d['html']))).strip()
    if len(t) < 90 and re.match(r'^[,;\s]*(v\.|read\b|=|corr\.|s\. )', t):   # a bare pointer ("v. X"): the page shows X with it,
        v = list(dict.fromkeys(x for x in re.findall(r'class="jx" data-r="([^"]+)"', d['html']) if x != r))   # unless X is already in another tab
        if v: d['v'] = v
    return d
idx, groups = {}, collections.defaultdict(dict)
for k, m in M.items():
    tabs = related(m['rid'], LEX[k]['h'])
    rid = m['rid']
    keep, firsts = [], {}
    for t in tabs:                 # entries shown together get one tab (the first of them)
        f = group(t)[0]
        if f in firsts: continue
        firsts[f] = t; keep.append(t)
    gr = group(rid)[0]
    if gr in firsts: rid = firsts[gr]
    tabs = keep
    for t in list(tabs):           # an empty stub Sefaria doesn't have (a numeral letter, a bare pointer): fold it into the
        if t == rid or t not in NOTSEF or not stub(t): continue       # listing next to it, or drop the tab (NOTSEF: the stubs found only by page name)
        tabs.remove(t)
        nb = [x for x in (t[0] + '%05d' % (int(t[1:]) - 1), t[0] + '%05d' % (int(t[1:]) + 1)) if x in tabs or x == rid]
        if nb: EXTRA.setdefault(rid if rid in nb else nb[0], set()).add(t)
    also = [r for r in m['also'] if r not in tabs and r != rid]
    idx[k] = [rid, m['kind'], also, tabs if len(tabs) > 1 else []]
    if GIRSA.get(k): idx[k].append(GIRSA[k])   # a note: Jastrow cites this pasuk with a different reading
    m = dict(m, rid=rid)
    for r in [m['rid']] + also + tabs:
        groups[r[0]][r] = ent(r)
have = {r for d in groups.values() for r in d}
for step in range(DEPTH):
    todo = set(LINKED) - have
    if not todo: break
    for r in sorted(todo): groups[r[0]][r] = ent(r); have.add(r)
for nb, ts in EXTRA.items():     # show the folded stubs inside the listing they sit next to, after it
    for t in ts:
        if t not in groups[t[0]]: groups[t[0]][t] = ent(t)
    d = groups[nb[0]][nb]; d['g'] = list(d.get('g') or [nb]) + sorted(ts)   # the real entry first, so it gives the heading
for nid, host in SPLITOFF.items():   # an entry jas_fix split off its host: shown right after the host, wherever the host is shown
    if host not in groups[host[0]]: continue
    groups[nid[0]][nid] = ent(nid)
    for d in groups[host[0]].values():
        if host in (d.get('g') or []): d['g'].insert(d['g'].index(host) + 1, nid)
    hd = groups[host[0]][host]
    if not hd.get('g'): hd['g'] = [host, nid]
json.dump(idx, open(SP + 'j/index.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
for g, d in groups.items(): json.dump(d, open(SP + f'j/{g}.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(idx), 'glossary words;', sum(len(d) for d in groups.values()), 'entries in', len(groups), 'files')
