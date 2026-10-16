#!/usr/bin/env python3
"""Аватар для профиля Авито: квадрат 1024, текст внутри круга (Авито режет фото профиля в кружок).
Запуск: python3 tools/profil.py → avito/profil/*.jpg + sheet.jpg (как выглядит в кружках)."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "profil"; OUT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / "tools" / "fonts" / "Manrope.ttf"
S = 1024; R = 470                      # радиус «безопасного» круга
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255)

def fnt(size, w=800):
    f = ImageFont.truetype(str(FONT), size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f

def width_at(y):
    """Доступная ширина строки на высоте y внутри круга (с запасом 40 px)."""
    dy = abs(y - S / 2)
    return 2 * math.sqrt(max(R * R - dy * dy, 0)) - 40

def fit(d, text, y_center, max_size, w=800):
    size = max_size
    while size > 20:
        f = fnt(size, w)
        if d.textlength(text, font=f) <= width_at(y_center): return f
        size -= 4
    return fnt(size, w)

def put(d, text, cy, max_size, fill, w=800, spacing=0):
    f = fit(d, text, cy, max_size, w)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    tw = (r - l) + spacing * (len(text) - 1)
    x = (S - tw) / 2 - l; y = cy - (b - t) / 2 - t
    if spacing:
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing
    else:
        d.text((x, y), text, font=f, fill=fill)

def gradient(c1, c2):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((S, S), Image.BILINEAR)

def photo_bg(name, dark=0.45):
    im = ImageOps.exif_transpose(Image.open(ROOT / "img" / "tg" / name)).convert("RGB")
    w, h = im.size; m = min(w, h)
    im = im.crop(((w - m) // 2, int((h - m) * 0.55), (w - m) // 2 + m, int((h - m) * 0.55) + m)).resize((S, S), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(2))
    return Image.blend(im, Image.new("RGB", (S, S), NAVY), dark)

def text_block(base, name=True, fill=WHITE, accent=SKY, name_fill=SKY):
    d = ImageDraw.Draw(base)
    if name:
        put(d, "TUR-LASER", 232, 54, name_fill, w=800, spacing=8)
        put(d, "ОЧИСТКА", 352, 118, fill)
        put(d, "VIN", 522, 300, accent)
        put(d, "ОТ РЖАВЧИНЫ", 736, 104, fill)
    else:
        put(d, "ОЧИСТКА", 318, 128, fill)
        put(d, "VIN", 512, 330, accent)
        put(d, "ОТ РЖАВЧИНЫ", 722, 110, fill)

def name_block(base, style="stack", fill=WHITE, accent=SKY, sub=WHITE, line=False):
    """Имя крупно, услуга мелко. style: stack — TUR / LASER в две строки; line — одной строкой."""
    d = ImageDraw.Draw(base)
    if style == "stack":
        put(d, "TUR", 372, 250, fill, spacing=6)
        put(d, "LASER", 560, 250, accent, spacing=6)
        if line:
            d.rounded_rectangle((S/2 - 200, 672, S/2 + 200, 678), 3, fill=accent)
        put(d, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 740, 54, sub, w=700)
    else:
        put(d, "TUR-LASER", 470, 170, fill, spacing=4)
        if line:
            d.rounded_rectangle((S/2 - 220, 572, S/2 + 220, 578), 3, fill=accent)
        put(d, "ОЧИСТКА VIN", 650, 72, accent, w=700)
        put(d, "ОТ РЖАВЧИНЫ", 740, 72, sub, w=700)


variants = {
    "7-siniy-tur-laser-dve-stroki":  (lambda: gradient(NAVY, BLUE), dict(_name=True, style="stack")),
    "8-siniy-tur-laser-odna-stroka": (lambda: gradient(NAVY, BLUE), dict(_name=True, style="line", line=True)),
    "9-foto-tur-laser":              (lambda: photo_bg("628342.jpg", 0.55), dict(_name=True, style="stack")),
    "10-goluboy-tur-laser":          (lambda: gradient((150, 205, 255), (96, 168, 245)), dict(_name=True, style="line", fill=NAVY, accent=WHITE, sub=NAVY, line=True)),
    "11-belyy-tur-laser":            (lambda: Image.new("RGB", (S, S), WHITE), dict(_name=True, style="stack", fill=NAVY, accent=(30, 110, 220), sub=NAVY)),
    "12-siniy-tur-laser-luch":       (lambda: gradient(NAVY, BLUE), dict(_name=True, style="stack", line=True)),
    "1-siniy-s-imenem":   (lambda: gradient(NAVY, BLUE), dict(name=True)),
    "2-siniy-bez-imeni":  (lambda: gradient(NAVY, BLUE), dict(name=False)),
    "3-foto-s-imenem":    (lambda: photo_bg("628336.jpg", 0.5), dict(name=True)),
    "4-foto-bez-imeni":   (lambda: photo_bg("628342.jpg", 0.5), dict(name=False)),
    "5-goluboy-s-imenem": (lambda: gradient((150, 205, 255), (96, 168, 245)), dict(name=True, fill=NAVY, accent=WHITE, name_fill=NAVY)),
    "6-belyy-bez-imeni":  (lambda: Image.new("RGB", (S, S), WHITE), dict(name=False, fill=NAVY, accent=(30, 110, 220))),
}
files = []
for key, (bg, kw) in variants.items():
    im = bg()
    if kw.pop("_name", False): name_block(im, **kw)
    else: text_block(im, **kw)
    p = OUT / f"{key}.jpg"; im.save(p, quality=92); files.append(p)

# лист: как выглядит в кружках 160 и 64 px (размеры аватара в приложении и в ленте)
T = 220; cols = 6; rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * T, rows * (T + 90)), (245, 245, 245))
for i, p in enumerate(files):
    im = Image.open(p).convert("RGB"); cx = (i % cols) * T; cy = (i // cols) * (T + 90)
    for size, y in ((160, 20), (64, 200)):
        m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
        sm = im.resize((size, size), Image.LANCZOS)
        sheet.paste(sm, (cx + (T - size) // 2, cy + y), m)
sheet.save(OUT / "sheet.jpg", quality=88)
print("готово:", *[p.name for p in files], sep="\n  ")
