"""og_image.py OUT.png : the link-preview picture (1200x630) shown when the page is shared in WhatsApp, iMessage etc."""
import sys
from PIL import Image, ImageDraw, ImageFont
SP = '/tmp/claude-0/-home-claude/b2b6b330-0f50-5db3-a7e4-69fa01b487e5/scratchpad/'
VB = SP + 'fonts-src/Mekorot (LPPL)/Vilna/Mekorot-Vilna-Bold.ttf'
VR = SP + 'fonts-src/Mekorot (LPPL)/Vilna/Mekorot-Vilna.ttf'
SER = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERB = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
W, H = 1200, 630
TEAL, PAPER, INK, MUTED, MARK = (31, 90, 90), (247, 248, 244), (29, 36, 34), (95, 107, 103), (243, 226, 179)
im = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(im)
f = lambda p, s: ImageFont.truetype(p, s)
# right: teal panel with the ת״א mark and the name
PX = 760
d.rectangle([PX, 0, W, H], fill=TEAL)
mark = 'ת"א'; fm = f(VB, 190)
bb = d.textbbox((0, 0), mark, font=fm, direction='rtl')
d.text((PX + (W - PX - (bb[2] - bb[0])) / 2 - bb[0], 95 - bb[1]), mark, font=fm, fill=(255, 255, 255), direction='rtl')
for txt, font, y, col in [('חומש עם אונקלוס', f(VB, 54), 335, (255, 255, 255)),
                          ('Chumash with Onkelos', f(SERB, 29), 420, (255, 255, 255)),
                          ('clause by clause · Rashi · Jastrow', f(SANS, 22), 478, (205, 226, 223))]:
    rtl = any('֐' <= c <= '׿' for c in txt)
    bb = d.textbbox((0, 0), txt, font=font, direction='rtl' if rtl else None)
    d.text((PX + (W - PX - (bb[2] - bb[0])) / 2 - bb[0], y - bb[1]), txt, font=font, fill=col, direction='rtl' if rtl else None)
# left: one clause the way the page shows it (Bereishis 49:10)
L, R = 56, PX - 56
def line(txt, font, y, col, hl=None):
    bb = d.textbbox((0, 0), txt, font=font, direction='rtl')
    x = R - (bb[2] - bb[0]) - bb[0]
    d.text((x, y - bb[1]), txt, font=font, fill=col, direction='rtl')
def hl_rtl(full, part, font, y, col):
    """draw an RTL line with `part` on a highlight"""
    bb = d.textbbox((0, 0), full, font=font, direction='rtl'); x0 = R - (bb[2] - bb[0]) - bb[0]
    i = full.index(part); right = full[:i]
    rw = d.textlength(right, font=font, direction='rtl') if right else 0
    pw = d.textlength(part, font=font, direction='rtl')
    xr = R - rw; d.rounded_rectangle([xr - pw - 6, y - 4, xr + 6, y + font.size + 10], radius=6, fill=MARK)
    d.text((x0, y - bb[1]), full, font=font, fill=col, direction='rtl')
d.text((L, 58), 'BEREISHIS 49:10', font=f(SANS, 18), fill=MUTED)
line('עַד כִּי־יָבֹא שִׁילֹה', f(VB, 60), 110, INK)
hl_rtl('עַד דְּיֵיתֵי מְשִׁיחָא', 'דְּיֵיתֵי מְשִׁיחָא', f(VB, 54), 215, TEAL)
fe = f(SER, 30); fb = f(SERB, 30); y = 330
d.text((L, y), 'until Shiloh comes', font=fe, fill=INK); y += 52
d.text((L, y), 'until ', font=fe, fill=INK); x = L + d.textlength('until ', font=fe)
part = 'the Moshiach will come'; pw = d.textlength(part, font=fb)
d.rounded_rectangle([x - 4, y - 2, x + pw + 4, y + 40], radius=6, fill=MARK); d.text((x, y), part, font=fb, fill=INK)
d.line([L, 470, R, 470], fill=(221, 227, 223), width=2)
d.text((L, 492), 'Hebrew · Targum Onkelos · English, side by side', font=f(SANS, 22), fill=MUTED)
d.text((L, 528), 'Tap any Aramaic word for its meaning', font=f(SANS, 22), fill=MUTED)
im.save(sys.argv[1], optimize=True)
