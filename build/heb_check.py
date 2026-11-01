"""heb_check.py : every Hebrew pasuk on the page must match the Sefaria source (Tanach with Ta'amei Hamikra) letter for letter,
vowel for vowel and mark for mark. Only the petucha/setuma signs and line splits may differ. Prints any difference; exit 1 if any."""
import json, glob, re, sys, unicodedata as u, collections
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
U = '/root/.claude/uploads/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/'
order = re.findall(r'"(\w+)": \[', re.search(r'\{"bereishit": \[\d[^}]*\}', open(SP + 'bereishit-onkelos.html', encoding='utf8').read()).group(0))
BOOK, bk = {}, 'Genesis'
for p in order:
    bk = {'shemot': 'Exodus', 'vayikra': 'Leviticus', 'bamidbar': 'Numbers', 'devarim': 'Deuteronomy'}.get(p, bk); BOOK[p] = bk
SRC = {}
for b in set(BOOK.values()):
    d = json.load(open(glob.glob(U + f'*-{b}_-_he_-_Tanach_with_Ta_amei_Hamikra.json')[0], encoding='utf8'))
    SRC[b] = d['versions'][0]['text'] if 'versions' in d else d['text']
def norm(s):
    s = re.sub(r'<[^>]+>', '', s); s = re.sub(r'\s*׀\s*', ' ', s); s = re.sub(r'\{[^}]*\}|\((?:פ|ס)\)|&nbsp;|&thinsp;', ' ', s)
    return u.normalize('NFC', re.sub(r'\s+', ' ', s).strip())
bad = []
for f in sorted(glob.glob(SP + 'p/*.json')):
    pid = f.split('/')[-1][:-5]
    for v in json.load(open(f, encoding='utf8'))['V']:
        a, b = norm(' '.join(v['h'])), norm(SRC[BOOK[pid]][v['c'] - 1][v['v'] - 1])
        if a != b:
            wa, wb = a.split(' '), b.split(' ')
            diff = [(x, y) for x, y in zip(wa, wb) if x != y][:3] or [('(length)', f'{len(wa)} vs {len(wb)} words')]
            bad.append((pid, v['c'], v['v'], diff))
for p, c, v, d in bad[:40]: print(p, f'{c}:{v}', ' | '.join(f'ours {x}  source {y}' for x, y in d))
print(len(bad), 'pesukim differ from the source')
sys.exit(1 if bad else 0)
