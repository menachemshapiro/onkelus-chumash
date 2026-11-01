import json,random,glob,re,sys
SP='/home/claude/work/'
M=json.load(open(SP+'build/jas-map.json')); E=json.load(open(SP+'jastrow/jastrow-lookups.json'))['entries']
lex={}
for f in glob.glob(SP+'g/*.json'):
    for k,v in json.load(open(f))['lex'].items(): lex.setdefault(k,v)
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 3)
for k in random.sample(sorted(M),40):
    m=M[k]; e=E[m['rid']]; d=re.sub('<[^>]+>','',(e.get('language_reference') or '')+' '+json.dumps(e['content'],ensure_ascii=False))[:90]
    print(m['kind'][0],lex[k]['h'],'|',lex[k]['g'][:28],'=>',e['headword'],'|',d)
