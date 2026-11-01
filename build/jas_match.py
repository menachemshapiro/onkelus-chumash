"""jas_match.py : match each glossary dictionary entry (lex) to its Jastrow entry from jastrow/jastrow-lookups.json.
Writes build/jas-map.json {lex_id: [best_rid, ...others]} and prints a summary."""
import json, glob, re, collections, unicodedata as u
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
J = json.load(open(SP + 'jastrow/jastrow-lookups.json', encoding='utf8')); Q, E = J['queries'], J['entries']
# round 2: the entries round 1's entries point to ("v. X")
J2 = json.load(open(SP + 'jastrow/jastrow-lookups-2.json', encoding='utf8')); Q.update(J2['queries']); E.update(J2['entries'])
import os
if os.path.exists(SP + 'jastrow/jastrow-lookups-3.json'):   # round 3: Sefaria's current text for entries first taken from the 2018 copy
    E.update(json.load(open(SP + 'jastrow/jastrow-lookups-3.json', encoding='utf8'))['entries'])
APIR = set(E)                     # entries downloaded from Sefaria (current text)
# Sefaria-Data's 2018 copy fills in every entry we have not downloaded (jas_2018.py)
_F = json.load(open(SP + 'jastrow/jastrow-2018.json', encoding='utf8')); _F.update(E); EAPI, EFULL = E, _F
lex = {}
for f in glob.glob(SP + 'g/*.json'):
    for k, v in json.load(open(f, encoding='utf8'))['lex'].items(): lex.setdefault(k, v)
def cons(s):
    s = u.normalize('NFD', s or ''); s = re.sub(r'[^א-ת]', '', s)
    return s.translate(str.maketrans('ךםןףץ', 'כמנפצ'))
def voc(s): return re.sub(r'[^ְ-ׇּׁׂא-ת]', '', u.normalize('NFD', s or ''))
def hw(e): return re.sub(r'\s+[IVX]+$|^\*', '', e['headword'].strip())
STOP = set('the a an of to and in or be is as for by on at with from that this it his her its'.split())
def ew(s): return {w for w in re.findall(r'[a-z]+', (s or '').lower()) if w not in STOP and len(w) > 2}
def indexes(E):
    c, v = collections.defaultdict(list), collections.defaultdict(list)
    for rid, e in E.items(): c[cons(hw(e))].append(rid); v[voc(hw(e))].append(rid)
    return c, v
IDX = {'api': indexes(EAPI), 'full': indexes(EFULL)}
E = EAPI; BYC, BYV = IDX['api']
def text(e): return re.sub(r'<[^>]+>', '', json.dumps(e.get('content', {}), ensure_ascii=False))
def resolve(rid, depth=0):
    """follow a bare cross-reference ("v. X", "= X") to the entry it points to, when we have it"""
    e = E[rid]; t = text(e)
    defs = ' '.join(s_.get('definition', '') for s_ in e.get('content', {}).get('senses', []) if isinstance(s_, dict))
    plain = re.sub(r'<[^>]+>', '', defs).strip(' ,.;')
    m = re.match(r'^(?:same,?\s*)?(?:v\.|=)\s*(?:sub\s+)?([\u0590-\u05ff*]+(?:\s+[IVX]+)?)', plain)
    if depth < 2 and m and len(plain) < 45:
        tgt = m.group(1).strip('*')
        if '׳' in tgt or "'" in tgt: return rid      # an abbreviated pointer ("v. sub חז׳"): can't tell which entry
        for r in BYV.get(voc(re.sub(r'\s+[IVX]+$', '', tgt)), []) + BYC.get(cons(tgt), []):
            if r != rid and hw(E[r]) == re.sub(r'\s+[IVX]+$', '', tgt) or (r != rid and cons(hw(E[r])) == cons(tgt)):
                return resolve(r, depth + 1)
    return rid
def dangling(rid):
    """a bare cross-reference ("v. X") whose target entry was not downloaded"""
    e = E[rid]
    defs = ' '.join(s_.get('definition', '') for s_ in e.get('content', {}).get('senses', []) if isinstance(s_, dict))
    plain = re.sub(r'<[^>]+>', '', defs).strip(' ,.;')
    return bool(re.match(r'^(?:same,?\s*)?(?:v\.|=)\s*(?:sub\s+)?[\u0590-\u05ff*]', plain)) and len(plain) < 45 and resolve(rid) == rid
def verbal(e):
    d = json.dumps(e.get('content', {}), ensure_ascii=False)
    return bool(re.search(r'<i>\s*to |binyan|"Pa\.|Pa\. |Af\. |Ithpa', d[:1500]))
HWMAP = {}
for _r, _e in EAPI.items(): HWMAP.setdefault(_e['headword'].strip(), _r)
def glosses(e, depth=0):
    """meaning words of an entry; an Aramaic entry that says only "same" borrows them from the entry before it (Jastrow's convention)"""
    g = _glosses(e)
    head = re.sub(r'<[^>]+>', '', (e.get('language_reference') or '') + ' ' + text(e)[:120])
    if depth < 2 and re.search(r'\bsame\b', head) and e.get('prev_hw') in HWMAP:
        g |= glosses(E[HWMAP[e['prev_hw']]], depth + 1)
    return g
def _glosses(e):
    d = json.dumps(e.get('content', {}), ensure_ascii=False) + (e.get('language_reference') or '')
    return ew(' '.join(re.findall(r'<i>(.*?)</i>', d)) + ' ' + ' '.join(re.findall(r'[a-z][a-z ,;-]{2,40}', text(e)[:200])))
def score(v, rid):
    e = E[rid]; h = hw(e); sc = 0; kind = 'word'; vx = False
    if cons(h) == cons(v['h']): vx = voc(h) == voc(v['h']); sc += 10 + (3 if vx else 0)
    elif any(cons(a) == cons(v['h']) for a in e.get('alt_headwords', [])): sc += 8; vx = any(voc(a) == voc(v['h']) for a in e.get('alt_headwords', []))
    elif v.get('r') and cons(h) == cons(v['r']): kind = 'root'; sc += 4
    else: return (-1, kind, rid)
    tgt = resolve(rid); t = E[tgt]
    ov = len(glosses(t) & ew(v.get('g')))
    if kind == 'root' and not (((v.get('p') or '').startswith('verb') and verbal(t)) or ov): return (-1, kind, tgt)
    if kind == 'word' and not (vx or ov): return (-1, kind, tgt)
    isverb = (v.get('p') or '').startswith('verb')
    if kind == 'word': sc += 2 if isverb == verbal(t) else -2
    d = json.dumps(t.get('content', {}), ensure_ascii=False)
    if 'ch' in (t.get('language_code') or ''): sc += 1
    if 'Onkelos' in d: sc += 2
    elif 'Targ' in d: sc += 1
    sc += min(8, 2 * ov)
    return (sc, kind, tgt)
PREV = json.load(open(SP + 'build/jas-map.prev.json', encoding='utf8'))   # earlier picks: kept when scores tie
out, stat = {}, collections.Counter()
for k, v in lex.items():
    if not v.get('h') or v.get('p') in ('the Divine Name',): continue
    E = EAPI; BYC, BYV = IDX['api']
    cands = set(Q.get(v['h'], [])) | set(BYC.get(cons(v['h']), [])) | (set(BYC.get(cons(v['r']), [])) if v.get('r') else set())
    sc = sorted((score(v, r) for r in sorted(cands)), key=lambda x: (-x[0], x[2] != PREV.get(k, {}).get('rid'), x[2]))
    sc = [x for x in sc if x[0] >= 6]
    if not sc:                    # nothing among the downloaded entries: try the whole 2018 dictionary (exact word only)
        E = EFULL; BYC, BYV = IDX['full']
        cands = set(BYC.get(cons(v['h']), []))
        sc = sorted((score(v, r) for r in cands), key=lambda x: -x[0]); sc = [x for x in sc if x[0] >= 10 and x[1] == 'word']
        if sc: stat['found in 2018 copy'] += 1
    seen = []
    for x in sc:
        if x[2] not in seen: seen.append(x[2])
    if sc and E is EAPI and not (glosses(E[sc[0][2]]) & ew(v.get('g'))):
        # the best guess shares no meaning with the glossary; if the word itself is only a pointer to an entry we don't have,
        # show that pointer (it names the right entry) rather than an unrelated homograph
        ptr = [r for r in cands if cons(hw(E[r])) == cons(v['h']) and dangling(r)]
        if ptr: out[k] = {'rid': ptr[0], 'kind': 'word', 'also': [x for x in seen if x != ptr[0]][:2]}; stat['pointer'] += 1; continue
    if sc: out[k] = {'rid': sc[0][2], 'kind': sc[0][1], 'also': seen[1:3]}; stat[sc[0][1]] += 1
    else: stat['none'] += 1
TARG = json.load(open(SP + 'build/jas-targ.json', encoding='utf8'))
for k, rid in TARG.items():  # Jastrow cites this pasuk of Onkelos under this entry, and it is the same word
    out[k] = {'rid': rid, 'kind': 'word', 'also': [x for x in ([out[k]['rid']] + out[k]['also'] if k in out else []) if x != rid][:2]}
stat['from Targ. O. citations'] = len(TARG)
OVR = {k: v for k, v in json.load(open(SP + 'build/jas-override.json', encoding='utf8')).items() if not k.startswith('_')}
for k, rid in OVR.items():   # hand-checked corrections
    if rid is None: out.pop(k, None)
    else:   # "rid" for the word's own entry, "rid:root" for the entry of its root
        rid, kind = (rid.split(':') + ['word'])[:2]
        out[k] = {'rid': rid, 'kind': kind, 'also': [x for x in out.get(k, {}).get('also', []) if x != rid]}
stat['hand-checked'] = len(OVR)
json.dump(out, open(SP + 'build/jas-map.json', 'w', encoding='utf8'), ensure_ascii=False)
print(stat)
