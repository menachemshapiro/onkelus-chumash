"""jas_abbr.py : Jastrow's "List of Abbreviations" (front of the dictionary; Sefaria: Jastrow, List of Abbreviations),
from the 2018 Sefaria-Data XML -> j/abbr.json {"en": [[abbr, meaning], ...]}. The pop-up loads it the first time an entry is opened.
Also Jastrow's "Hebrew or Aramaic Abbreviations" list (he) and a few pairs read as one (x: h. text, i.e., e.g., h. a. ch.).
ADDED (common ones missing from the list) is kept here for review only (abbr-review.md lists what the entries use that the list lacks)."""
import re, json, html, os
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
X = open(SP + 'jastrow/full/Jastrow-full-2017.xml', encoding='utf8').read()
front = X[:X.index('<body>')]
he_start = front.index('Hebrew or Aramaic Abbreviations'); en_start = front.index('List of Abbreviations.')
def items(block):
    out = []
    for p in re.findall(r'<p>(.*?)</p>', block, re.S):
        p = re.sub(r'<pgbrk[^>]*/>', '', p)
        p = re.sub(r'<italic>(.*?)</italic>', r'<i>\1</i>', p, flags=re.S)
        p = re.sub(r'<sup>(.*?)</sup>', r'<sup>\1</sup>', p, flags=re.S)
        p = re.sub(r'<(?!/?(?:i|sup)>)[^>]+>', '', p)
        p = html.unescape(re.sub(r'\s+', ' ', p)).strip()
        if ' = ' not in p: continue
        a, m = p.split(' = ', 1)
        out.append([a.strip(), m.strip()])
    return out
HE = items(front[he_start:en_start]); EN = items(front[en_start:])
# Sefaria's current text of both lists (jastrow/fetch_abbr_list.py, Oct 22) wins: same items, a few small corrections (ă for ã)
def sef(lines):
    out = []
    for l in lines:
        l = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<(?!/?(?:i|sup)>)[^>]+>', '', l))).strip()
        if ' = ' in l: a, m = l.split(' = ', 1); out.append([a.strip(), m.strip().rstrip('`')])
    return out
if os.path.exists(SP + 'jastrow/jastrow-abbr-list.json'):
    _S = json.load(open(SP + 'jastrow/jastrow-abbr-list.json', encoding='utf8'))
    EN = sef(_S['Jastrow, List of Abbreviations']['versions'][0]['text']); HE = sef(_S['Jastrow, Hebrew or Aramaic Abbreviations']['versions'][0]['text'])
# common in the entries but not in Jastrow's list; shown in the pop-up marked as added here
ADDED = [['Ib.', 'ibidem, in the same place (the book or passage just cited)'], ['m.', 'masculine'], ['f.', 'feminine'], ['fem.', 'feminine'],
    ['h. text', 'Hebrew text (of the Bible verse the Targum translates)'], ['Part.', 'participle'], ['i. e.', 'id est, that is'],
    ['e. g.', 'exempli gratia, for example'], ['sq.', 'sequens, and the following'], ['pass.', 'passive'], ['p.', 'page'],
    ['Pe.', 'Peal'], ['Pa.', 'Pael'], ['Af.', 'Afel'], ['Hof.', 'Hofal'], ['constr.', 'construct state'], ['supra', 'above'], ['infra', 'below'],
    ['Esp.', 'especially'], ['wds.', 'words'], ['quot.', 'quoted'], ['Denom.', 'denominative (formed from a noun)'], ['Chald.', 'Chaldaic (Aramaic)'],
    ['corresp.', 'corresponding'], ['sing.', 'singular'], ['incorr.', 'incorrect, incorrectly'], ['Hebr.', 'Hebrew'], ['Syr.', 'Syriac'],
    ['Arab.', 'Arabic'], ['interch.', 'interchanged, interchangeable'], ['euphem.', 'euphemism, euphemistically'], ['neut.', 'neuter'],
    ['perh.', 'perhaps'], ['Mss.', 'manuscripts'], ['interpret.', 'interpretation'], ['abbr.', 'abbreviation'], ['Dict.', 'Dictionary'],
    ['trnsf.', 'transferred (used figuratively)'], ['sec.', 'second'], ['Bub.', 'Buber’s edition'], ['Amst.', 'Amsterdam edition'],
    ['Krot.', 'Krotoschin edition (of the Y’rushalmi)'], ['Lag.', 'Lagarde’s edition (of the Targumim)'], ['Chr.', 'Chronicles'], ['Ezek.', 'Ezekiel']]
have = {a for a, m in EN}; ADDED = [x for x in ADDED if x[0] not in have]
PAIRS = [['h. text', 'Hebrew text (of the Bible verse the Targum translates)'], ['h. a. ch.', 'Hebrew and Chaldaic (Aramaic)'],
         ['i. e.', 'id est, that is'], ['i.e.', 'id est, that is'], ['e. g.', 'exempli gratia, for example'], ['e.g.', 'exempli gratia, for example']]
json.dump({'en': EN, 'he': HE, 'x': PAIRS}, open(SP + 'j/abbr.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
print(len(HE), 'Hebrew/Aramaic,', len(EN), 'English abbreviations,', len(ADDED), 'added')
