"""eo_check.py ALIGNFILE PARSHA : check a word-by-word alignment for "as Onkelos reads it" and write build/eo/<parsha>.json.
For every clause it checks that
  1. the Aramaic words listed are exactly the Targum clause's words, in order (alternate readings in parentheses are skipped);
  2. every English word of the new clause is accounted for: by an Aramaic word's translation or a "+" line;
  3. English words outside <b>…</b> were already in Metsudah's English for that clause (so nothing of Metsudah's is invented),
     and Metsudah's words that are dropped are listed, so a reviewer sees what was removed."""
import json, re, sys, unicodedata as u
from collections import Counter
N = lambda s: u.normalize('NFC', s)
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
path, pid = sys.argv[1], sys.argv[2]
P = {f"{v['c']}:{v['v']}": v for v in json.load(open(SP + f'p/{pid}.json', encoding='utf8'))['V']}
def aram_tokens(t):
    t = re.sub(r'<[^>]+>', '', t); t = re.sub(r'\([^)]*\)', ' ', t)
    return [N(w).strip(':.,;') for w in t.replace('־', ' ').split() if re.search('[א-ת]', w)]
def en_words(s):
    s = re.sub(r'<[^>]+>', '', s).replace('—', ' ').replace('…', ' ')
    return [w.lower().strip("’'") for w in re.findall(r"[A-Za-z’']+", s) if w.strip("’'")]
def bare(s): return re.sub(r'\{[^}]*\}', ' ', re.sub(r'<b>.*?</b>', ' ', s))
verses, cur, problems_early = {}, None, []
for line in open(path, encoding='utf8'):
    line = line.rstrip('\n')
    if not line.strip() or line.startswith('#'): continue
    if line.startswith('@ '): cur = line[2:].strip(); verses[cur] = []; continue
    if line == '= same': verses[cur].append(None); continue
    if line.startswith('E: '): verses[cur].append({'E': line[3:], 'map': [], 'plus': [], 'notes': []}); continue
    cl = verses[cur][-1]
    if line.startswith('M: '):
        segs = [x.strip() for x in line[3:].split('|')]
        k = len(verses[cur]) - 1
        toks = aram_tokens(P[cur]['t'][k]) if cur in P and k < len(P[cur]['t']) else []
        if len(segs) != len(toks): problems_early.append(f'{cur} clause {k+1}: {len(segs)} English pieces for {len(toks)} Aramaic words: {" ".join(toks)}'); continue
        for t, e in zip(toks, segs):
            if e == '^' and cl['map']: a0, e0 = cl['map'][-1]; cl['map'][-1] = (a0 + ' ' + t, e0)
            else: cl['map'].append((t, '' if e == '-' else e))
        continue
    if line.startswith('+'): cl['plus'].append(line[1:].strip())
    elif line.startswith('!'): cl['notes'].append(line[1:].strip())
    else:
        a, _, e = line.partition('='); cl['map'].append((N(a.strip()), e.strip()))
out, problems, report, align = {}, list(problems_early), [], {}
for cv, cls in verses.items():
    v = P[cv]
    while len(cls) < len(v['e']): cls.append(None)   # clauses not written out at the end are unchanged
    if len(cls) != len(v['e']): problems.append(f'{cv}: {len(cls)} clauses written, page has {len(v["e"])}'); continue
    eo = []
    for j, cl in enumerate(cls):
        if cl is None: eo.append(v['e'][j]); continue
        want = aram_tokens(v['t'][j]); got = [w for a, _ in cl['map'] for w in a.split()]
        if want != got: problems.append(f'{cv} clause {j+1}: Aramaic words\n    page: {" ".join(want)}\n    map:  {" ".join(got)}')
        have = Counter(en_words(cl['E']))
        acc = Counter(w for _, e in cl['map'] for w in en_words(e)) + Counter(w for p in cl['plus'] for w in en_words(p))
        if have - acc: problems.append(f'{cv} clause {j+1}: English words not accounted for: {" ".join(sorted((have - acc).elements()))}')
        if acc - have: problems.append(f'{cv} clause {j+1}: listed but not in the English: {" ".join(sorted((acc - have).elements()))}')
        kept, orig = Counter(en_words(bare(cl['E']))), Counter(en_words(re.sub(r'\[<b>.*?</b>\]', ' ', v['e'][j])))
        if kept - orig: problems.append(f'{cv} clause {j+1}: unmarked English not in Metsudah: {" ".join(sorted((kept - orig).elements()))} (mark Onkelos wording with <b>, added words with {{}})')
        for a in re.findall(r'\{([^}]*)\}', cl['E']):
            if not any(a.strip() in p for p in cl['plus']) and not any(a.strip() in e for _, e in cl['map']): problems.append(f'{cv} clause {j+1}: added word {{{a}}} is not listed')
        dropped = orig - kept
        report.append((cv, j + 1, v['e'][j], cl['E'], ' '.join(sorted(dropped.elements())), cl['notes']))
        eo.append(cl['E'])
    out[cv] = eo
    align[cv] = [None if cl is None else {'map': [[a, e] for a, e in cl['map']], 'plus': [x for x in cl['plus'] if x], 'notes': cl['notes']} for cl in cls]
print(f'{len(verses)} pesukim, {sum(1 for c in verses.values() for x in c if x)} clauses changed')
for p in problems: print('PROBLEM', p)
if not problems:
    import os
    dst = os.path.dirname(os.path.abspath(__file__)) + f'/eo/{pid}.json'
    old = json.load(open(dst, encoding='utf8')) if os.path.exists(dst) else {}
    old.update(out); json.dump(old, open(dst, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    adst = dst[:-5] + '.align.json'
    oa = json.load(open(adst, encoding='utf8')) if os.path.exists(adst) else {}
    oa.update(align); json.dump(oa, open(adst, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    json.dump(report, open(path.rsplit('.', 1)[0] + '.report.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print('written', dst)
