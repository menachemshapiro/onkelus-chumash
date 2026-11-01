"""lit_auto.py : first draft of the exact English for every Targum clause, from the glossary (g/<parsha>.json), written to
build/lit/<parsha>.auto.txt in lit_merge.py's format. Hand-written build/lit/<parsha>.txt wins clause by clause.

Each word's meaning is the glossary's meaning for that word in that pasuk (or for its spelling), cleaned up:
  - "(he)", "(they)", "(of)" … are kept as plain words; a "(… not …)" is dropped (לָא has its own row);
  - "(lit. …)" is kept; notes like "(Hebrew: …)", "(= …)", "(here: …)", "(i.e. …)" are dropped; "X / Y" keeps X.
Words read together are paired: a noun with its demonstrative (זִמְנָא הָדָא = this time), "surely" doublings
(מִתַּב אִתּוּב), and fixed phrases (מִן קֳדָם, בְּדִיל דִּי, בַּר תּוֹרֵי …)."""
import json, glob, os, re, unicodedata as u
HERE = os.path.dirname(os.path.abspath(__file__)); SP = os.path.dirname(HERE) + '/'
N = lambda s: u.normalize('NFC', s)
bare = lambda s: re.sub(r'[֑-ׇ]', '', u.normalize('NFD', s))
FUNC = set('he she it they i you we am are is was were will shall be been of to the a an his her its their my your our me him them us one ones that who which there'.split())

def clean(here):
    s = here
    s = re.sub(r'\((?:Hebrew|here|also|i\.e\.|=|e\.g\.|cf\.|pl\.|fem\.|masc\.|sing\.|construct)[^)]*\)', '', s)
    s = re.sub(r'\([^)]*[א-ת][^)]*\)', '', s)                    # notes in Hebrew letters
    s = re.sub(r'\((?![Ll]it\.)[^)]*\bnot\b[^)]*\)', '', s)                 # "(do not)": לָא has its own row
    def unwrap(m):
        inner = m.group(1)
        if re.match(r'(?i)lit\.', inner) or inner.startswith('marks'): return m.group(0)
        ws = inner.lower().split()
        if ws and all(w in FUNC for w in ws): return inner
        return ''                                                           # "(Hashem)", "(as a priest)" …: dropped
    s = re.sub(r'\(([^()]*)\)', unwrap, s)
    s = s.split(' / ')[0]
    s = re.sub(r';\s.*$', '', s) if not re.search(r'\(lit\.[^)]*;', s) else s
    s = s.replace('(marks the object)', '(sign of the object)')
    return re.sub(r'\s+', ' ', s).strip(' ,')

DEM = {'הדין': 'this', 'הדא': 'this', 'דין': 'this', 'דא': 'this', 'האלין': 'these', 'הלין': 'these', 'ההוא': 'that', 'ההיא': 'that',
       'האנון': 'those', 'האנין': 'those'}
PHRASE = {('מן', 'קדם'): 'from before', ('בדיל', 'די'): 'so that', ('בתר', 'כן'): 'afterwards', ('כמא', 'די'): 'as',
          ('עד', 'כען'): 'still (lit. until now)', ('למא', 'דנן'): 'why is this', ('בר', 'תורי'): 'a calf (lit. a son of cattle)',
          ('בני', 'תורי'): 'calves (lit. sons of cattle)', ('על', 'כן'): 'therefore', ('על', 'אפי'): 'over the face of',
          ('מן', 'בתר'): 'after', ('כל', 'קבל'): 'opposite', ('לות', 'כל'): None}
def key(w): return bare(w).replace('־', '')
FIX = {'בדיל': 'for the sake of', 'עשרא': 'ten', 'בגין': 'because of'}   # common words whose glossary meaning is off on its own
LEX = {}
for _f in glob.glob(SP + 'g/*.json'):
    for _k, _v in json.load(open(_f, encoding='utf8'))['lex'].items(): LEX.setdefault(_k, _v)

def pairs(words, gl):
    """group the words: returns [(start, end, exact or None)]"""
    out, i = [], 0
    while i < len(words):
        w = words[i]; k = key(w); kk = k[1:] if k[:1] == 'ו' and len(k) > 2 else k; andp = 'and ' if kk != k else ''
        if i + 1 < len(words):
            k2 = key(words[i + 1])
            ph = PHRASE.get((kk, k2)) or PHRASE.get((k, k2))
            if ph:
                out.append((i, i + 2, (andp if PHRASE.get((kk, k2)) and kk != k else '') + ph)); i += 2; continue
            g1, g2 = gl[i], gl[i + 1]
            if k2 in DEM and g1 and g1.get('f', '').startswith('noun'):
                noun = clean(g1['here'])
                m = re.match(r'^((?:and |in |to |from |like |at |on |for |with |of |as )*)(?:the |a )?(.*)$', noun)
                out.append((i, i + 2, f'{m.group(1)}{DEM[k2]} {m.group(2)}')); i += 2; continue
            if g1 and g2 and g1.get('l') == g2.get('l') and g1.get('l') and 'infinitive' in g1.get('f', '') and 'infinitive' not in g2.get('f', ''):
                out.append((i, i + 2, 'surely ' + clean(g2['here']) + f' (lit. {clean(g1["here"])} {clean(g2["here"])})')); i += 2; continue
        out.append((i, i + 1, None)); i += 1
    return out

def run():
    tot = 0
    for pf in sorted(glob.glob(SP + 'p/*.json')):
        pid = os.path.basename(pf)[:-5]; g = json.load(open(SP + f'g/{pid}.json', encoding='utf8'))
        lines = ['# Draft made by lit_auto.py from the glossary. Do not edit: put corrections in ' + pid + '.txt (it wins clause by clause).']
        for v in json.load(open(pf, encoding='utf8'))['V']:
            at = g['at'].get(f"{v['c']}:{v['v']}", {})
            for j, t in enumerate(v['t']):
                a = (v.get('ea') or [None] * len(v['t']))[j]
                words = [w for ar, en in a['map'] for w in ar.split()] if a else re.sub(r'<[^>]+>|\([^)]*\)|[:׃,.;]', ' ', t).split()
                if not words: continue
                gl = [at.get(N(w)) or g['forms'].get(N(w)) for w in words]
                lines.append(f"@ {v['c']}:{v['v']}.{j}")
                for s, e, ex in pairs(words, gl):
                    if ex is None:
                        ex = clean(gl[s]['here']) if gl[s] else '?'
                        if gl[s] and (ex.startswith('-') or not ex):   # a suffix-like or empty meaning: the dictionary's first meaning
                            ex = re.split(r'[;,(]', LEX.get(gl[s].get('l'), {}).get('g', '') or '?')[0].strip() or ex
                        ex = FIX.get(key(words[s]), ex)
                        if gl[s] and gl[s].get('l') == 'yy' or key(words[s]) in ('יי', 'דיי', 'ויי', 'ליי', 'מיי', 'קדםיי'):
                            ex = {'ד': 'of Hashem', 'ו': 'and Hashem', 'ל': 'to Hashem', 'מ': 'from Hashem'}.get(key(words[s])[0], 'Hashem') if key(words[s]) != 'יי' else 'Hashem'
                    lines.append(f"{' '.join(words[s:e])} | {ex or '?'}"); tot += 1
        open(HERE + f'/lit/{pid}.auto.txt', 'w', encoding='utf8').write('\n'.join(lines) + '\n')
    print('lit_auto:', tot, 'rows')

if __name__ == '__main__': run()
