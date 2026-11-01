"""jas_2018.py : turn Sefaria-Data's 2018 Jastrow XML (jastrow/full/Jastrow-full-2017.xml, 32,512 entries)
into the same shape as the entries we download from Sefaria's API, so the build can fall back on it.
Writes jastrow/jastrow-2018.json {rid: entry} and jastrow/targ-o-cites.json [[rid, book, chapter, verse, onkelos_only]].
The 2018 text is used only where Sefaria's current text has not been downloaded (see jas_build.py)."""
import re, json, html, unicodedata as u
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
X = open(SP + 'jastrow/full/Jastrow-full-2017.xml', encoding='utf8').read()
BOOK = {'Gen': 'Genesis', 'Ex': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deut': 'Deuteronomy'}
ROM = {'I': 1, 'V': 5, 'X': 10, 'L': 50}
def rom(s):
    n = 0
    for i, ch in enumerate(s):
        v = ROM[ch]; n += -v if i + 1 < len(s) and ROM[s[i + 1]] > v else v
    return n
def fixheb(s):
    s = u.normalize('NFD', s)
    s = re.sub('ֹו', 'וֹ', s)          # the 2018 file writes holam before the vav (אֱגֹורָא)
    return u.normalize('NFC', s)
HEB = re.compile(r'([֐-׿][֐-׿\'"׳״ ]*[֐-׿\'׳]|[֐-׿])')
CITE = re.compile(r'Targ\.\s+(O\.\s+(?:a\.\s+Y\.\s+(?:I{1,2}\s+)?)?|Y\.\s+(?:I{1,2}\s+)?|)(?:(Gen|Ex|Lev|Num|Deut)\.\s+)([IVXL]+),\s*(\d+)')
CONT = re.compile(r'\s*(?:(?:,\s*sq\.)|(?:;\s*(?:a\.\s*(?:fr|e)\.)?))?\s*(?:;\s*|\s+Ib\.\s+(?:([IVXL]+),\s*)?)(\d+)\b')
CITES = []
def link_cites(t, rid):
    """wrap Onkelos citations ("Targ. O. Gen. XXV, 27", plain "Targ. Gen. …", and "Ib. …" after them) in Sefaria links"""
    out, pos = [], 0
    for m in CITE.finditer(t):
        tg, bk, ch, vs = m.group(1), m.group(2), rom(m.group(3)), int(m.group(4))
        onk = not tg.startswith('Y.')
        if not onk: continue
        out.append(t[pos:m.start()])
        out.append(f'<a href="/Onkelos_{BOOK[bk]}.{ch}.{vs}">{m.group(0)}</a>')
        CITES.append([rid, BOOK[bk], ch, vs, tg.startswith('O.')]); pos = m.end()
        while True:   # "; 30; 31" or "Ib. XLVI, 29" right after
            c = CONT.match(t, pos)
            if not c or c.end() - pos > 30: break
            if c.group(1): ch = rom(c.group(1))
            vs = int(c.group(2))
            if vs > 200: break
            seg = t[pos:c.end()]; num = re.search(r'\d+$', seg)
            out.append(seg[:num.start()] + f'<a href="/Onkelos_{BOOK[bk]}.{ch}.{vs}">{num.group(0)}</a>')
            CITES.append([rid, BOOK[bk], ch, vs, tg.startswith('O.')]); pos = c.end()
    out.append(t[pos:]); return ''.join(out)
def inline(x, rid):
    """XML fragment -> the HTML our build expects (i, b, sup, rtl spans, links)"""
    x = re.sub(r'<pgbrk[^>]*/>', '', x)
    x = re.sub(r'<xref rid="([^"]+)">(.*?)</xref>', lambda m: f'\x01{m.group(1)}\x02{m.group(2)}\x03', x, flags=re.S)
    x = re.sub(r'<(/?)italic>', r'<\1i>', x); x = re.sub(r'<(/?)bold>', r'<\1b>', x)
    x = re.sub(r'</?(plural-form|alternative|p|td|tr|table)[^>]*>', ' ', x)
    x = re.sub(r'<(?!/?(?:i|b|sup|sub)>)[^>]+>', '', x)
    x = fixheb(re.sub(r'\s+', ' ', x))
    x = link_cites(x, rid)
    # Hebrew runs in rtl spans, but not inside tags or the xref markers
    parts = re.split(r'(<[^>]+>|\x01[^\x02]*\x02|\x03)', x)
    x = ''.join(p if (p.startswith('<') or p.startswith('\x01') or p == '\x03') else HEB.sub(r'<span dir="rtl">\1</span>', p) for p in parts)
    x = re.sub(r'\x01([^\x02]*)\x02', r'<a dir="rtl" class="jx2018" data-r="\1">', x).replace('\x03', '</a>')
    return x.strip()
def senses(block, rid):
    out = []
    for m in re.finditer(r'<sense>(.*?)</sense>', block, re.S):
        s = m.group(1); d = {}
        n = re.search(r'<number>(.*?)</number>', s, re.S)
        if n: d['number'] = n.group(1).strip()
        body = ' '.join(re.findall(r'<(?:definition|notes)>(.*?)</(?:definition|notes)>', s, re.S))
        if body.strip(): d['definition'] = ' ' + inline(body, rid)
        if d: out.append(d)
    return out
E, prev = {}, None
for m in re.finditer(r'<entry id="([^"]+)">(.*?)</entry>', X, re.S):
    rid, x = m.group(1), m.group(2)
    hws = [fixheb(re.sub(r'<[^>]+>', '', h)).strip(' ,;') for h in re.findall(r'<head-word>(.*?)</head-word>', x, re.S)]
    hws = [h for h in hws if re.search(r'[\u05d0-\u05ea]', h)]
    num = re.search(r'<hw-number>(.*?)</hw-number>', x)
    hw = hws[0] + (' ' + num.group(1).strip() if num else '') if hws else rid
    e = {'headword': hw, 'alt_headwords': hws[1:], 'rid': rid, 'src': '2018'}
    lk = re.search(r'<language-key>(.*?)</language-key>', x, re.S)
    if lk: e['language_code'] = ' ' + lk.group(1).strip() + ' '
    lr = re.search(r'<language-reference>(.*?)</language-reference>', x, re.S)
    if lr: e['language_reference'] = inline(lr.group(1), rid)
    content = {}
    pos = re.search(r'<pos>(.*?)</pos>', x, re.S)
    if pos: content['morphology'] = re.sub(r'<[^>]+>', '', pos.group(1)).strip()
    main = re.sub(r'<binyan>.*?</binyan>', '', x, flags=re.S)
    ss = senses(main, rid)
    for b in re.finditer(r'<binyan>(.*?)</binyan>', x, re.S):
        bt = b.group(1)
        name = re.search(r'<binyan-name>(.*?)</binyan-name>', bt, re.S)
        forms = [fixheb(re.sub(r'<[^>]+>', '', f)).strip() for f in re.findall(r'<binyan-form>(.*?)</binyan-form>', bt, re.S)]
        ss.append({'grammar': {'verbal_stem': (name.group(1).strip() if name else ''), 'binyan_form': forms}, 'senses': senses(bt, rid)})
    content['senses'] = ss; e['content'] = content
    e['prev_hw'] = prev; prev = hw
    E[rid] = e
json.dump(E, open(SP + 'jastrow/jastrow-2018.json', 'w', encoding='utf8'), ensure_ascii=False)
json.dump(CITES, open(SP + 'jastrow/targ-o-cites.json', 'w', encoding='utf8'), ensure_ascii=False)
print(len(E), 'entries;', len(CITES), 'Onkelos citations in', len({c[0] for c in CITES}), 'entries')
