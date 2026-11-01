"""abbr_review.py : abbreviations the pop-up entries use that are not in Jastrow's List of Abbreviations -> abbr-review.md"""
import json, glob, re, html, collections, unicodedata as u
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
exec(open(SP + 'build/jas_abbr.py').read().split("json.dump(")[0])     # HE, EN, ADDED
J = {}
for f in glob.glob(SP + 'j/[A-Z].json'): J.update(json.load(open(f, encoding='utf8')))
listed = {a for a, m in EN}
lower = {a.lower(): a for a in listed}
rx = re.compile(r"(?<![A-Za-zÀ-ɏḀ-ỿ̀-ͯ’'&])(?:" + '|'.join(re.escape(a).replace(r'\ ', r'\s+') for a in sorted(listed, key=len, reverse=True)) + r")(?![A-Za-zÀ-ɏḀ-ỿ̀-ͯ])")
ADD = dict(ADDED); ADD.update({'supra.': 'above', 'infra.': 'below', 'ab.': 'above (as ab. = as above)', 'gen.': 'general (in gen.)',
  'ibid.': 'ibidem, in the same place', 'Ibid.': 'ibidem, in the same place', 'ib.': 'ibidem, in the same place', 'etc.': 'et cetera',
  'Pilp.': 'Pilpel', 'Palp.': 'Palpel', 'Ithpalp.': 'Ithpalpal', 'Hithpalp.': 'Hithpalpel', 'Shaf.': 'Shafel', 'Saf.': 'Safel', 'Ittaf.': 'Ittafal',
  'Pu.': 'Pual', 'Polel.': 'Polel', 'Hithpol.': 'Hithpolel', 'Ithpol.': 'Ithpolel', 'Dithpe.': 'Dithpeel', 'Pesh.': 'Peshitta (Syriac Bible)',
  'Pers.': 'Persian', 'Gr.': 'Greek', 'Assyr.': 'Assyrian', 'Lat.': 'Latin', 'Engl.': 'English', 'masc.': 'masculine', 'accus.': 'accusative',
  'infin.': 'infinitive', 'inf.': 'infinitive', 'Inf.': 'infinitive', 'imperat.': 'imperative', 'imper.': 'imperative', 'perf.': 'perfect',
  'Perf.': 'perfect', 'fut.': 'future', 'impf.': 'imperfect', 'suff.': 'suffix', 'conj.': 'conjunction', 'interj.': 'interjection',
  'interrog.': 'interrogative', 'plur.': 'plural', 'redupl.': 'reduplicated, reduplication', 'reduplic.': 'reduplicated, reduplication',
  'transpos.': 'transposed, transposition', 'transp.': 'transposed, transposition', 'transl.': 'translation, translated', 'etymol.': 'etymology',
  'deriv.': 'derived, derivation', 'Deriv.': 'derived, derivation', 'homilet.': 'homiletic, homiletically', 'lect.': 'lectio, reading',
  'marg.': 'margin', 'vv.': 'verses', 'cit.': 'cited', 'orig.': 'original, originally', 'tradit.': 'tradition, traditional', 'relat.': 'relative',
  'apocop.': 'apocopated', 'Metaph.': 'metaphor, metaphorically', 'Mishn.': 'Mishnah', 'Geogr.': 'geography, geographical', 'frequ.': 'frequently',
  'Frequ.': 'frequently', 'Euphem.': 'euphemism, euphemistically', 'Transf.': 'transferred (used figuratively)', 'denomin.': 'denominative',
  'Perh.': 'perhaps', 'hebr.': 'Hebrew', 'pp.': 'pages', 'anoth.': 'another', 'Eduy.': 'ʿEduyoth (Mishnah and Tosefta)', 'Meïl.': 'M’ilah (Talmud)',
  'Kerith.': 'K’rithoth (Talmud)', 'Thazr.': 'Thazria (a pericope)', 'K’dosh.': 'K’doshim (a pericope)', 'B’midb.': 'B’midbar (a pericope)',
  'Vayishl.': 'Vayishlaḥ (a pericope)', 'Vayigg.': 'Vayiggash (a pericope)', 'Haăz.': 'Haăzinu (a pericope)', 'Rashb.': 'Rashbam',
  'Bxt.': 'Buxtorf (Lexicon Chaldaicum)', 'Buxt.': 'Buxtorf (Lexicon Chaldaicum)', 'Oxf.': 'Oxford (manuscript or edition)', 'Leipz.': 'Leipzig'}); ADD.update({'O.': 'Onkelos (after a Targum citation: Targ. O.)', 'h.': 'Hebrew (as in h. text)'})
tok = re.compile(r"(?<![A-Za-zÀ-ɏḀ-ỿ̀-ͯ’'&.])([A-Za-zÀ-ɏḀ-ỿ̀-ͯ][A-Za-zÀ-ɏḀ-ỿ̀-ͯ’']{0,13}\.)(\s*)(.?)")
tot, mid, cite, ex, nent = collections.Counter(), collections.Counter(), collections.Counter(), {}, collections.Counter()
pairs = collections.Counter()
HEB = collections.Counter(); hex_ = {}
def heN(t): return re.sub(r'[֑-ׇ]', '', u.normalize('NFD', t)).replace('״', '"').replace('׳', "'")
HEL = collections.defaultdict(list)
for a, m in HE: HEL[heN(a)].append(re.sub(r'<[^>]+>', '', m))
for r, e in J.items():
    t = html.unescape(re.sub(r'<[^>]+>', ' ', e['html'])); t = re.sub(r'\s+', ' ', t)
    hw = re.sub(r'[^א-ת]', '', heN(e['h']))
    for m in re.finditer(r'[א-ת]+(?:"[א-ת]+|\')+', heN(t)):
        w = m.group(0)
        if '"' not in w and w not in HEL: continue   # a word cut short (ס׳, שי׳): Jastrow's way of shortening a quoted word, not an abbreviation
        HEB[w] += 1; hex_.setdefault(w, (e['h'], heN(t)[max(0, m.start() - 40):m.end() + 30]))
    en = re.sub(r'[֐-׿"\'׳״]+', ' ', t)
    for p in ('i. e.', 'i.e.', 'e. g.', 'e.g.', 'h. text', 'h. a. ch.', 'l. c.'):
        if p not in listed: pairs[p] += en.count(p)
    en = rx.sub(' ', en)
    seen = set()
    for m in tok.finditer(en):
        w, sp, nx = m.groups()
        tot[w] += 1
        if w not in seen: nent[w] += 1; seen.add(w)
        if nx and (nx.islower() or nx.isdigit() or nx in ',;:)]—–-' or nx in 'ᵃᵇᶜᵈ'): mid[w] += 1
        if re.match(r'\s*[IVXL]+[,.\s]|\s*\d', en[m.end(1):m.end(1) + 6]): cite[w] += 1
        if w not in ex: ex[w] = (e['h'], en[max(0, m.start() - 45):m.end() + 35].strip())
from nltk.corpus import wordnet as wn
STOP = set('me him her it us them you thee thou thy thine his hers its their theirs ours mine yours this that these those there here then '
           'out up off on in at by to of for from with so too also again once one ones all any each other others another nothing '
           'something anything everything himself herself itself themselves myself thyself yourself ourselves else now ago yet still '
           'away down over before after about above below under between within without into upon whom who what which why how where when'.split())
def word(w):
    b = w[:-1].lower().replace('’', "'")
    return b in STOP or (len(b) > 2 and bool(wn.synsets(b)))
KEEP1 = {'O.': 'Onkelos (after a Targum citation: Targ. O.)', 'h.': 'Hebrew (as in h. text)'}
rows = []
for w, n in tot.items():
    if n < 5: continue
    if (len(w) == 2 and w not in ADD) or (word(w) and w not in ADD and w not in KEEP1 and not (w.lower() in lower)): continue
    ratio = (mid[w] + cite[w]) / n
    if ratio < 0.6 and w not in ADD: continue
    rows.append((w, n, nent[w], ratio))
rows.sort(key=lambda x: -x[1])
def cell(s): return s.replace('|', '\\|')
out = ['# Abbreviations in the pop-up entries that are not in Jastrow’s List of Abbreviations', '',
       f'Counted over the {len(J):,} entries the pop-up uses. The page currently explains only the {len(EN)} abbreviations on Sefaria’s *Jastrow, List of Abbreviations*. '
       'Below: things the entries use that the list lacks, most frequent first. “Uses” counts every occurrence; “entries” counts entries. '
       'A suggested meaning is given where I am confident; check the others against Jastrow’s usage.', '',
       '## 1. Same as a listed abbreviation but capitalized differently', '',
       'Usually just sentence position (“V.” starting a sentence = “v.”). These could be matched automatically.', '',
       '| In the entries | Uses | Listed as | Meaning on the list | Example |', '|---|---|---|---|---|']
rest = []
for w, n, ne, ratio in rows:
    L = lower.get(w.lower())
    if L and w not in listed and len(w) > 2 and ((L[0].islower() and w[0].isupper()) or w in ('trnsf.', 'var.')):
        out.append(f'| {w} | {n:,} | {L} | {cell(dict(EN)[L])} | {cell(ex[w][1])} |')
    else: rest.append((w, n, ne, ratio))
out += ['', '## 2. Pairs of abbreviations read together', '', '| Abbreviation | Uses | Suggested meaning |', '|---|---|---|']
SUG2 = {'i. e.': 'id est, that is', 'i.e.': 'id est, that is', 'e. g.': 'exempli gratia, for example', 'e.g.': 'exempli gratia, for example', 'h. text': 'Hebrew text (of the Bible verse the Targum translates)',
        'h. a. ch.': 'Hebrew and Chaldaic (Aramaic)', 'l. c.': 'loco citato, in the place cited'}
for p, n in pairs.most_common():
    if n: out.append(f'| {p} | {n:,} | {SUG2.get(p, "")} |')
out += ['', '## 3. Other abbreviations', '',
        'Single words ending in a period that are mostly followed by more of the sentence (so probably abbreviations, not sentence ends). '
        'Some will be ordinary words or parts of names (e.g. initials); those can simply be left out.', '',
        '| Abbreviation | Uses | Entries | Suggested meaning | Example (entry: text) |', '|---|---|---|---|---|']
for w, n, ne, ratio in rest:
    out.append(f'| {w} | {n:,} | {ne:,} | {cell(ADD.get(w, ""))} | {cell(ex[w][0])}: …{cell(ex[w][1])}… |')
out += ['', '## 4. Hebrew and Aramaic abbreviations', '',
        'Jastrow has a separate list, “Hebrew or Aramaic Abbreviations” (306 items), that is not on Sefaria’s *List of Abbreviations* page. '
        'These are the ones the entries use: every form with ״, and forms with ׳ that are on that list (other words cut short with ׳, like ס׳ for the entry’s own word, are left out). With that list’s meaning where it has one.', '',
        '| Abbreviation | Uses | In Jastrow’s Hebrew list | Example |', '|---|---|---|---|']
for w, n in HEB.most_common():
    if n < 5: break
    m = HEL.get(w) or []
    out.append(f'| {w.replace(chr(34), "״").replace(chr(39), "׳")} | {n:,} | {cell("; or ".join(m))} | {cell(hex_[w][1])} |')
open(SP + 'abbr-review.md', 'w', encoding='utf8').write('\n'.join(out) + '\n')
print( 'section3', len(rest), 'hebrew', sum(1 for w, n in HEB.items() if n >= 3))
