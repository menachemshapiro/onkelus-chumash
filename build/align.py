"""Auto-split Hebrew verses at major disjunctive te'amim and align Targum/English clauses.
Writes data.json: list of {c, v, h:[...], t:[...], e:[...], p:'פ'|'ס'|None}."""
import json, re, sys

UP = '/root/.claude/uploads/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/'
DL = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/dl/'
import os
BOOK = os.environ.get('BOOK', 'Genesis')
FILES = {
 'Genesis': ('dbd23d2b-Genesis_-_he_-_Tanach_with_Ta_amei_Hamikra.json', UP + '09b0d455-Onkelos_Genesis_-_he_-_merged.json', '1b6a1d52'),
 'Exodus': ('e1572105-Exodus_-_he_-_Tanach_with_Ta_amei_Hamikra.json', UP + '6c366ab6-Onkelos_Exodus_-_he_-_merged.json', 'bd51e55f'),
 'Leviticus': ('1057161d-Leviticus_-_he_-_Tanach_with_Ta_amei_Hamikra.json', UP + '9162c7ff-Onkelos_Leviticus_-_he_-_merged.json', '2988b6f4'),
 'Numbers': ('505481c8-Numbers_-_he_-_Tanach_with_Ta_amei_Hamikra.json', UP + 'e619952a-Onkelos_Numbers_-_he_-_merged.json', '3e809a0b'),
 'Deuteronomy': ('992a40c0-Deuteronomy_-_he_-_Tanach_with_Ta_amei_Hamikra.json', UP + '2cff8119-Onkelos_Deuteronomy_-_he_-_merged.json', '639d7313'),
}
_h, _t, _e = FILES[BOOK]
HEB = json.load(open(UP + _h))['text']
TG = json.load(open(_t))['text']
EN = json.load(open(UP + f'{_e}-Onkelos_{BOOK}_-_en_-_Metsudah_Chumash__Metsudah_Publications__2009__with_Onkelos_translation_.json'))['text']

import os
SPEC = os.environ.get('RANGE', '1:1-6:8'); OUT = os.environ.get('OUT', 'data.json')
_a, _b = SPEC.split('-'); C0, V0 = map(int, _a.split(':')); C1, V1 = map(int, _b.split(':'))
END = [(c, V0 if c == C0 else 1, V1 if c == C1 else len(HEB[c - 1])) for c in range(C0, C1 + 1)]
BREAK = set('֑֒֓֔֕')  # etnachta, segol, shalshelet, zakef katon/gadol
OVR = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}


def htoks(clause):
    return len(re.split(r'[\s־]+', clause.strip()))


STRONG = set('\u0591\u0592\u0593')  # etnachta, segolta, shalshelet
ZAKEF = set('\u0594\u0595')
def split_heb(text):
    pet = None
    m = re.search(r'\s*\((פ|ס)\)\s*$', text)
    if m:
        pet = m.group(1); text = text[:m.start()]
    text = text.replace(' \u05c0 ', ' ')  # paseq
    words = text.split()
    # half = up to next strong break or end; split at zakef only if pieces stay readable
    strong_at = [i for i, w in enumerate(words) if any(c in STRONG for c in w)] + [len(words) - 1]
    out, cur, start = [], [], 0
    for i, w in enumerate(words):
        cur.append(w)
        if i == len(words) - 1: break
        if any(c in STRONG for c in w):
            out.append(' '.join(cur)); cur = []; continue
        if any(c in ZAKEF for c in w):
            nxt = next(k for k in strong_at if k >= i)
            if len(cur) >= 2 and (nxt - i) >= 2:
                out.append(' '.join(cur)); cur = []
    if cur: out.append(' '.join(cur))
    return out, pet


def balance(parts, tag):
    o, c = f'<{tag}>', f'</{tag}>'
    res, carry = [], False
    for p in parts:
        if carry: p = o + p
        opens, closes = p.count(o), p.count(c)
        carry = opens > closes
        if carry: p = p + c
        res.append(p)
    return res


def cut(tokens, weights, score):
    """Choose cut positions near proportional targets, preferring high score(i) (cut before token i)."""
    n, total = len(tokens), sum(weights)
    cuts, acc, last = [], 0, 0
    for w in weights[:-1]:
        acc += w
        target = round(n * acc / total)
        best, bscore = None, -1e9
        for i in range(max(last + 1, target - 4), min(n - 1, target + 4) + 1):
            if i <= last or i >= n: continue
            s = score(i) - abs(i - target) * 0.6
            if s > bscore: best, bscore = i, s
        if best is None: best = min(max(last + 1, target), n - 1)
        cuts.append(best); last = best
    segs, prev = [], 0
    for cpos in cuts + [n]:
        segs.append(' '.join(tokens[prev:cpos])); prev = cpos
    return segs


NIQ = re.compile(r'[\u0591-\u05C7]')
def bare(w): return NIQ.sub('', re.sub(r'<[^>]+>', '', w)).replace('\u05be', ' ').split(' ')[0]
MAP = {'את': ['ית'], 'כי': ['ארי'], 'אשר': ['די', 'ד'], 'על': ['על'], 'בין': ['בין'], 'מן': ['מן'], 'לא': ['לא'],
       'כל': ['כל', 'כול'], 'אל': ['לות', 'ל'], 'הנה': ['הא'], 'אלה': ['אלין'], 'זה': ['דין', 'דא'], 'גם': ['אף'], 'עד': ['עד'],
       'ויאמר': ['ואמר'], 'ויהי': ['והוה', 'והות'], 'ויקרא': ['וקרא'], 'וירא': ['וחזא'], 'ויעש': ['ועבד']}
GOD = {'אלהים', 'יהוה', 'האלהים', 'ליהוה', 'ויהוה'}
def tg_score(htext_next_first, hprev_last, ttoks):
    hb = bare(htext_next_first); hl = bare(hprev_last)
    hv = hb.startswith('ו'); hcore = hb[1:] if hv else hb
    def score(i):
        tb = bare(ttoks[i]); tp = bare(ttoks[i - 1])
        tv = tb.startswith('ו'); tcore = tb[1:] if tv else tb
        s = 0.0
        if hv and tv: s += 2
        if hv != tv: s -= 1
        if hb in MAP and any(tb.startswith(m) for m in MAP[hb]): s += 3
        elif hcore in MAP and any(tcore.startswith(m) for m in MAP[hcore]): s += 3
        if hl in GOD and tp in ('יי', 'אלהים', 'דיי'): s += 3
        if tp.endswith(':'): s -= 5
        return s
    return score
def align_tg(text, hcl):
    toks = text.split()
    if len(hcl) == 1 or len(toks) < len(hcl): return [text] + [''] * (len(hcl) - 1), 9
    # cut one boundary at a time so each uses its own Hebrew anchor
    weights = [htoks(c) for c in hcl]
    n, total = len(toks), sum(weights)
    cuts, acc, last, worst = [], 0, 0, 9
    for k in range(len(hcl) - 1):
        acc += weights[k]
        target = round(n * acc / total)
        sc = tg_score(hcl[k + 1].split()[0], hcl[k].split()[-1], toks)
        best, bs, raw = None, -1e9, 0
        for i in range(max(last + 1, target - 4), min(n - 1, target + 4) + 1):
            v = sc(i) - abs(i - target) * 0.4
            if v > bs: best, bs, raw = i, v, sc(i)
        if best is None: best = min(max(last + 1, target), n - 1)
        worst = min(worst, raw); cuts.append(best); last = best
    segs, prev = [], 0
    for c in cuts + [n]: segs.append(' '.join(toks[prev:c])); prev = c
    return balance(segs, 'b'), worst


def align_en(text, hcl):
    toks = text.split()
    if len(hcl) == 1 or len(toks) < len(hcl): return [text] + [''] * (len(hcl) - 1)
    nextv = [bare(c.split()[0]).startswith('ו') for c in hcl[1:]]
    depth, inside = 0, []
    for t in toks:
        inside.append(depth > 0)
        depth += t.count('[') - t.count(']')
    def score(i):
        if inside[i]: return -5
        prev = re.sub(r'<[^>]+>', '', toks[i - 1])
        w = re.sub(r'<[^>]+>', '', toks[i]).lower()
        s = 0
        if re.search(r'[.;:]["\]\)]*$', prev): s += 3
        elif re.search(r'[,]["\]\)]*$', prev): s += 2
        if w in ('and', 'but', 'then', 'for', 'so'): s += 1.2
        if i < 2 or i > len(toks) - 2: s -= 3
        return s
    return balance(cut(toks, [htoks(c) for c in hcl], score), 'b')


def norm(w): return re.sub(r'[^\w\u05d0-\u05ea]', '', NIQ.sub('', re.sub(r'<[^>]+>', '', w))).lower()
def apply_ovr(src, spec, key, nm):
    toks = src.split()
    if isinstance(spec, list):  # anchors: each new segment starts at first match after previous cut
        nt = [norm(x) for x in toks]; cuts = [0]
        for a in spec:
            aw = [norm(x) for x in a.split()]
            pos = next((i for i in range(cuts[-1] + 1, len(toks)) if nt[i:i + len(aw)] == aw), None)
            if pos is None: print('ANCHOR MISS', key, nm, a); continue
            cuts.append(pos)
        cuts.append(len(toks))
        return balance([' '.join(toks[a:b]) for a, b in zip(cuts, cuts[1:])], 'b'); segs = [x.split() for x in spec.split('|')]
    flat = [w for sg in segs for w in sg]
    if len(flat) != len(toks) or any(norm(a) != norm(b) for a, b in zip(flat, toks)):
        print('OVR MISMATCH', key, nm, len(flat), len(toks), [(a, b) for a, b in zip(flat, toks) if norm(a) != norm(b)][:3])
    out, k = [], 0
    for sg in segs: out.append(' '.join(toks[k:k + len(sg)])); k += len(sg)
    return balance(out, 'b')

# Metsudah italicizes transliterated Hebrew terms after Bereishis; those are not Onkelos departures
TRANSLIT = re.compile(r"(?i)^(kohein|kohanim|kohein gadol|gadol|tzoraas|tzorua|metzora|nesek|zov|zovah|matzoh|matzos|chometz|chametz|sela|selaim|ephod|log|nisan|omer|shofar|shekel|shekels|gerah|eiphah|ephah|hin|kor|terumah|kodesh|nazir|azazel|urim|tumim|choshen|me’il|mitznefes|tzitz|avneit|chagigah|shekolim|shekalim|mishkon|mishkan|shabbos|shabbosos|shabbasos|amos|amo¯s|amoh|amohs|molech|chazak|shofor|sukkos|succos|tachash|teruah|teruahs|kehunah|eishel|solom|chogov|esrog|lulav|hadasim|aravos|tzora’as|tzoraas|epha|pesach|tzizis|tzitzis|minchah|sela’im|yoveil|yovel|bris|mezuzah|tefillin|kohanim|leviim|amein|mitzvah|mitzvos|mitzvohs|totafos|mon|shemitah|tzir’oh|cheirem|cherem|shittim|ayah|tinshames|shovuos|yidoni|nega|charchur)[’'s.,;:]*$")
TEXTFIX = {} if BOOK != 'Genesis' else {'3:12': [('me—she', 'me — she')], '13:17': [('land—its', 'land — its'), ('breadth—for', 'breadth — for')]}
data = []
for c, first, last in END:
    for v in range(first, last + 1):
        key = f'{c}:{v}'
        h, pet = split_heb(HEB[c - 1][v - 1])
        t, e = TG[c - 1][v - 1], EN[c - 1][v - 1]
        e = e.replace('<i>', '<b>').replace('</i>', '</b>')
        for a_, b_ in TEXTFIX.get(key, []): e = e.replace(a_, b_)
        if BOOK != 'Genesis':
            e = re.sub(r'\s*—\s*', ' — ', e).strip()  # space every em-dash
            e = re.sub(r'(?<!\[)<b>([^<]*)</b>', lambda m: m.group(1) if TRANSLIT.match(m.group(1).strip()) else m.group(0), e)
        o = OVR.get(key, {})
        e_src = e
        for a_, b_ in o.get('efix', []): e = e.replace(a_, b_)
        for a_, b_ in o.get('tfix', []): t = t.replace(a_, b_)
        if 'hg' in o:
            g, k, nh = o['hg'], 0, []
            assert sum(g) == len(h), (key, g, len(h))
            for size in g: nh.append(' '.join(h[k:k + size])); k += size
            h = nh
        if 'hw' in o:
            ws, k, nh = ' '.join(h).split(' '), 0, []
            assert sum(o['hw']) == len(ws), (key, o['hw'], len(ws), ws)
            for size in o['hw']: nh.append(' '.join(ws[k:k + size])); k += size
            h = nh
        tc, conf = (apply_ovr(t, o['t'], key, 't'), 9) if 't' in o else align_tg(t, h)
        ec = apply_ovr(e, o['e'], key, 'e') if 'e' in o else align_en(e, h)
        for nm, arr in (('t', tc), ('e', ec)):
            if len(arr) != len(h): print('COUNT MISMATCH', key, nm, len(arr), len(h))
        data.append({'c': c, 'v': v, 'h': h, 't': tc, 'e': ec, 'p': pet, 'conf': conf, 'ovr': bool(o)})
        if o.get('efix'): data[-1]['oe'] = e_src  # source text before corrections, for 'Show original'
json.dump(data, open('/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/build/' + OUT, 'w'), ensure_ascii=False)
print(len(data), 'verses')
