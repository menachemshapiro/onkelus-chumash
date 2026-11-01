"""lit_merge.py : add the exact (literal) English to the Onkelos word-by-word table, from build/lit/<parsha>.txt.

File format:  "@ c:v.clause"  then one line per Aramaic word, or per group of words read together:
    Aramaic | exact English
The groups must cover the clause's Aramaic words in order (the same words as the word-by-word match, v['ea']).
Writes v['el'][clause] = [[number of Aramaic words, exact English, English used in the translation (absent if none)], ...]
into p/<parsha>.json (the page takes the Aramaic words from the clause itself).
The page shows the exact English, with the English used in parentheses when it is different. A clause with no
word-by-word match (no Onkelos change to the English) is split into the Targum's own words, and has no "English used" (null).
"Hashem" in the exact English stands for the Divine Name: it is shown the way the translation writes it (Adonoy, my Master ...).
Run after eo_merge.py (eo_merge.py calls it)."""
import json, os, re, glob, sys, unicodedata as u
HERE = os.path.dirname(os.path.abspath(__file__)); SP = os.path.dirname(HERE) + '/'
N = lambda s: u.normalize('NFC', s)
NAME = r'Adonoy|[Mm]y Master|the Lord|LORD|Hashem|Elohim'

def read(fn):
    out, cur = {}, None
    for ln in open(fn, encoding='utf8'):
        ln = ln.rstrip('\n')
        if not ln.strip() or ln.startswith('#'): continue
        if ln.startswith('@ '): cur = ln[2:].strip(); out[cur] = []; continue
        a, e = [x.strip() for x in ln.split('|', 1)]
        out[cur].append((N(a), e))
    return out

def merge(verbose=True):
    n = 0
    for pf in sorted(glob.glob(SP + 'p/*.json')):
        pid = os.path.basename(pf)[:-5]; src = HERE + f'/lit/{pid}.txt'
        d = json.load(open(pf, encoding='utf8'))
        L = read(HERE + f'/lit/{pid}.auto.txt') if os.path.exists(HERE + f'/lit/{pid}.auto.txt') else {}   # draft from the glossary
        if os.path.exists(src): L.update(read(src))                                                     # hand-written wins
        changed = False
        for v in d['V']:
            el = None
            for j in range(len(v['t'])):
                key = f"{v['c']}:{v['v']}.{j}"
                if key not in L: continue
                a = (v.get('ea') or [None] * len(v['t']))[j]
                if a:
                    words = [N(w) for ar, en in a['map'] for w in ar.split()]
                    owner = [k for k, (ar, en) in enumerate(a['map']) for w in ar.split()]
                else:   # the Targum's own words, as the page's word-by-word table splits them
                    words = [N(w) for w in re.sub(r'<[^>]+>|\([^)]*\)|[:׃,.;]', ' ', v['t'][j]).split()]
                    owner = None
                eng = re.sub(r'<[^>]+>', '', (v.get('eo') or v['e'])[j])
                name = (re.search(NAME, eng) or [None])[0] or 'Adonoy'
                rows, i = [], 0
                for ar, ex in L[key]:
                    ws = ar.split()
                    if words[i:i + len(ws)] != ws:
                        raise SystemExit(f'{pid} {key}: "{ar}" does not match the next words "{" ".join(words[i:i + len(ws)])}"')
                    if owner is None: used = None
                    else:
                        used, part = [], False
                        for k in dict.fromkeys(owner[i:i + len(ws)]):
                            e = a['map'][k][1]
                            first = owner.index(k)
                            if first < i: part = True; continue          # this row's English was given with the words before
                            if e and e not in used: used.append(e)
                        used = None if part and not used else ' '.join(used)
                    if 'Hashem' in ex:   # the Divine Name as the translation writes it
                        nm = (re.search(NAME, used or '') or [None])[0] or name
                        ex = ex.replace('Hashem', nm[0].lower() + nm[1:] if nm.startswith('My ') and not ex.startswith('Hashem') else nm)
                    rows.append([len(ws), ex] + ([] if used is None else [used])); i += len(ws)   # word count, exact English, English used
                if i != len(words): raise SystemExit(f'{pid} {key}: words left over: {" ".join(words[i:])}')
                el = el or [None] * len(v['t']); el[j] = rows; n += 1
            if el != v.get('el'):
                if el: v['el'] = el
                else: v.pop('el', None)
                changed = True
        if changed: json.dump(d, open(pf, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    if verbose: print('lit:', n, 'clauses with exact English')

if __name__ == '__main__': merge()
