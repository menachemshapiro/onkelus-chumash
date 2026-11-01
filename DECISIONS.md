# Chumash with Onkelos — Compromises and Decisions

Updated Oct 20, 2026 · Menachem

## Hebrew clause splitting rule

Each pasuk is split into clauses by its te'amim, using one fixed rule:

- It always breaks at **etnachta**, **segolta** and **shalshelet**.
- It breaks at **zakef** (katon or gadol) only when at least 2 words fall on each side.
- It does not break at lesser disjunctives (revia, tipcha, pashta and so on).

Where this rule gave a clause that the Targum or the English couldn't follow, the clauses were joined. The next section lists those pesukim.

## Hebrew text checks (Oct 23)

- **The Hebrew is Sefaria's text, unchanged.** build/heb_check.py compares every pasuk on the page with the Sefaria source (Tanach with Ta'amei Hamikra), letter, vowel and ta'am. Only the petucha/setuma signs, the paseq (left as is) and the line splits differ. Oct 23: all 5,846 pesukim match.
- **Meteg next to a vowel.** In the default font (Noto Serif Hebrew), a meteg after a vowel is drawn in the middle of the vowel, so tzeirei + meteg looks like a kamatz (reported in Bereishis 16:8, אֵֽי־מִזֶּה; the text itself was right). The page puts a zero-width joiner between the vowel and the meteg when te'amim are shown, which makes the font set the meteg beside the vowel; copied text drops the joiner again. This affects about 9,000 places (tzeirei 1,092, segol 1,300, kamatz 2,915 and others). build/meteg_test.js draws every vowel + meteg in Noto Serif Hebrew, Frank Ruhl Libre and David Libre and fails if a meteg lands inside a vowel. Mekorot Vilna sets the meteg below the vowel rather than between its dots, with or without the joiner.

## Hebrew clauses joined, by parsha

In these pesukim, two or more clauses from the rule were shown as a single line. Usually this was because the Targum or the English could not be split at the same point.

| Parsha | Pesukim |
| --- | --- |
| Bereishit | 4:7, 4:20, 4:21, 4:26, 5:1, 6:2, 6:3; the ages in ch. 5 (5:5, 7, 8, 10, 11, 13, 14, 16, 17, 20, 23, 26, 27, 30, 31) |
| Noach | 7:4, 7:6, 7:10, 7:12, 8:10, 8:12, 9:28, 9:29, 10:18, 11:7, 11:13, 11:15, 11:17 |
| Lech Lecha | 12:7, 15:3, 15:17, 16:8, 17:1, 17:26 |
| Vayera | 18:25, 18:28, 18:33, 20:10, 20:13, 20:14, 21:5, 21:16, 21:30, 22:1 |
| Chayei Sarah | 23:6, 24:8 |
| Toldot | 25:23, 26:18, 26:24, 27:6, 27:11, 27:30, 27:34, 28:2 |
| Vayetzei | 29:8, 29:13, 29:17, 30:14, 30:22, 30:29, 31:6, 31:47, 31:53 |
| Vayishlach | 32:20, 34:4, 34:13, 34:19, 35:5, 35:29, 36:13, 36:32 |
| Vayeshev | 39:6, 39:19 |
| Miketz | 41:4, 41:7, 41:20, 41:24, 41:26, 41:27, 41:43, 42:21, 44:8, 44:17 |
| Vayigash | 44:19, 44:33, 47:5 |
| Vayechi | 47:28, 48:9, 48:20, 48:21, 49:31, 50:4, 50:25 |
| Shemot | 1:1, 1:14 |
| Bo | 12:40, 12:41 |
| Beshalach | 16:16 |
| Yitro | 18:17, 20:19 |
| Mishpatim | 22:8, 24:13 |
| Terumah | 25:26, 25:27, 26:2, 26:5, 26:8, 26:25 |
| Tetzaveh | 28:23, 29:36 |
| Ki Tisa | 32:8, 34:4, 34:10, 34:35 |
| Vayakhel | 36:9, 36:10, 36:12, 36:15, 36:26, 36:30, 37:13, 37:14, 38:17 |
| Pekudei | 39:6, 40:3, 40:31 |
| Vayikra | 3:6, 4:28 |
| Tzav | 7:12, 7:17 |
| Shemini | 10:16 |
| Tazria | 13:57 |
| Acharei Mot | 16:5 |
| Kedoshim | 19:2, 19:4, 19:28 |
| Emor | 21:8, 21:12, 23:14, 24:5 |
| Behar | 25:9, 25:41 |
| Bechukotai | 26:14, 26:32, 26:38 |
| Bamidbar | 1:25, 2:15, 3:21, 3:46 |
| Behaalotecha | 10:5, 11:14, 11:24 |
| Shelach | 15:11, 15:22, 15:33 |
| Korach | 17:17, 17:18, 18:21 |
| Chukat | 20:4, 20:10, 20:21, 21:24 |
| Balak | 22:3, 22:17, 23:26 |
| Pinchas | 27:20, 28:4, 28:17 |
| Matot | 30:9, 31:31, 31:36, 31:40, 31:43, 31:46, 32:11, 32:15, 32:18 |
| Masei | 33:40, 35:24, 35:30, 35:33 |
| Devarim | 1:32, 3:6 |
| Vaetchanan | 4:5, 4:14, 5:22, 6:14, 6:16, 6:17 |
| Eikev | 7:20, 9:11 |
| Re'eh | 12:26, 14:1, 15:21, 16:1 |

No clauses were joined in Vaera, Metzora, Naso, Shoftim, Ki Teitzei, Ki Tavo, Nitzavim, Vayeilech, Ha'azinu or Vezot Haberachah.

## Hand-set split points

3,583 pesukim have Onkelos and/or English break points that were set by hand: 885 in Bereishit and 2,698 in Shemot through Devarim. In those pesukim, the automatic word-count alignment put a break in the wrong place.

- 1:1–10 were aligned entirely by hand.
- In the rest of the Chumash, the automatic splits were checked against a full printout of each parsha. They were corrected only where a line clearly didn't match its Hebrew clause.
- Each English line starts where its first few words are found in the pasuk. When those words were too short (for example, just "said"), they could match an earlier spot and start the line in the wrong place. In those cases more words were used so the line starts in the right place, for example "The servant said" instead of "said". Other examples: "They will kill", "His father rebuked" (Vayeshev 37:10), "the sons of Eliphaz", "[Eisov] said".

## Where the English can't match the Hebrew

In some pesukim, the English line cannot line up exactly with its Hebrew clause:

- **Word order.** English word order sometimes places a word in the neighbouring clause. The split follows the English sentence rather than breaking it mid-phrase. Examples: 21:30 ("Take"), 3:12, 29:24, 29:29, 37:2.
- **Long bracketed Onkelos renderings.** Short bracketed glosses stay whole. Where a long bracket covered several Hebrew clauses, it was cut at the Targum's own clause breaks and each piece placed after the English it matches, so every line shows the Hebrew, Targum and English of the same clause. Only the order of the English words changed; a check confirms none were added or lost. These pesukim have a **Show original** button on the page. This was done in 33 pesukim: Ha'azinu 32:12, 13, 14, 15, 19, 22, 32, 34, 36, 41; Vezot Haberachah 33:2, 3, 6, 7, 9, 17, 18, 26; Noach 11:5; Lech Lecha 13:16, 14:17; Vayera 20:16, 21:22, 22:14; Vayetzei 31:39; Vayechi 49:9, 49:11, 49:17; Vaera 8:22; Beshalach 15:11, 17:16; Behaalotecha 12:12; Balak 23:19. In Vayechi 49:9, 11 and 17, Hebrew clauses that had been joined were split again. About 40 other pesukim have a long bracket that already sits with its own clause, and were left as they are.

## Changes to the English text

The Metsudah English was changed only in the places listed in the table. Everything else is as in the source.

| Change | Where |
| --- | --- |
| Spaced dashes made into proper dashes | Bereishit 3:12, 13:17, 19:4, 19:11, 19:12, 19:24, 20:7, 22:2, 24:7, 24:16, 26:15, 27:23, 29:27, 30:31, 32:12, 34:14, 34:24, 34:29, 35:6, 37:25, 38:30, 39:1, 39:17, 45:10, 48:13; Shemot through Devarim: every dash, done automatically |
| "transgr ession" → "transgression" | Bereishit 50:17 |
| Stray "û" → "—" | Bereishit 49:17 |
| "Burnt — offering" → "Burnt-offering" | Shemot 31:9 |
| "of of Eliav" → "of Eliav" | Bamidbar 7:29 |
| "Adonoy, El him" → "Adonoy, Elohim" | Devarim 3:24 |
| "nd you inherit" → "and you inherit" | Devarim 26:1 |
| "of these these happenings" → "of these happenings" (reported on the page) | Bereishit 24:28 |
| Italic glosses shown in bold | Throughout |

**Clear typos were corrected** throughout the Chumash (66 in all): misspellings such as "Angles" → "Angels" (Bereishit 32:31), "Sidal" → "Tidal" (14:9, as in 14:1), "divid", "rasied", "testimonoy", "exept", "promished", "seperate", "bretheren", "stubborness", "annointing", "annihalate", "inquities" and "persued"; doubled or wrong words such as "the the midst", "the their land", "your are", "to do perform" and "such a think"; and words broken across a line, such as "congrega-tion" and "compen-sation". Unusual but deliberate wording (archaic spellings, transliterations, words like "doublefold" and "grainstalks") was left as it is. "Chazak" at the end of Bereishit 50:26 and Devarim 34:12 was kept.

## Display decisions

- **Glosses:** italic glosses in the English get the same highlight as the bold ones.
- **Targum variant notes** (נ״י / נ״א / ס״א) appear in small grey type.
- **Ketiv/qere** is shown as in the source, with the qere in brackets, e.g. אהלה [אהלו].
- **Mid-pasuk parsha break:** the petucha inside 35:22 is shown inline as {פ}.
- **Verse numbers** are in Hebrew letters, with טו / טז for 15 and 16.
- **Te'amim toggle:** turning it off removes the cantillation marks, meteg and paseq, and keeps the niqqud (from v16).
- **Transliterated words:** Hebrew terms written in English letters in the translation (kohein, matzos, Shabbos, mishkan, shemitah, Amein and so on) are not highlighted. Only bracketed glosses are marked as places where the Onkelos departs from the plain meaning.
- **Go-to box:** the box at the end of the location bar jumps to a pasuk, e.g. `32:13`, `לב יג`, `Vayechi 49:11` or `שמות טו יא`. With numbers only, it searches the current parsha first, then the rest of that sefer. Links to a pasuk (`#parsha/perek:pasuk`) work only when the page is opened outside claude.ai, because claude.ai doesn't pass the link's `#` part into the page.
- **Report:** every pasuk has a small Report button. A report records the pasuk, which part needs fixing and a note, and is saved with the page so Claude can read the list and fix them.

## Aliyot

- The aliyah divisions follow Hebcal's full-kriyah (Shabbos) schedule.
- Maftir overlaps the end of shevi'i, so "(מפטיר)" appears inside shevi'i rather than starting a separate section.
- Exporting the shevi'i aliyah therefore runs to the end of the parsha, including the maftir pesukim.
- **Double parshiyot** (Vayakhel-Pekudei, Tazria-Metzora, Acharei Mot-Kedoshim, Behar-Bechukotai, Chukat-Balak, Matot-Masei, Nitzavim-Vayeilech) each have their own entry, with Hebcal's combined aliyah breaks rather than the breaks of the two separate parshiyot.
- Where two aliyot start on the same pasuk, they share one label, e.g. "שביעי ומפטיר" in Eikev.
- Vezot Haberachah has seven aliyot and no maftir, following Hebcal.

## Rashi

- Niqqud is stripped from Rashi to match the usual Rashi script presentation.
- Doubled punctuation marks from the source were cleaned up.
- On the page, Rashi sits under its pasuk in columns: 1, 2, 3 or 4, chosen under Typography → Rashi → Columns. The default is 3 on a computer and 1 on a phone.

## Export

| Format | Decision or limitation |
| --- | --- |
| All | Rashi columns (1–4) are chosen in the Export panel and apply to PDF, Word and HTML; the choice starts at the page's own Typography setting. In Word, the comments are split, in order, into columns of about equal length. |
| Word (.docx) | Uses the font names from the Typography panel, so those fonts must be installed on the computer that opens the file. |
| Word (.docx) | Needs an internet connection, because the Word library loads from a CDN on first use. |
| Page loading | The page holds no verse text itself; each parsha's text and Rashi is a separate file fetched when that parsha is opened (about 45 KB compressed each), so the page opens quickly. Only the four default fonts are waited for; the Typography panel's other fonts load in the background. |
| PDF | Saved as a real .pdf file, built in the page (works on phones, where printing is blocked). Each page is a picture of the text, so it looks exactly like the page but the text can't be selected or searched; for selectable text, export Word or HTML. If the PDF can't be built, it falls back to a print-ready HTML file. |
| HTML | Fonts are embedded, so the file looks the same offline. |
| All | The viewer asks you to confirm each save before the file downloads. |

## Targum glossary (beta)

- **What it covers.** Every word of the Targum in all 54 parshiyot can be tapped. The card shows the word split into its parts (prefixes, the word itself, endings), the root, the grammatical form, what the word means in this pasuk, and the dictionary entry.
- **Beta.** The glossary was written word by word with Claude and checked by script, not by a scholar. It will have mistakes. The card says so, and its **Report a problem** button sends a note about that word.
- **Meaning "here".** Each word has a meaning that fits most places it appears. Where a word means something else in a particular pasuk, that pasuk has its own entry. Some fixed phrases are handled as phrases: זִמְנָא after מַשְׁכַּן reads "(the Tent of) Meeting", not "time".
- **Words with ו ד ל ב כ מ in front.** If such a word was not written out, it is built from the plain word plus the prefix. This is not done when the letter is really part of the word (a preposition never attaches to a finished verb), which avoided errors like "from -teen" for מַעְשַׂר.
- **Notes that belong to one pasuk.** A note explaining an idiom ("עַד לָא = not yet") or giving the Hebrew word Onkelos translates ("Hebrew: אָסוֹן") is shown only in a pasuk that actually contains those words. A name supplied as the subject of a verb ("(Hashem) commanded") is shown only where the English of that pasuk has that name.
- **Alternate readings** (נ"א, נ"י and similar) stay in the Targum text, in parentheses and a smaller font, and can be tapped like any other word.
- **Outside help.** For a small number of hard words (71 lookups in all), the meaning was checked against the Comprehensive Aramaic Lexicon (cal.huc.edu). Every lookup is logged in `build/cal-log.json`.
- **Cleanup pass.** After all five books were done, every gloss in the Torah was compared with the English of its pasuk. About 2,270 glosses were corrected where a meaning written for one pasuk had been reused where it did not fit.

## English as Onkelos reads it

- **Three English modes.** The drop-down next to the English button chooses which English is shown. **Combined** is the Metsudah English as printed, with Onkelos's wording in [brackets]. **Plain** takes the brackets out, so the English follows the Hebrew. **Onkelos** rewrites the English so that it follows the Targum.
- **Which pesukim.** Only pesukim where the Targum has bracketed wording of its own get an Onkelos English (2,321 pesukim). In every other pasuk all three modes show the same English.
- **How it is written.** The Onkelos English keeps Metsudah's words wherever the Targum agrees with them. Wording that comes from Onkelos is in bold. Where the Hebrew says Elohim, the English keeps "God". Connecting words that Metsudah leaves out are added in {curly brackets}, but only when they make the English read better.
- **Word by word.** Every Aramaic word, prefix and suffix is matched to the English that renders it, or marked "not translated". English words with no Aramaic word behind them are listed as "English only". A script checks every pasuk. Any English word that is not in bold must appear in Metsudah's own English for that clause. If a word's Aramaic is on another line, the word is moved to that line.
- **Onkelos word by word.** When **Word by word** is on, each line has an **Onkelos word by word** drop-down under the English, with the table of matches and any notes. It stays available when the English is turned off.
- **Notes.** A note is added only when it tells the reader something the English does not show by itself. That can be a Targum word that Metsudah renders loosely, an idiom, or a reading that needs explaining. There are no notes just to say that Metsudah's word follows the Hebrew, or that Metsudah left out a word or prefix. About 1,400 notes of that kind were removed on Oct 21. A second pass then compared every word-by-word pair with the glossary meaning of its Aramaic word, and added a short note where Metsudah's kept English is loose (for example בְּנָךְ "your children" for Metsudah's "descendants", or בְּקַשְׁיוּ "with hardness" for "contrary"). Most flagged pairs were plain synonyms and got no note. The same pass was then run with a word list for every clause and over Bereishis 49, and notes that only said a word or prefix was left untranslated were removed.
- **Where the files are.** The hand-written matches are in `build/eo-align/<parsha>.txt`. They are checked by `build/eo_check.py` and merged into the parsha data by `build/eo_merge.py`. Rewritten renderings used throughout include "the Word of" (מֵימְרָא), "Shechina", "before" for "to", "accept the word of" for obey, and "idols of the nations" for other gods.

## Interface

- **Toolbar.** The parsha, perek and pasuk pickers come first. Next are small toggles for Te'amim, Targum, English (with its mode drop-down), Rashi and Word by word. Typography (Aa) and Export (⤓) are icons, with their full names in a tooltip.
- **Verse size.** The default size of the Hebrew is 1.85rem.
- **Phones.** No מקרא / תרגום / English labels are shown on a phone. The three texts are told apart by font and color. In the Stacked layout on a larger screen, the labels appear once at the start of each perek.
- **Reopening.** The page remembers the last pasuk you were reading (and how far into it) in this browser, and opens there next time, including from the home-screen shortcut. A link to a specific pasuk still wins.
- **Go-to box.** It widens while you type. On a phone it takes its own full-width row with 16px text (so iOS doesn't zoom), and shrinks back before the jump so the pasuk lands right under the bar.
- **Keeping your place.** Switching the English mode, turning Targum, English, Rashi, te'amim or word by word on or off, changing fonts or sizes, or rotating the phone keeps the pasuk you were reading in place (at the same point within it) instead of letting the page drift to another pasuk.
- **Help.** The **?** button opens a short guide to the page's features.
- **Report on the GitHub copy.** The copy on GitHub Pages has no place to save reports yet, so its Report buttons show a short notice that the feature is not available there yet. On claude.ai, reports are saved with the page.

## Targum highlights filled in

- Bereishis 49 and Vayikra 25–27 have no highlight marks in the source Targum. There, the highlights are filled in from the word-by-word match: a Targum word is highlighted when the English used for it includes Onkelos's own (bold) wording. Checked against the chapters that do have source marks, this rule agrees about 92% of the time on what to highlight and finds about 91% of the marked words. The rule is in `build/tg_hl.py` and runs in `eo_merge.py`.

## Jastrow pop-up

- **What it is.** On a glossary card, *Jastrow → Open entry* shows the word's entry from Jastrow's *Dictionary of the Targumim, the Talmud Babli and Yerushalmi, and the Midrashic Literature* (1903, public domain), as published on Sefaria. Links from one Jastrow entry to another open that entry inside the pop-up, with a Back button (about 14,200 of 24,000 such links; the rest, to entries not downloaded, go to Sefaria). Citations link to the source on Sefaria, except citations of Onkelos, which jump to that pasuk on this page (Ctrl/⌘-click opens it in a new tab, outside claude.ai). Targum Yonasan, Ketuvim and other sources stay on Sefaria.
- **Where the entries came from.** `build/jastrow/fetch_jastrow.py` looked up each glossary headword once with Sefaria's dictionary API (about 3,100 lookups, run on Menachem's computer, Oct 21). Sefaria's bulk text export does not include its dictionaries.
- **Matching.** `build/jas_match.py` picks, for each glossary entry, the Jastrow entry whose headword has the same letters (preferring the same vowels), that is Aramaic, cites the Targum, has the same part of speech, and shares words with the glossary meaning. Bare cross-references ("v. X") are followed to the entry they point to. A second lookup (`build/jastrow/fetch_jastrow2.py`, Oct 21) downloaded the 1,935 entries the first round's entries point to, so most pointers now resolve. If no entry for the word itself fits, a verb is matched to its root's entry, and the pop-up says so. A match with neither the same vowels nor any shared meaning is dropped. About 1,840 of the 2,160 glossary entries have a Jastrow entry (1,570 for the word itself, 265 for its root). Where other entries also fit, they are offered as "Other possible entries". All related entries appear as tabs at the top of the pop-up, in dictionary order: every entry whose headword or alternative form has the same letters as the word or its matched entry, reading a weak last letter (א ה י) as one letter and keeping shin and sin apart. So צַלִּי shows צלי/צָלָה (Hebrew, to roast), צְלֵי/צְלָא I, צְלֵי ²/צְלָא II and צָלִי. Each tab is labelled "this word" (the matched entry, which also has a highlighted background), "cites 12:8" when the entry cites Onkelos on the pasuk being read (that citation is highlighted in the entry), or "Targ. O." when it cites Onkelos elsewhere.
- **Beta.** The matching is automatic, so some entries will be the wrong homograph; the pop-up says so.
- **Files.** `j/index.json` maps glossary entries to Jastrow entries; `j/<letter>.json` holds the entries, loaded only when one is opened. On the home-screen app each letter file is kept for offline use once it has been opened.

## Jastrow matching (Oct 22)
- Matches are made by script (build/jas_match.py). Any match whose Jastrow meaning shares no words with the glossary meaning was checked by hand; corrections are kept in build/jas-override.json (glossary id → Jastrow entry, or null for "no right entry downloaded"). Overrides win over the script.
- Where Jastrow gives a short Aramaic entry ("ch. same") the pop-up shows it with the Hebrew entry it refers to; we point to the Aramaic entry when it cites Onkelos.

## Translation check (Oct 22)
- A word's meaning in a pasuk is checked against its dictionary meaning and Jastrow; where the link was to the wrong word (a homograph, or a form matched by letters alone) it is relinked; where Onkelos's meaning differs from Metsudah's English and the English was ours, the English follows Onkelos.
- Hand fixes to the glossary live in build/glfix.tsv so they survive a rebuild: F = relink/re-gloss a form, A = a verse-scoped line added to gl/cleanup.txt, L = a dictionary meaning.

## Jastrow sources (Oct 22)
- Sefaria's current text (from its API) is always preferred. Sefaria-Data's 2018 XML (commit 947c1b9, the one before "Delete dicts") is used only for entries not yet downloaded, and for cross-referencing and citation checks done locally, so Sefaria's servers are not asked for them. Entries shown from the 2018 copy carry a note in the pop-up.
- A Jastrow entry that cites an Onkelos pasuk for the same word as our glossary word is taken as that word's entry (build/jas-targ.json), unless the citation is for a different part of speech (rejected by hand). Hand-checked choices (build/jas-override.json) still win.

- Jastrow's “ch. same” means “same as the entry before”. Such an entry is shown together with that entry in one tab, in dictionary order, each under its own title (build/jas_build.py, group()).
- Jastrow's “preced.” (and “preced. wds.”) always points to the entry right before (checked: all 2,252 uses in the pop-up). An entry that refers to the one before it this way (“(preced.)” = derived from it, “v. preced.”, “= preced.”, “fem. of preced.” …) is shown after it in the same tab, like “ch. same”. Chains are followed; a chain longer than 8 entries shows 8 around the word.
- **Abbreviations.** Words in a Jastrow entry that are on Jastrow's “List of Abbreviations” (280 items, matched regardless of capitals) or his “Hebrew or Aramaic Abbreviations” (306 items; also with one prefix letter, e.g. ד + א״ר) get a dotted underline, as do a few pairs read as one (h. text, i.e., e.g., h. a. ch.). Hovering (computer) or tapping (phone) shows the meaning in a small tooltip; on a phone, tapping an abbreviation inside a link shows the meaning instead of following the link. The ? button turns this on or off (remembered). Both lists are Sefaria's current text (jastrow/jastrow-abbr-list.json; the same items as the 2018 copy, with a few small spelling corrections). The lists (j/abbr.json, about 23 KB) are loaded the first time an entry is opened, not with the page. abbr-review.md lists other abbreviations the entries use, for review.
- **Fixes to Sefaria's Jastrow from the 1903 scans** (build/jas_fix.py, from Menachem's work on rebuilding the printed layout, Oct 23): 49 binyan names that were lost (only “*.” or “[.” left) are restored from the scans (e.g. *Pi., [Hif.); 5 short entries that had been stuck onto the entry before them as fake binyanim are separate entries again, shown right after it (עָקַם, כְּפוּשָׁה, שֶׁגֶם, *דְּקִילִין, נרווד); in סָתַר I, נִסְתַּר is text and the binyan is Hithpa.; in אָרִיחַ the two passages written “brick over brick” are drawn as small right-to-left grids. Unsure, left as read: רְבֵי ² Pa. (maybe *Pa.), the headword נרווד, and אָחַז's *Nif. (looks like Hif., not checked). The downloaded files are not changed; the fixes are applied on every build.
- **Different readings (girsaot).** When the Jastrow entry for a word cites the pasuk with a different reading or spelling than our Targum text, the word is still linked to it, and the pop-up says so in a note under the title (build/jas-girsa.json). Oct 23: 10 such words.
- A Jastrow entry that only points elsewhere (“, v. X”, “read X”, “= X”) is shown together with X in its tab, unless X is already in another tab of the same pop-up. Links to entries the pop-up has open them in the pop-up only; they no longer also open Sefaria (only links to entries we don't have, and citations, go to Sefaria).
- Jastrow's “next w.” (also “next ws.”, “next art.”) always points to the entry right after (checked: all 544 linked uses). An entry that says it is shown before that next entry, in the same tab.

- Where CAL and Jastrow differ on a word's meaning or root, the glossary follows Jastrow and notes CAL's view in the meaning.
