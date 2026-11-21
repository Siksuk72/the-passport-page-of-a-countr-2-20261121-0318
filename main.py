#!/usr/bin/env python3
"""Render an invented passport spread: the Republic of Valdoria.

Writes /output/entry.png (1024x1024, <= 1 MiB). Deterministic: every
pixel comes from this file and a fixed-seed random generator; no network,
no clock, no files outside the repository.

The document: a passport of the Republic of Valdoria, a small landlocked
alpine republic. Holder Elena Maris Voss, born in the capital Kaldris, is
a licensed mountain guide. The spread is the data page (left) and the
visas page (right), carrying one summer journey — Ostara, Talyria, the
Free Port of Brennar, home to Valdoria — with every stamp dated after
the passport's issue (12 JUN 2024) and in travel order. The telling
paperwork detail is Condition 7: a licensed guide may not take clients
above 3,000 m without a second guide (Valdorian Alpine Code s.12).

Run:  python3 main.py        (writes /output/entry.png)
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
PAPER = (243, 238, 224)      # passport paper
PAPER2 = (238, 232, 214)
INK = (28, 43, 51)           # document ink
MUTE = (92, 96, 88)          # small-print grey
GREEN = (31, 77, 58)         # Valdoria green
GOLD = (160, 125, 44)
RULE = (120, 116, 98)
BG = (26, 38, 40)            # table the spread lies on
STAMP_BLUE = (39, 64, 139)
STAMP_GREEN = (46, 107, 52)
STAMP_RED = (139, 47, 35)
STAMP_PURPLE = (91, 47, 122)

# ---------------------------------------------------------------- fonts
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/truetype/liberation/",
    "/usr/share/fonts/truetype/noto/",
]
_FACES = {
    "serif": ["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf"],
    "serif_b": ["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"],
    "sans": ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
    "sans_b": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    "mono": ["DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"],
    "mono_b": ["DejaVuSansMono-Bold.ttf", "LiberationMono-Bold.ttf"],
}
_cache = {}


def font(name, size):
    key = (name, size)
    if key in _cache:
        return _cache[key]
    for d in _FONT_DIRS:
        for fname in _FACES[name]:
            path = os.path.join(d, fname)
            if os.path.exists(path):
                try:
                    _cache[key] = ImageFont.truetype(path, size)
                    return _cache[key]
                except OSError:
                    continue
    _cache[key] = ImageFont.load_default()
    return _cache[key]


def text_c(d, cx, y, s, f, fill=INK):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def text(d, x, y, s, f, fill=INK):
    d.text((x, y), s, font=f, fill=fill)


def wrap(d, s, f, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        elif cur:
            lines.append(cur)
            cur = w
        else:
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- MRZ (ICAO 9303)
def mrz_check(s):
    vals = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
    total = 0
    for i, ch in enumerate(s):
        v = 0 if ch == "<" else vals[ch]
        total += v * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = ("P<" + "VLD" + "VOSS" + "<<" + "ELENA<MARIS").ljust(44, "<")
    doc = "VD0417823"
    dob, sex, exp = "940314", "F", "340611"
    body = (doc + mrz_check(doc) + "VLD" + dob + mrz_check(dob) + sex
            + exp + mrz_check(exp) + "<" * 15)
    line2 = body + mrz_check(body)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- portrait
def draw_portrait(pw, ph):
    """Flat-illustration passport photo of Elena Maris Voss, 30, a mountain
    guide: dark auburn hair tied back, green eyes, freckles, dark green
    wool jacket. Drawn with primitives; seeded grain for a photo feel."""
    rng = random.Random(20261121)
    img = Image.new("RGB", (pw, ph), (196, 205, 210))
    d = ImageDraw.Draw(img, "RGBA")
    # backdrop: soft studio gradient, slightly darker at the edges
    for y in range(ph):
        t = y / ph
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip((206, 213, 216), (168, 180, 188)))
        d.line([(0, y), (pw, y)], fill=c)
    cx = pw // 2
    # shoulders / jacket
    d.polygon([(cx - 78, ph), (cx - 62, ph - 58), (cx - 34, ph - 44),
               (cx + 34, ph - 44), (cx + 62, ph - 58), (cx + 78, ph)],
              fill=(46, 74, 58))
    d.polygon([(cx - 34, ph - 44), (cx, ph - 18), (cx + 34, ph - 44),
               (cx + 20, ph), (cx - 20, ph)], fill=(38, 62, 48))
    # jacket collar + zipper
    d.line([(cx - 14, ph - 46), (cx, ph - 26), (cx + 14, ph - 46)],
           fill=(24, 44, 34), width=3)
    d.line([(cx, ph - 26), (cx, ph)], fill=(24, 44, 34), width=2)
    # neck
    d.rounded_rectangle([cx - 13, ph - 62, cx + 13, ph - 34],
                        radius=6, fill=(198, 148, 112))
    # hair behind head (tied back, low bun)
    d.ellipse([cx - 44, 22, cx + 44, 108], fill=(74, 40, 26))
    d.ellipse([cx - 24, 8, cx + 24, 40], fill=(74, 40, 26))
    # head
    skin = (217, 165, 131)
    d.ellipse([cx - 38, 34, cx + 38, 118], fill=skin)
    # jaw shading: soften the ellipse into a face shape
    d.polygon([(cx - 38, 70), (cx - 30, 108), (cx - 16, 122),
               (cx + 16, 122), (cx + 30, 108), (cx + 38, 70)],
              fill=skin)
    d.ellipse([cx - 38, 34, cx + 38, 118], outline=(198, 148, 112), width=1)
    # side shading (light from upper left)
    shade = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.ellipse([cx + 6, 34, cx + 42, 120], fill=(120, 70, 40, 46))
    sd.ellipse([cx - 40, 90, cx + 40, 124], fill=(150, 90, 50, 30))
    img = Image.alpha_composite(img.convert("RGBA"), shade)
    d = ImageDraw.Draw(img, "RGBA")
    # hair: fringe across forehead, side falls
    d.pieslice([cx - 40, 30, cx + 40, 92], 180, 360, fill=(74, 40, 26))
    d.polygon([(cx - 40, 40), (cx - 34, 96), (cx - 26, 96), (cx - 32, 40)],
              fill=(74, 40, 26))
    d.polygon([(cx + 40, 40), (cx + 34, 96), (cx + 26, 96), (cx + 32, 40)],
              fill=(74, 40, 26))
    d.arc([cx - 34, 30, cx + 34, 78], 200, 340, fill=(96, 54, 34), width=2)
    # ears
    d.ellipse([cx - 42, 72, cx - 34, 92], fill=skin)
    d.ellipse([cx + 34, 72, cx + 42, 92], fill=skin)
    # eyebrows
    d.arc([cx - 25, 68, cx - 9, 80], 200, 340, fill=(74, 40, 26), width=2)
    d.arc([cx + 9, 68, cx + 25, 80], 200, 340, fill=(74, 40, 26), width=2)
    # eyes: white, green iris, pupil, highlight
    for ex in (cx - 16, cx + 16):
        d.ellipse([ex - 8, 81, ex + 8, 89], fill=(245, 240, 230))
        d.ellipse([ex - 4, 82, ex + 4, 89], fill=(74, 107, 79))
        d.ellipse([ex - 2, 83, ex + 2, 88], fill=(20, 20, 20))
        d.ellipse([ex + 2, 82, ex + 4, 84], fill=(255, 255, 255))
        d.arc([ex - 8, 80, ex + 8, 90], 180, 360, fill=(60, 32, 22), width=1)
    # nose: soft shadow + nostrils
    d.line([(cx + 1, 88), (cx - 1, 102)], fill=(190, 138, 104), width=2)
    d.ellipse([cx - 5, 102, cx - 1, 106], fill=(170, 116, 86))
    d.ellipse([cx + 1, 102, cx + 5, 106], fill=(170, 116, 86))
    # lips
    d.polygon([(cx - 10, 112), (cx, 109), (cx + 10, 112), (cx, 116)],
              fill=(168, 95, 82))
    d.line([(cx - 10, 112), (cx + 10, 112)], fill=(140, 74, 62), width=1)
    # freckles across nose and cheeks
    for fx, fy in [(-14, 96), (-9, 99), (-20, 92), (14, 96), (9, 99),
                   (20, 92), (-4, 97), (4, 97), (-12, 104), (12, 104)]:
        d.point((cx + fx, fy), fill=(150, 96, 60))
    # grain + vignette
    for _ in range(320):
        x, y = rng.randrange(pw), rng.randrange(ph)
        v = rng.randrange(0, 40)
        d.point((x, y), fill=(v, v, v, 8))
    vig = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    vd.rectangle([0, 0, pw, 8], fill=(0, 0, 0, 18))
    vd.rectangle([0, ph - 8, pw, ph], fill=(0, 0, 0, 18))
    img = Image.alpha_composite(img, vig)
    return img.convert("RGB")


# ---------------------------------------------------------------- coat of arms
def draw_arms(d, cx, cy, s):
    """Valdoria arms: green shield, three white peaks, gold star, river."""
    w, h = int(44 * s), int(52 * s)
    x0, y0 = cx - w // 2, cy - h // 2
    shield = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h - 14),
              (cx, y0 + h), (x0, y0 + h - 14)]
    d.polygon(shield, fill=GREEN, outline=GOLD, width=2)
    d.polygon([(cx - 16 * s, y0 + 34 * s), (cx - 8 * s, y0 + 16 * s),
               (cx, y0 + 34 * s)], fill=(245, 242, 230))
    d.polygon([(cx - 4 * s, y0 + 34 * s), (cx + 6 * s, y0 + 12 * s),
               (cx + 16 * s, y0 + 34 * s)], fill=(245, 242, 230))
    d.line([(x0 + 4, y0 + h - 10), (x0 + w - 4, y0 + h - 10)],
           fill=(245, 242, 230), width=2)
    # star
    r = 5 * s
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), y0 + 8 * s + rr * math.sin(ang)))
    d.polygon(pts, fill=GOLD)


# ---------------------------------------------------------------- stamps
def arc_text(d, cx, cy, r, text, f, a0, a1, fill):
    """Draw text along an arc (angles in degrees, 0 = east, ccw negative)."""
    n = len(text)
    for i, ch in enumerate(text):
        a = math.radians(a0 + (a1 - a0) * (i / max(n - 1, 1)))
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        # rotate each glyph tangentially
        glyph = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((20 - gd.textlength(ch, font=f) / 2, 12), ch, font=f, fill=fill)
        glyph = glyph.rotate(math.degrees(a) + 90, resample=Image.BICUBIC,
                             center=(20, 20))
        d._image.paste(glyph, (int(x - 20), int(y - 20)), glyph)


def make_stamp(country, kind, date, code, color, angle, size=(216, 150)):
    """An oval border-control stamp, drawn on its own layer then rotated."""
    w, h = size
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = layer.width // 2, layer.height // 2
    rx, ry = w // 2, h // 2
    for inset, wd in ((0, 3), (7, 1)):
        d.ellipse([cx - rx + inset, cy - ry + inset, cx + rx - inset,
                   cy + ry - inset], outline=color + (255,), width=wd)
    arc_text(d, cx, cy, ry - 20, country, font("sans_b", 15),
             -155, -25, color + (255,))
    d.line([(cx - rx + 16, cy - 8), (cx + rx - 16, cy - 8)],
           fill=color + (255,), width=1)
    text_c(d, cx, cy - 2, kind, font("sans_b", 17), color + (255,))
    text_c(d, cx, cy + 18, date, font("mono_b", 15), color + (255,))
    d.line([(cx - rx + 16, cy + 38), (cx + rx - 16, cy + 38)],
           fill=color + (255,), width=1)
    text_c(d, cx, cy + 44, code, font("mono", 10), color + (255,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    # fade the ink a little: real stamps are never perfectly solid
    alpha = layer.split()[3].point(lambda a: int(a * 0.92))
    layer.putalpha(alpha)
    return layer


def make_exit_stamp(date, color, angle):
    w, h = 118, 40
    layer = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([12, 12, 12 + w, 12 + h], outline=color + (255,), width=2)
    text_c(d, 12 + w // 2, 15, "EXIT", font("sans_b", 11), color + (255,))
    text_c(d, 12 + w // 2, 30, date, font("mono_b", 12), color + (255,))
    return layer.rotate(angle, resample=Image.BICUBIC, expand=True)


def make_fee_stamp():
    w, h = 190, 52
    layer = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([12, 12, 12 + w, 12 + h], outline=STAMP_RED + (255,), width=2)
    d.rectangle([16, 16, 12 + w - 4, 12 + h - 4], outline=STAMP_RED + (255,),
                width=1)
    text_c(d, 12 + w // 2, 17, "FEE PAID  ·  40 KORUN", font("sans_b", 12),
           STAMP_RED + (255,))
    text_c(d, 12 + w // 2, 34, "GUIDE PERMIT  ·  19 AUG 2024",
           font("mono", 10), STAMP_RED + (255,))
    return layer.rotate(-5, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------- guilloche
def guilloche(base, box, color=(90, 110, 120), alpha=11, step=6):
    """Fine wavy security lines across a page region."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    y = y0 + 4
    while y < y1:
        pts = []
        for x in range(x0, x1 + 1, 5):
            pts.append((x, y + 4 * math.sin((x - x0) / 22.0 + y / 31.0)))
        d.line(pts, fill=color + (alpha,), width=1)
        y += step
    comp = Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB")
    base.paste(comp)


def signature(d, x, y, scale=1.0):
    """Holder's signature: one flowing pen stroke."""
    pts = []
    for t in range(0, 101):
        px = x + t * 1.15 * scale
        py = (y + 6 * math.sin(t / 9.0) * math.exp(-t / 60.0)
              - 8 * math.sin(t / 4.0) * (t / 100.0))
        pts.append((px, py))
    d.line(pts, fill=(40, 50, 90), width=2)
    d.line([(x + 96 * scale, y + 2), (x + 118 * scale, y - 6)],
           fill=(40, 50, 90), width=2)


# ---------------------------------------------------------------- pages
def data_page(img, d):
    x0, y0, x1, y1 = 20, 20, 502, 1004
    d.rectangle([x0, y0, x1, y1], fill=PAPER, outline=(120, 110, 88), width=1)
    guilloche(img, (x0 + 2, y0 + 2, x1 - 2, y1 - 2))
    d = ImageDraw.Draw(img)

    # header: arms + country name
    draw_arms(d, 90, 62, 0.9)
    text(d, 128, 40, "REPUBLIC OF VALDORIA", font("serif_b", 20), GREEN)
    text(d, 128, 66, "REPUBLIKA VALDORIA  ·  PASAPORTA", font("sans_b", 10),
         MUTE)
    d.line([(44, 96), (478, 96)], fill=RULE, width=1)
    d.line([(44, 100), (478, 100)], fill=RULE, width=1)
    text_c(d, 261, 110, "PASSPORT  ·  TYPE P  ·  CODE VLD  ·  No. VD 0417823",
           font("sans_b", 11), INK)

    # photo
    px, py, pw, ph = 44, 140, 150, 200
    photo = draw_portrait(pw, ph)
    img.paste(photo, (px, py))
    d.rectangle([px, py, px + pw, py + ph], outline=INK, width=1)
    d.rectangle([px - 3, py - 3, px + pw + 3, py + ph + 3], outline=RULE,
                width=1)
    text_c(d, px + pw // 2, py + ph + 8, "PHOTOGRAPH", font("sans", 8), MUTE)

    # data fields, right of the photo
    fields = [
        ("SURNAME", "VOSS"),
        ("GIVEN NAMES", "ELENA MARIS"),
        ("NATIONALITY", "VALDORIAN"),
        ("DATE OF BIRTH", "14 MAR 1994"),
        ("PLACE OF BIRTH", "KALDRIS, VALDORIA"),
        ("SEX", "F"),
    ]
    fy = 140
    for label, value in fields:
        text(d, 212, fy, label, font("sans_b", 9), MUTE)
        text(d, 212, fy + 12, value, font("sans_b", 14), INK)
        fy += 34
    # issue / expiry / authority, full width under the photo
    d.line([(44, 372), (478, 372)], fill=RULE, width=1)
    cols = [("DATE OF ISSUE", ["12 JUN 2024"], 44),
            ("DATE OF EXPIRY", ["11 JUN 2034"], 196),
            ("AUTHORITY", ["MINISTRY OF THE", "INTERIOR — KALDRIS"], 348)]
    for label, lines, cx in cols:
        text(d, cx, 384, label, font("sans_b", 9), MUTE)
        ly = 396
        for value in lines:
            text(d, cx, ly, value, font("sans_b", 12), INK)
            ly += 14
    d.line([(44, 440), (478, 440)], fill=RULE, width=1)

    # occupation + signature
    text(d, 44, 452, "OCCUPATION", font("sans_b", 9), MUTE)
    text(d, 44, 464, "MOUNTAIN GUIDE  ·  LIC. No. MG-2214",
         font("sans_b", 13), INK)
    text(d, 44, 496, "HOLDER'S SIGNATURE", font("sans_b", 9), MUTE)
    signature(d, 44, 516, 1.5)
    d.line([(44, 530), (330, 530)], fill=RULE, width=1)

    # small printed note: the passport's own fine print
    note = ("This passport is the property of the Republic of Valdoria. "
            "If found, please return it to the nearest Valdorian mission "
            "or to the Ministry of the Interior, Kaldris.")
    y = 556
    for line in wrap(d, note, font("sans", 9), 434):
        text(d, 44, y, line, font("sans", 9), MUTE)
        y += 13

    # physical description (agrees with the portrait) + observations
    d.line([(44, 612), (478, 612)], fill=RULE, width=1)
    phys = [("HEIGHT", "168 cm", 44), ("EYES", "GREEN", 196),
            ("HAIR", "AUBURN", 348)]
    for label, value, cx in phys:
        text(d, cx, 624, label, font("sans_b", 9), MUTE)
        text(d, cx, 636, value, font("sans_b", 12), INK)
    d.line([(44, 668), (478, 668)], fill=RULE, width=1)
    text(d, 44, 680, "OBSERVATIONS", font("sans_b", 9), MUTE)
    obs = ("Holder is exempt from the Brennar harbour tax under the "
           "2019 Treaty of Vesk Pass. Previous passport No. VD 0093117, "
           "issued 14 MAY 2014, surrendered on issue of this passport.")
    y = 694
    for line in wrap(d, obs, font("sans", 10), 434):
        text(d, 44, y, line, font("sans", 10), INK)
        y += 14

    # perforated passport number (single row of punched dots, top edge)
    for i in range(9):
        cx = 60 + i * 46
        d.ellipse([cx - 1, 25, cx + 1, 27], fill=(150, 140, 120))

    # MRZ
    d.rectangle([36, 930, 486, 984], fill=(232, 226, 208))
    l1, l2 = mrz_lines()
    text(d, 44, 938, l1, font("mono", 15), INK)
    text(d, 44, 960, l2, font("mono", 15), INK)
    text_c(d, 261, 906, "—  MACHINE READABLE ZONE  —", font("sans", 8), MUTE)


def visas_page(img, d):
    x0, y0, x1, y1 = 522, 20, 1004, 1004
    d.rectangle([x0, y0, x1, y1], fill=PAPER2, outline=(120, 110, 88), width=1)
    guilloche(img, (x0 + 2, y0 + 2, x1 - 2, y1 - 2))
    d = ImageDraw.Draw(img)
    text_c(d, 763, 40, "VISAS", font("serif_b", 20), GREEN)
    text_c(d, 763, 66, "VIZAT  ·  PAGE 12", font("sans_b", 10), MUTE)
    d.line([(546, 96), (980, 96)], fill=RULE, width=1)
    d.line([(546, 100), (980, 100)], fill=RULE, width=1)

    stamps = [
        # country, kind, date, code, colour, angle, cell x, cell y, exit date
        ("OSTARA", "ENTRY", "28 JUN 2024", "KALDRIS BCP · 014", STAMP_BLUE,
         -7, 546, 122, "11 JUL 2024"),
        ("TALYRIA", "ENTRY", "12 JUL 2024", "VESK PASS · 207", STAMP_GREEN,
         5, 762, 122, "02 AUG 2024"),
        ("BRENNAR", "ENTRY", "03 AUG 2024", "FREE PORT · 031", STAMP_RED,
         -4, 546, 330, "19 AUG 2024"),
        ("VALDORIA", "ENTRY", "19 AUG 2024", "KALDRIS BCP · 014", STAMP_PURPLE,
         6, 762, 330, None),
    ]
    for country, kind, date, code, color, angle, sx, sy, exit_date in stamps:
        stamp = make_stamp(country, kind, date, code, color, angle)
        img.paste(stamp, (sx + 4, sy + 8), stamp)
        if exit_date:
            ex = make_exit_stamp(exit_date, color, -angle)
            img.paste(ex, (sx + 96, sy + 168), ex)
        d = ImageDraw.Draw(img)

    # telling detail: Condition 7 — the mountain-guide endorsement
    d.rectangle([546, 560, 980, 700], outline=GREEN, width=2)
    d.rectangle([550, 564, 976, 696], outline=GREEN, width=1)
    text(d, 566, 576, "CONDITION 7 — ENDORSEMENT", font("sans_b", 12), GREEN)
    cond = ("The holder is a licensed mountain guide (Lic. No. MG-2214). "
            "Guided ascents above 3,000 m require a second licensed "
            "guide on the rope. Valdorian Alpine Code, §12.")
    y = 600
    for line in wrap(d, cond, font("sans", 12), 394):
        text(d, 566, y, line, font("sans", 12), INK)
        y += 17
    text(d, 566, y + 6, "Issued at Kaldris, 12 JUN 2024 — same date as this "
         "passport.", font("sans", 10), MUTE)

    # fee stamp overlapping the endorsement box
    fee = make_fee_stamp()
    img.paste(fee, (700, 668), fee)
    d = ImageDraw.Draw(img)

    # handwritten-style note under the box, in the officer's hand
    text(d, 566, 766, "Permit renewed — see Condition 7.",
         font("serif", 12), (40, 50, 90))

    # page furniture
    d.line([(546, 820), (980, 820)], fill=RULE, width=1)
    text_c(d, 763, 836, "REPUBLIC OF VALDORIA  ·  MINISTRY OF THE INTERIOR",
           font("sans_b", 9), MUTE)
    text_c(d, 763, 856, "This page is valid only with the photograph and the "
           "machine-readable zone on the facing page.",
           font("sans", 9), MUTE)

    # document barcode (official use) fills the foot of the page
    rng = random.Random(417823)
    bx = 660
    for _ in range(52):
        bw = rng.choice((2, 3, 4, 6))
        if rng.random() < 0.62:
            d.rectangle([bx, 900, bx + bw - 1, 946], fill=INK)
        bx += bw + rng.choice((2, 3, 4))
    text_c(d, 763, 952, "VD 0417823  ·  FOR OFFICIAL USE ONLY",
           font("mono", 10), MUTE)


def main():
    os.makedirs("/output", exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # spread shadow + page edges
    d.rectangle([14, 14, 1010, 1010], fill=(10, 16, 17))
    data_page(img, d)
    visas_page(img, d)
    d = ImageDraw.Draw(img)
    # centre gutter shadow
    for i in range(10):
        d.line([(508 + i, 20), (508 + i, 1004)], fill=(0, 0, 0, 18 - i))
        d.line([(516 - i, 20), (516 - i, 1004)], fill=(0, 0, 0, 18 - i))
    img.save(OUT, format="PNG", optimize=True)
    if os.path.getsize(OUT) > 1_048_576:
        img.save(OUT, format="JPEG", quality=88, optimize=True)
    os.chmod(OUT, 0o644)
    print(f"wrote {OUT}: {img.size} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
