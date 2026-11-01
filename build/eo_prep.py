"""eo_prep.py PARSHA [c:v-c:v] : print, for every pasuk with Onkelos brackets, each clause's Aramaic words (numbered, with the
glossary meaning) and the English as printed, as the worksheet for writing eo-align/<parsha>.txt in the M: format."""
import json, re, sys, runpy, unicodedata as u
N = lambda s: u.normalize('NFC', s)
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
sys.argv, ARGS = ['gloss_build.py', 'todo', 'none'], sys.argv[1:]
G = runpy.run_path('gloss_build.py', run_name='bt')
pid = ARGS[0]; rng = ARGS[1] if len(ARGS) > 1 else None
V = json.load(open(SP + f'p/{pid}.json', encoding='utf8'))['V']
def aram_tokens(t):
    t = re.sub(r'<[^>]+>', '', t); t = re.sub(r'\([^)]*\)', ' ', t)
    return [N(w).strip(':.,;') for w in t.replace('־', ' ').split() if re.search('[א-ת]', w)]
key = lambda s: tuple(map(int, s.split(':')))
for v in V:
    if rng:
        a, b = rng.split('-')
        if not (key(a) <= (v['c'], v['v']) <= key(b)): continue
    if not any('[<b>' in e for e in v['e']): continue
    print(f"@ {v['c']}:{v['v']}")
    prev = None
    for j, (t, e) in enumerate(zip(v['t'], v['e'])):
        toks = aram_tokens(t)
        gl = []
        for w in toks:
            g, _ = G['lookup'](w, v['c'], v['v'], pid, prev); prev = w
            h = re.sub(r'\s*\((?:Hebrew|Onkelos)[^)]*\)|\s*\([^)]*=[^)]*\)', '', g['here']) if g else '?'
            gl.append(f'{w}={h}')
        mark = '*' if '[<b>' in e else ' '
        if mark == '*' or '<b>' in t: print(f" {mark}{j+1} T: " + ' · '.join(gl) + (f"  [{len(toks)}]"))
        else: print(f"  {j+1} T: " + ' '.join(toks))
        print(f"    E: {e.replace('<b>', '{').replace('</b>', '}')}")
