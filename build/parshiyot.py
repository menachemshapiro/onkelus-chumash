"""All 54 parshiyot: id, Hebrew name, book key, English name, hebcal key."""
import json
BOOKS = {'Genesis': 'בראשית', 'Exodus': 'שמות', 'Leviticus': 'ויקרא', 'Numbers': 'במדבר', 'Deuteronomy': 'דברים'}
RASHI = {'Genesis': 'b40b2473-Rashi_on_Genesis_-_he_-_merged.json', 'Exodus': '86078330-Rashi_on_Exodus_-_he_-_merged.json',
         'Leviticus': '19c5d870-Rashi_on_Leviticus_-_he_-_merged.json', 'Numbers': '974fa1cf-Rashi_on_Numbers_-_he_-_merged.json',
         'Deuteronomy': '485aa2b8-Rashi_on_Deuteronomy_-_he_-_merged.json'}
P = [
 ('bereishit','בראשית','Genesis','Bereishit','Bereshit'), ('noach','נח','Genesis','Noach','Noach'),
 ('lechlecha','לך לך','Genesis','Lech Lecha','Lech-Lecha'), ('vayera','וירא','Genesis','Vayera','Vayera'),
 ('chayeisarah','חיי שרה','Genesis','Chayei Sarah','Chayei Sara'), ('toldot','תולדות','Genesis','Toldot','Toldot'),
 ('vayetzei','ויצא','Genesis','Vayetzei','Vayetzei'), ('vayishlach','וישלח','Genesis','Vayishlach','Vayishlach'),
 ('vayeshev','וישב','Genesis','Vayeshev','Vayeshev'), ('miketz','מקץ','Genesis','Miketz','Miketz'),
 ('vayigash','ויגש','Genesis','Vayigash','Vayigash'), ('vayechi','ויחי','Genesis','Vayechi','Vayechi'),
 ('shemot','שמות','Exodus','Shemot','Shemot'), ('vaera','וארא','Exodus','Vaera','Vaera'), ('bo','בא','Exodus','Bo','Bo'),
 ('beshalach','בשלח','Exodus','Beshalach','Beshalach'), ('yitro','יתרו','Exodus','Yitro','Yitro'),
 ('mishpatim','משפטים','Exodus','Mishpatim','Mishpatim'), ('terumah','תרומה','Exodus','Terumah','Terumah'),
 ('tetzaveh','תצוה','Exodus','Tetzaveh','Tetzaveh'), ('kitisa','כי תשא','Exodus','Ki Tisa','Ki Tisa'),
 ('vayakhel','ויקהל','Exodus','Vayakhel','Vayakhel'), ('pekudei','פקודי','Exodus','Pekudei','Pekudei'),
 ('vayikra','ויקרא','Leviticus','Vayikra','Vayikra'), ('tzav','צו','Leviticus','Tzav','Tzav'),
 ('shemini','שמיני','Leviticus','Shemini','Shmini'), ('tazria','תזריע','Leviticus','Tazria','Tazria'),
 ('metzora','מצורע','Leviticus','Metzora','Metzora'), ('achareimot','אחרי מות','Leviticus','Acharei Mot','Achrei Mot'),
 ('kedoshim','קדושים','Leviticus','Kedoshim','Kedoshim'), ('emor','אמור','Leviticus','Emor','Emor'),
 ('behar','בהר','Leviticus','Behar','Behar'), ('bechukotai','בחוקותי','Leviticus','Bechukotai','Bechukotai'),
 ('bamidbar','במדבר','Numbers','Bamidbar','Bamidbar'), ('naso','נשא','Numbers','Naso','Nasso'),
 ('behaalotecha','בהעלותך','Numbers','Behaalotecha',"Beha'alotcha"), ('shelach','שלח','Numbers','Shelach',"Sh'lach"),
 ('korach','קרח','Numbers','Korach','Korach'), ('chukat','חקת','Numbers','Chukat','Chukat'), ('balak','בלק','Numbers','Balak','Balak'),
 ('pinchas','פינחס','Numbers','Pinchas','Pinchas'), ('matot','מטות','Numbers','Matot','Matot'), ('masei','מסעי','Numbers','Masei','Masei'),
 ('devarim','דברים','Deuteronomy','Devarim','Devarim'), ('vaetchanan','ואתחנן','Deuteronomy','Vaetchanan','Vaetchanan'),
 ('eikev','עקב','Deuteronomy','Eikev','Eikev'), ('reeh','ראה','Deuteronomy',"Re'eh","Re'eh"),
 ('shoftim','שופטים','Deuteronomy','Shoftim','Shoftim'), ('kiteitzei','כי תצא','Deuteronomy','Ki Teitzei','Ki Teitzei'),
 ('kitavo','כי תבוא','Deuteronomy','Ki Tavo','Ki Tavo'), ('nitzavim','נצבים','Deuteronomy','Nitzavim','Nitzavim'),
 ('vayeilech','וילך','Deuteronomy','Vayeilech','Vayeilech'), ('haazinu','האזינו','Deuteronomy','Haazinu',"Ha'azinu"),
 ('vezot','וזאת הברכה','Deuteronomy','Vezot Haberachah','Vezot Haberakhah'),
]
AL = json.load(open('/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/dl/aliyot.json'))
def pt(s): c, v = s.split(':'); return int(c), int(v)
def aliyot(hk):
    fk = AL[hk]['fullkriyah']
    return [pt(fk[k][0]) for k in ['1','2','3','4','5','6','7','M'] if k in fk]
def rng(hk):
    fk = AL[hk]['fullkriyah']; return fk['1'][0] + '-' + fk['7'][1]
COMBINED = [  # id, Hebrew, English, hebcal key, parts
 ('vayakhelpekudei','ויקהל-פקודי','Vayakhel-Pekudei','Vayakhel-Pekudei',('vayakhel','pekudei')),
 ('tazriametzora','תזריע-מצורע','Tazria-Metzora','Tazria-Metzora',('tazria','metzora')),
 ('achareimotkedoshim','אחרי מות-קדושים','Acharei Mot-Kedoshim','Achrei Mot-Kedoshim',('achareimot','kedoshim')),
 ('beharbechukotai','בהר-בחוקותי','Behar-Bechukotai','Behar-Bechukotai',('behar','bechukotai')),
 ('chukatbalak','חקת-בלק','Chukat-Balak','Chukat-Balak',('chukat','balak')),
 ('matotmasei','מטות-מסעי','Matot-Masei','Matot-Masei',('matot','masei')),
 ('nitzavimvayeilech','נצבים-וילך','Nitzavim-Vayeilech','Nitzavim-Vayeilech',('nitzavim','vayeilech')),
]
