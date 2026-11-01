"""make_fetch3.py : list every Jastrow entry the site uses (jastrow/entries-in-use.tsv) and write
jastrow/fetch_jastrow3.py, which downloads Sefaria's current text for the ones we only have from the 2018 copy."""
import json, glob, re, os
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
F = json.load(open(SP + 'jastrow/jastrow-2018.json', encoding='utf8'))
API = {}
for f in ['jastrow-all.json', 'jastrow-extra.json', 'jastrow-lookups.json', 'jastrow-lookups-2.json', 'jastrow-lookups-3.json', 'jastrow-pages.json']:
    if os.path.exists(SP + 'jastrow/' + f): API.update(json.load(open(SP + 'jastrow/' + f, encoding='utf8'))['entries'])
ix = json.load(open(SP + 'j/index.json', encoding='utf8'))
why = {}
for l, (rid, kind, also, tabs) in ix.items():
    why.setdefault(rid, 'matched to a glossary word')
    for r in also: why.setdefault(r, 'other possible entry')
    for r in tabs: why.setdefault(r, 'related-entry tab')
used = set()
for f in glob.glob(SP + 'j/[A-Z].json'): used |= set(json.load(open(f, encoding='utf8')))
rows = []
for r in sorted(used):
    src = 'sefaria' if r in API else '2018'
    rows.append((r, (API.get(r) or F[r])['headword'], src, why.get(r, 'linked from another entry')))
with open(SP + 'jastrow/entries-in-use.tsv', 'w', encoding='utf8') as fh:
    fh.write('rid\theadword\ttext from\twhy it is included\n' + '\n'.join('\t'.join(x) for x in rows) + '\n')
NOT = set(json.load(open(SP + 'jastrow/not-in-word-search.json'))) if os.path.exists(SP + 'jastrow/not-in-word-search.json') else set()   # the word search misses these; fetched by page name instead (jastrow-pages.json)
want = {r: [F[r]['headword']] + F[r].get('alt_headwords', []) for r, h, s, w in rows if s == '2018' and r not in NOT}
def q(h): return re.sub(r'\s+[IVX]+$', '', h.strip().lstrip('*')).strip()
WANT = {r: [q(h) for h in hs if "'" not in h and '׳' not in h and q(h)] for r, hs in want.items()}
tpl = open(SP + 'build/fetch3_template.py', encoding='utf8').read()
tpl = tpl.replace('__N__', str(len(WANT))).replace('__WANT__', json.dumps(WANT, ensure_ascii=False, indent=0))
open(SP + 'jastrow/fetch_jastrow3.py', 'w', encoding='utf8').write(tpl)
print(len(rows), 'entries in use;', sum(1 for x in rows if x[2] == 'sefaria'), 'with Sefaria text;', len(WANT), 'to download;',
      len({h for hs in WANT.values() for h in hs[:1]}), 'first lookups')
