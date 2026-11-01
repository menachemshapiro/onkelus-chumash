import json,glob,re,collections,unicodedata as u
N=lambda s:u.normalize('NFC',s)
c=collections.Counter(); miss=collections.Counter(); par=collections.Counter()
for f in glob.glob('/home/claude/work/p/*.json'):
    pid=f.split('/')[-1][:-5]; g=json.load(open(f'/home/claude/work/g/{pid}.json'))
    for v in json.load(open(f))['V']:
        at=g['at'].get(f"{v['c']}:{v['v']}",{})
        for line in v['t']:
            for w in re.sub(r'<[^>]+>|\([^)]*\)|[:׃,.;]',' ',line).split():
                fm=at.get(N(w)) or g['forms'].get(N(w))
                c['words']+=1
                if not fm: miss[w]+=1
                else:
                    for m in re.findall(r'\(([^)]*)\)',fm['here']): par[re.sub(r'\s.*','',m)]+=1
print(c, 'missing',sum(miss.values()),miss.most_common(10)); print(par.most_common(30))
