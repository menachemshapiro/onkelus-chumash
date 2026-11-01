"""make_fetch_all.py : write jastrow/fetch_jastrow_all.py, which downloads Sefaria's current text for every
Jastrow entry in the 2018 copy (32,512) that we have not downloaded yet, to complete our copy of the dictionary."""
import json, re, os
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
F = json.load(open(SP + 'jastrow/jastrow-2018.json', encoding='utf8'))
API = {}
for f in ['jastrow-extra.json', 'jastrow-lookups.json', 'jastrow-lookups-2.json', 'jastrow-lookups-3.json', 'jastrow-pages.json', 'jastrow-all.json']:
    if os.path.exists(SP + 'jastrow/' + f):
        d = json.load(open(SP + 'jastrow/' + f, encoding='utf8')); API.update(d['entries']); API.update(d.get('pages', {}))
def q(h): return re.sub(r'\s+([IVX]+|[¹²³⁴⁵])$', '', h.strip().lstrip('*')).strip()
def nb(r, s): return r[0] + '%05d' % (int(r[1:]) + s)
WANT, NAMES = {}, {}
for r in sorted(F):
    if r in API: continue
    hs = [F[r]['headword']] + F[r].get('alt_headwords', [])
    qs = list(dict.fromkeys(q(h) for h in hs if "'" not in h and '׳' not in h and q(h)))
    ns = list(dict.fromkeys(x for h in hs[:1] for x in (h.replace("'", '׳'), h.replace("'", '׳').lstrip('*'))))
    WANT[r] = {'q': qs[:3], 'n': ns}
    kn = []
    a, b = API.get(nb(r, -1)), API.get(nb(r, 1))
    if a and a.get('next_hw'): kn.append(a['next_hw'])
    if b and b.get('prev_hw'): kn.append(b['prev_hw'])
    if kn: NAMES[r] = list(dict.fromkeys(kn))
tpl = open(SP + 'build/fetch_all_template.py', encoding='utf8').read()
tpl = tpl.replace('__N__', f'{len(WANT):,}').replace('__WANT__', json.dumps(WANT, ensure_ascii=False, separators=(',', ':')).replace('},"', '},\n"'))
tpl = tpl.replace('__NAMES__', json.dumps(NAMES, ensure_ascii=False, separators=(',', ':')).replace('],"', '],\n"'))
open(SP + 'jastrow/fetch_jastrow_all.py', 'w', encoding='utf8').write(tpl)
print(len(F), 'in the 2018 copy;', len(API), 'downloaded;', len(WANT), 'to download;', len(NAMES), 'with a known page name;',
      len({w['q'][0] for w in WANT.values() if w['q']}), 'distinct first searches;', sum(1 for w in WANT.values() if not w['q']), 'page name only')
