"""jas_pages.py : turn Jastrow entries fetched by page name (raw Sefaria text, from fetch_jastrow5/6 and fetch_jastrow_all)
into the same shape as the word-search entries, and add them to jastrow/jastrow-pages.json.
Usage: python3 build/jas_pages.py FILE.json   (FILE: {"pages": {rid: {"name", "text"}}} or the pages-5/6 format)"""
import json, re, sys
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
def convert(rid, t):
    t = ' '.join(t) if isinstance(t, list) else t
    m = re.match(r'\s*<strong[^>]*>(.*?)</strong>', t)
    hw = re.sub('<[^>]+>', '', m.group(1)).strip() if m else rid
    if m: t = t[m.end():]
    t = t.replace('&nbsp;', ' ')
    t = re.sub(r'<strong dir="rtl">\s*</strong>', '', t)
    t = re.sub(r'<strong dir="rtl">(.*?)</strong>', r'<b><span dir="rtl">\1</span></b>', t)
    t = re.sub(r'<(/?)strong>', r'<\1b>', t)
    parts = [re.sub(r'\s+', ' ', p).rstrip() for p in re.split(r'<br\s*/?>', t)]
    return {'headword': hw, 'rid': rid, 'content': {'senses': [{'definition': ' ' + p.strip(' ,')} for p in parts if p.strip(' ,')]}}
if __name__ == '__main__':
    src = json.load(open(sys.argv[1], encoding='utf8'))
    J = json.load(open(SP + 'jastrow/jastrow-pages.json', encoding='utf8'))
    n = 0
    for rid, v in src.get('pages', {}).items():
        if v.get('text'): J['entries'][rid] = convert(rid, v['text']); n += 1
    json.dump(J, open(SP + 'jastrow/jastrow-pages.json', 'w', encoding='utf8'), ensure_ascii=False)
    print(n, 'converted;', len(J['entries']), 'in jastrow-pages.json')
