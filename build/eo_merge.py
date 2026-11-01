"""Add the Onkelos-only English (build/eo/<parsha>.json) to the parsha data files (p/<parsha>.json) as field 'eo'.
Run after build_page.py; build_page.py also calls it. Checks that every entry has one string per clause."""
import json, os, glob
import tg_hl
HERE = os.path.dirname(os.path.abspath(__file__)); SP = os.path.dirname(HERE) + '/'
def merge(verbose=True):
    n = 0
    for pf in sorted(glob.glob(SP + 'p/*.json')):
        pid = os.path.basename(pf)[:-5]
        src = HERE + f'/eo/{pid}.json'
        d = json.load(open(pf, encoding='utf8'))
        eo = json.load(open(src, encoding='utf8')) if os.path.exists(src) else {}
        asrc = src[:-5] + '.align.json'
        al = json.load(open(asrc, encoding='utf8')) if os.path.exists(asrc) else {}
        changed = False
        for v in d['V']:
            k = f"{v['c']}:{v['v']}"
            new = eo.get(k)
            if new is not None:
                if len(new) != len(v['e']): raise SystemExit(f'{pid} {k}: {len(new)} clauses in eo, {len(v["e"])} on the page')
                if v.get('eo') != new: v['eo'] = new; changed = True
                n += 1
            elif 'eo' in v: del v['eo']; changed = True
            a = al.get(k)   # word-by-word match behind it, with notes ('ea')
            if a is not None and v.get('ea') != a: v['ea'] = a; changed = True
            elif a is None and 'ea' in v: del v['ea']; changed = True
            if (pid, v['c']) in tg_hl.CHAPTERS and a and v.get('eo'):   # Targum highlights where the source has none
                for j, cl in enumerate(a):
                    if not cl: continue
                    t = tg_hl.apply(v['t'][j], tg_hl.marks(v['eo'][j], cl['map']))
                    if t is not None and t != v['t'][j]: v['t'][j] = t; changed = True
        if changed: json.dump(d, open(pf, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    if verbose: print('eo: ', n, 'pesukim with Onkelos-only English')
if __name__ == '__main__': merge()
