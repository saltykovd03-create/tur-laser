#!/usr/bin/env python3
"""Аватар «TUR / LASER + услуга мелко» в разных шрифтах. → avito/profil/shrift-*.jpg + shrift-sheet.jpg"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "profil"; FD = ROOT / "tools" / "fonts"
S = 1024; R = 470
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255)
FONTS = {  # имя файла, вес для переменного шрифта, трекинг имени
    "unbounded":  ("Unbounded.ttf", 800, 2),
    "oswald":     ("Oswald.ttf", 700, 10),
    "russo-one":  ("RussoOne-Regular.ttf", None, 6),
    "exo2":       ("Exo2.ttf", 800, 4),
    "montserrat": ("Montserrat.ttf", 800, 4),
    "rubik":      ("Rubik.ttf", 800, 4),
}
SUB = FD / "Manrope.ttf"

def fnt(path, size, w=None):
    f = ImageFont.truetype(str(path), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f

def width_at(y):
    dy = abs(y - S / 2); return 2 * math.sqrt(max(R * R - dy * dy, 0)) - 40

def put(d, text, cy, max_size, fill, path, w=None, spacing=0):
    size = max_size
    while size > 20:
        f = fnt(path, size, w)
        if d.textlength(text, font=f) + spacing * (len(text) - 1) <= width_at(cy): break
        size -= 4
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    tw = (r - l) + spacing * (len(text) - 1); x = (S - tw) / 2 - l; y = cy - (b - t) / 2 - t
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing

def gradient(c1, c2):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((S, S), Image.BILINEAR)

outs = []
for key, (fname, w, sp) in FONTS.items():
    im = gradient(NAVY, BLUE); d = ImageDraw.Draw(im); path = FD / fname
    put(d, "TUR", 372, 250, WHITE, path, w, sp)
    put(d, "LASER", 560, 250, SKY, path, w, sp)
    d.rounded_rectangle((S/2 - 200, 672, S/2 + 200, 678), 3, fill=SKY)
    put(d, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 740, 54, WHITE, SUB, 700)
    p = OUT / f"shrift-{key}.jpg"; im.save(p, quality=92); outs.append(p)

T = 220; sheet = Image.new("RGB", (len(outs) * T, T + 90), (245, 245, 245))
for i, p in enumerate(outs):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
sheet.save(OUT / "shrift-sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
