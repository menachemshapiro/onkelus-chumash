"""auto_eo.py PARSHA [c:v-c:v] : first draft of "as Onkelos reads it" with a word-by-word match, for hand review.
Writes eo-align/<parsha>.draft.txt in the same format as the hand-made files, with "?" lines where the draft is unsure.

For each clause whose English has bold [<b>…</b>] Onkelos renderings:
  * every way of letting each bracket replace 0–5 of the English words before it is tried;
  * each candidate English is matched against the Aramaic words through the glossary;
  * the candidate that leaves the fewest Aramaic words and English words unmatched wins (fewer words replaced on a tie)."""
import json, re, sys, itertools, runpy, unicodedata as u
N = lambda s: u.normalize('NFC', s)
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
sys.argv, ARGS = ['gloss_build.py', 'todo', 'none'], sys.argv[1:]
G = runpy.run_path('gloss_build.py', run_name='bt')
pid = ARGS[0]; rng = ARGS[1] if len(ARGS) > 1 else None
V = json.load(open(SP + f'p/{pid}.json', encoding='utf8'))['V']

STOP = set('a an the of to in on at by for with from and or but that which who whom whose this these those is are was were be been being will shall would should may might can could do does did has have had not no nor it its he him his she her they them their we us our you your i me my so as if than then there here upon unto into out up all every each any one'.split())
def stem(w):
    w = w.lower().replace('’', "'").strip("'")
    if w.endswith("'s"): w = w[:-2]
    for suf, mn in (('ies', 4), ('ing', 5), ('ed', 4), ('es', 4), ('s', 4), ('ly', 5)):
        if w.endswith(suf) and len(w) >= mn: w = w[:-len(suf)]; break
    return w
ALIAS = {'israel': 'yisrael', 'yisroel': 'yisrael', 'yoseif': 'yosef', 'yitzchok': 'yitzchak', 'eisov': 'esav', 'adonoy': 'hashem', 'elohim': 'hashem', 'god': 'hashem', 'lord': 'hashem',
         'moshe': 'moshe', 'aharon': 'aharon', 'pharaoh': 'paroh', 'egypt': 'mitzrayim', 'canaan': 'kenaan', 'binyomin': 'binyamin', 'yehudah': 'yehudah'}
def norm(w):
    w = w.lower().replace('’', "'")
    return ALIAS.get(w.strip("'"), stem(w))
def words(s): return re.findall(r"[A-Za-z][A-Za-z’']*", re.sub(r'<[^>]+>', '', s))
def content(s): return [norm(w) for w in words(s) if w.lower() not in STOP]
LEXG = {k: v.get('g', '') for k, v in G['LEX'].items()}
def gloss_words(e):
    if not e: return set()
    h = re.sub(r'\((?:Hebrew|Onkelos)[^)]*\)|\([^)]*=[^)]*\)', ' ', e.get('here', ''))
    h = (h + ' ' + LEXG.get(e.get('l'), '')).replace('(', ' ').replace(')', ' ').replace('lit.', ' ')
    return set(content(h))
def like(a, b):
    return a == b or (len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4])
def hit(w, g): return any(like(w, x) for x in g)

def aram_tokens(t):
    t = re.sub(r'<[^>]+>', '', t); t = re.sub(r'\([^)]*\)', ' ', t)
    return [N(w).strip(':.,;') for w in t.replace('־', ' ').split() if re.search('[א-ת]', w)]

# --- English as a list of pieces: ('w', word), ('p', punctuation/space), ('onk', text), ('br', [plain bracket]), ('par', (paren)) ---
def pieces(e):
    out = []
    for m in re.finditer(r"\[<b>(.*?)</b>\]|\[[^\]]*\]|\([^)]*\)|<b>.*?</b>|[A-Za-z0-9][A-Za-z0-9’'\-]*|\s+|.", e):
        s = m.group(0)
        if m.group(1) is not None: out.append(('onk', m.group(1)))
        elif s.startswith('['): out.append(('br', s))
        elif s.startswith('('): out.append(('par', s))
        elif s.startswith('<b>'): out.append(('w', s))
        elif re.match(r'[A-Za-z0-9]', s): out.append(('w', s))
        else: out.append(('p', s))
    return out
def build(pcs, ks):
    """ks[i] = how many words (and parentheticals) before Onkelos bracket i it replaces"""
    keep = [True] * len(pcs); bi = 0
    for i, (k, s) in enumerate(pcs):
        if k != 'onk': continue
        n, j = ks[bi], i - 1; bi += 1
        while n > 0 and j >= 0:
            if pcs[j][0] in ('w', 'par'): keep[j] = False; n -= pcs[j][0] == 'w'
            elif pcs[j][0] in ('onk', 'br'): break
            j -= 1
        # a parenthetical right before the removed words goes too ("(there was) darkness")
    out = ''
    for i, (k, s) in enumerate(pcs):
        if not keep[i]: continue
        out += f'<b>{s.strip()}</b>' if k == 'onk' else s
    out = re.sub(r'\s+([,.;:!?])', r'\1', re.sub(r'\s{2,}', ' ', out)).strip()
    out = re.sub(r'^([,;:]\s*)', '', out)
    return out
def room(pcs):
    """how many words each bracket could replace: words back to the previous bracket"""
    r, cnt = [], 0
    for k, s in pcs:
        if k == 'w': cnt += 1
        elif k in ('onk',): r.append(min(cnt, 10)); cnt = 0
        elif k == 'br': cnt = 0
    return r

def score(eo, toks):
    ew = content(eo)
    pool = list(ew); miss_a = 0
    for g in toks:
        if not g: continue
        h = next((w for w in pool if hit(w, g)), None)
        if h: pool.remove(h)
        else: miss_a += 1
    return miss_a + len(pool)

def align(eo, toks, glosses):
    """greedy: each Aramaic word takes the English words its gloss shares; leftovers are listed for review"""
    ew = words(eo); used = [False] * len(ew); rows = []
    for t, g in zip(toks, glosses):
        gw = gloss_words(g); take = []
        for i, w in enumerate(ew):
            if not used[i] and w.lower() not in STOP and hit(norm(w), gw): take.append(i)
        # widen to neighbouring small words that belong with it (the, of, to, his …)
        if take:
            lo, hi = min(take), max(take)
            if hi - lo > 4: take = [take[0]]; lo = hi = take[0]
            while lo > 0 and not used[lo - 1] and ew[lo - 1].lower() in STOP and ew[lo - 1].lower() not in ('and',) : lo -= 1
            if t.startswith(('וְ', 'וּ', 'וַ', 'וִ', 'וֶ', 'וָ', 'וֵ')) and lo > 0 and not used[lo - 1] and ew[lo - 1].lower() == 'and': lo -= 1
            take = list(range(lo, hi + 1))
            for i in take: used[i] = True
        rows.append((t, ' '.join(ew[i] for i in take)))
    left = [ew[i] for i in range(len(ew)) if not used[i]]
    return rows, left

def main():
    lines = [f'# DRAFT for {pid}: made by auto_eo.py; "?" lines need a look.', '']
    total = flagged = 0
    for vi, v in enumerate(V):
        cv = f"{v['c']}:{v['v']}"
        if rng:
            a, b = rng.split('-'); key = lambda s: tuple(map(int, s.split(':')))
            if not (key(a) <= (v['c'], v['v']) <= key(b)): continue
        if not any('[<b>' in e for e in v['e']): continue
        lines.append(f'@ {cv}')
        vt = [t for t in (aram_tokens(x) for x in v['t'])]
        flat = [w for c in vt for w in c]
        gl, prev = [], None
        for w in flat: e, how = G['lookup'](w, v['c'], v['v'], pid, prev); gl.append(e); prev = w
        k0 = 0
        for j, e in enumerate(v['e']):
            toks = vt[j]; glosses = gl[k0:k0 + len(toks)]; k0 += len(toks)
            if '[<b>' not in e: lines.append('= same'); continue
            total += 1
            pcs = pieces(e); rm = room(pcs)
            gsets = [gloss_words(g) for g in glosses]
            best = None
            combos = 1
            for r in rm: combos *= r + 1
            if combos <= 4000: cand = itertools.product(*[range(r + 1) for r in rm])
            else:   # too many: settle one bracket at a time
                ks = [0] * len(rm)
                for i, r in enumerate(rm):
                    ks[i] = min(range(r + 1), key=lambda k: (score(build(pcs, ks[:i] + [k] + ks[i + 1:]), gsets), k))
                cand = [tuple(ks)]
            for ks in cand:
                eo = build(pcs, ks); sc = (score(eo, gsets), sum(ks))
                if best is None or sc < best[0]: best = (sc, eo, ks)
            (bad, _), eo, ks = best
            rows, left = align(eo, toks, glosses)
            lines.append('E: ' + eo)
            for t, en in rows: lines.append(f'{t} = {en}')
            for w in left: lines.append(f'+ {w}')
            miss = [t for t, en in rows if not en and t not in ('יָת', 'וְיָת')]
            content_left = [w for w in left if w.lower() not in STOP]
            if miss or content_left:
                flagged += 1
                lines.append(f'? check: Aramaic with no English: {" ".join(miss) or "-"} · English with no Aramaic: {" ".join(content_left) or "-"}')
        lines.append('')
    open(f'eo-align/{pid}.draft.txt', 'w', encoding='utf8').write('\n'.join(lines))
    print(f'{pid}: {total} clauses drafted, {flagged} flagged for a look')
main()
