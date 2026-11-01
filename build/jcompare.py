# Compare our Sefaria-API Jastrow entries with the 2018 Sefaria-Data XML, entry by entry (same ids).
import json, re, unicodedata, difflib, collections, html
SP='/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
API={}
for f in ['jastrow-lookups.json','jastrow-lookups-2.json']:
    API.update(json.load(open(SP+'jastrow/'+f))['entries'])
X={}
for m in re.finditer(r'<entry id="([^"]+)">(.*?)</entry>', open(SP+'jastrow/full/Jastrow-full-2017.xml',encoding='utf8').read(), re.S):
    X[m.group(1)]=m.group(2)
SUP=str.maketrans({'ᵃ':'a','ᵇ':'b','ᶜ':'c','ᵈ':'d','׳':"'",'״':'"','’':"'",'‘':"'",'“':'"','”':'"'})
NIQ=re.compile(r'[֑-ׇ]')
def norm(s, niqqud=True):
    s=html.unescape(re.sub(r'<sup>(.*?)</sup>',r'\1',s)); s=re.sub(r'<[^>]+>',' ',s)
    s=unicodedata.normalize('NFD',s).translate(SUP)
    s=re.sub('ֹו','וֹ',s)          # holam written before vav
    s=unicodedata.normalize('NFC',s)
    if not niqqud: s=NIQ.sub('',s)
    s=re.sub(r'\s+([,.;:)\]])',r'\1',s); s=re.sub(r'([(\[])\s+',r'\1',s)
    return re.sub(r'\s+',' ',s).strip()
def apitext(e):
    out=[]
    def walk(o):
        if isinstance(o,str): out.append(o)
        elif isinstance(o,list): [walk(x) for x in o]
        elif isinstance(o,dict):
            for k,v in o.items():
                if k=='morphology': continue
                walk(v)
    out.append(e.get('language_code','') or ''); out.append(e.get('language_reference','') or '')
    walk(e.get('content',{}))
    return ' '.join(out)
def xmltext(x):
    x=re.sub(r'<(head-word|hw-number|alt-head-word|pos)>.*?</\1>','',x,flags=re.S)
    return x
res=collections.Counter(); rows=[]
for rid,e in API.items():
    if rid not in X: res['not in 2018 file']+=1; rows.append((rid,'missing',0,'','')); continue
    a=norm(apitext(e)); b=norm(xmltext(X[rid]))
    if a.replace(' ','')==b.replace(' ',''): res['identical']+=1; continue
    if norm(apitext(e),False).replace(' ','')==norm(xmltext(X[rid]),False).replace(' ',''): res['niqqud only']+=1; rows.append((rid,'niqqud',1,a,b)); continue
    ta,tb=list(a.replace(' ','')),list(b.replace(' ',''))
    if sorted(ta)==sorted(tb): res['same words, other order']+=1; rows.append((rid,'order',1,a,b)); continue
    r=difflib.SequenceMatcher(None,ta,tb,autojunk=False).ratio()
    res['differs']+=1; rows.append((rid,'diff',r,a,b))
print(len(API),'entries we have;',len(X),'in the 2018 file'); print(res)
json.dump(rows,open(SP+'jcmp/rows.json','w'),ensure_ascii=False)

# ---- second pass: ignore sense numbers, binyan labels, punctuation and transliteration accents
BIN=r'(?:Nithpa|Hithpa|Ithpa|Ithpe|Ittaf|Nithpe|Hithpo|Pilp|Polel|Pa|Pi|Pu|Af|Hif|Hof|Nif|Shaf|Pe|Kal)\.'
def core(s):
    s=re.sub(r'—?\s*\d{1,2}\)','',s); s=re.sub(BIN,'',s)
    s=unicodedata.normalize('NFD',s); s=re.sub(r'[̀-ͯ]','',s)   # ă ã ḥ → a a h
    return re.sub(r'[\s,.;:—\-()\[\]\'"*]','',s)
res2=collections.Counter(); left=[]
for r in rows:
    if r[1]=='missing': continue
    a,b=core(r[3]),core(r[4])
    if a==b: res2['same apart from layout']+=1; continue
    rr=difflib.SequenceMatcher(None,a,b,autojunk=False)
    left.append((r[0],round(rr.ratio(),3),[(op,a[i1:i2],b[j1:j2]) for op,i1,i2,j1,j2 in rr.get_opcodes() if op!='equal'],r[3],r[4]))
    res2['still differ']+=1
print('of the non-identical:',res2)
json.dump(left,open(SP+'jcmp/left.json','w'),ensure_ascii=False)
