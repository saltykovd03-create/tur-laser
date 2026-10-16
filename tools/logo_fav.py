#!/usr/bin/env python3
"""Развитие двух понравившихся: ржавые буквы TUR-LASER с лучом и шестиугольник TL.
→ avito/logo/fav-*.jpg|png + fav-sheet.jpg"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "logo"; FD = ROOT / "tools" / "fonts"
S = 1024
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255); RUST = (171, 84, 38)

def fnt(name, size, w=None):
    f = ImageFont.truetype(str(FD / name), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
def gradient(w=S, h=S, c1=NAVY, c2=BLUE):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((w, h), Image.BILINEAR)
def rust_texture(w, h, seed=3):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), RUST); d = ImageDraw.Draw(im)
    for _ in range(max(w * h // 90, 50)):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(2, 9)
        d.ellipse((x-r, y-r, x+r, y+r), fill=rnd.choice([(120, 56, 22), (150, 70, 30), (205, 112, 60), (96, 44, 18)]))
    return im.filter(ImageFilter.GaussianBlur(0.6))
def glow_line(base, p1, p2, core=6, glow=40, color=SKY, core_color=WHITE):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (120,), width=glow)
    layer = layer.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (255,), width=core + 6); d.line([p1, p2], fill=core_color + (255,), width=core)
    base.paste(layer, (0, 0), layer)
def spark(base, c, r=22, color=SKY, core_color=WHITE):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r*2.2, c[1]-r*2.2, c[0]+r*2.2, c[1]+r*2.2), fill=color + (150,))
    layer = layer.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r, c[1]-r, c[0]+r, c[1]+r), fill=core_color + (255,)); base.paste(layer, (0, 0), layer)
def text_mask(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text:
        md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m
def centered_text(base, text, cy, font, fill, spacing=0, cx=None):
    m = text_mask(text, font, spacing); x = int((cx if cx is not None else S / 2) - m.width / 2); y = int(cy - m.height / 2)
    base.paste(Image.new("RGB", m.size, fill), (x, y), m)

def rusty_word(base, font_name, weight, cx, cy, max_w, clean=WHITE, spacing=2, size=150, beam=True, ratio=0.45):
    """Слово TUR-LASER: левая часть ржавая, правая clean, луч на границе. Возвращает (x, y, w, h)."""
    f = fnt(font_name, size, weight); m = text_mask("TUR-LASER", f, spacing)
    if m.width > max_w:
        f = fnt(font_name, int(size * max_w / m.width), weight); m = text_mask("TUR-LASER", f, spacing)
    x, y = int(cx - m.width / 2), int(cy - m.height / 2); split = int(m.width * ratio)
    fill = Image.new("RGB", m.size, clean); fill.paste(rust_texture(split, m.height, 11), (0, 0))
    base.paste(fill, (x, y), m)
    if beam:
        glow_line(base, (x + split, y - int(m.height * 0.6)), (x + split, y + m.height + int(m.height * 0.6)), core=7, glow=46)
        spark(base, (x + split, y - int(m.height * 0.6)), r=16)
    return x, y, m.width, m.height

def hex_tl(base, cx, cy, R, outline=SKY, fill=None, letters=WHITE, beam=SKY, beam_core=WHITE, width=26):
    d = ImageDraw.Draw(base)
    pts = [(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)]
    d.polygon(pts, outline=outline, fill=fill, width=width)
    centered_text(base, "TL", cy + int(R * 0.03), fnt("Unbounded.ttf", int(R * 0.84), 800), letters, 6, cx=cx)
    glow_line(base, (cx + R * 1.32, cy - R * 1.32), (cx + R * 0.28, cy - R * 0.28), core=max(4, R // 36), glow=max(20, R // 6), color=beam, core_color=beam_core)
    spark(base, (cx + R * 0.28, cy - R * 0.28), r=max(8, R // 18), color=beam, core_color=beam_core)

def sub(base, cy, fill=WHITE, size=48): centered_text(base, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", cy, fnt("Manrope.ttf", size, 700), fill)

outs = []
# ржавые буквы в трёх шрифтах
for key, fn, w, sp in (("oswald", "Oswald.ttf", 700, 8), ("russo", "RussoOne-Regular.ttf", None, 6), ("montserrat", "Montserrat.ttf", 800, 4)):
    im = gradient(); rusty_word(im, fn, w, S // 2, 512, 900, spacing=sp); sub(im, 740, size=44)
    p = OUT / f"fav-bukvy-{key}.jpg"; im.save(p, quality=92); outs.append(p)
# ржавые буквы на белом
im = Image.new("RGB", (S, S), WHITE); rusty_word(im, "Unbounded.ttf", 800, S // 2, 512, 900, clean=NAVY); sub(im, 740, fill=NAVY, size=44)
p = OUT / "fav-bukvy-belyy.jpg"; im.save(p, quality=92); outs.append(p)
# шестиугольник: залитый голубым
im = gradient(); hex_tl(im, S // 2, 440, 250, outline=SKY, fill=SKY, letters=NAVY, beam=WHITE, beam_core=WHITE)
centered_text(im, "TUR-LASER", 790, fnt("Manrope.ttf", 60, 800), WHITE, 8); p = OUT / "fav-shildik-zalivka.jpg"; im.save(p, quality=92); outs.append(p)
# шестиугольник на белом
im = Image.new("RGB", (S, S), WHITE); hex_tl(im, S // 2, 440, 250, outline=NAVY, letters=NAVY, beam=SKY, beam_core=(30, 110, 220))
centered_text(im, "TUR-LASER", 790, fnt("Manrope.ttf", 60, 800), NAVY, 8); p = OUT / "fav-shildik-belyy.jpg"; im.save(p, quality=92); outs.append(p)
# шестиугольник, где буквы TL наполовину ржавые (два любимых в одном)
im = gradient(); d = ImageDraw.Draw(im); cx, cy, R = S // 2, 440, 250
pts = [(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)]
d.polygon(pts, outline=SKY, width=26)
f = fnt("Unbounded.ttf", 210, 800); m = text_mask("TL", f, 6); x, y = cx - m.width // 2, cy + 8 - m.height // 2; split = int(m.width * 0.5)
fill = Image.new("RGB", m.size, WHITE); fill.paste(rust_texture(split, m.height, 17), (0, 0)); im.paste(fill, (x, y), m)
glow_line(im, (x + split, cy - R - 60), (x + split, cy + R + 60), core=7, glow=44); spark(im, (x + split, cy - R - 60), r=16)
centered_text(im, "TUR-LASER", 790, fnt("Manrope.ttf", 60, 800), WHITE, 8); p = OUT / "fav-shildik-rzhavyy.jpg"; im.save(p, quality=92); outs.append(p)
# горизонтальные версии для шапки сайта, прозрачный фон
for key, bg_dark in (("tyomnyy", True), ("svetlyy", False)):
    W, H = 1800, 600; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rgb = Image.new("RGB", (W, H), NAVY if bg_dark else WHITE)
    hex_tl(rgb, 300, 300, 200, outline=SKY if bg_dark else NAVY, letters=WHITE if bg_dark else NAVY, beam=SKY, beam_core=WHITE if bg_dark else (30, 110, 220), width=22)
    rusty_word(rgb, "Unbounded.ttf", 800, 1130, 270, 1150, clean=WHITE if bg_dark else NAVY, size=170, beam=False)
    centered_text(rgb, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 440, fnt("Manrope.ttf", 54, 700), SKY if bg_dark else NAVY, cx=1130)
    # прозрачность: всё, что совпало с фоном, убираем
    bgc = NAVY if bg_dark else WHITE; px = rgb.load(); ap = im.load()
    for yy in range(H):
        for xx in range(W):
            c = px[xx, yy]
            if abs(c[0]-bgc[0]) + abs(c[1]-bgc[1]) + abs(c[2]-bgc[2]) > 24: ap[xx, yy] = c + (255,)
    p = OUT / f"fav-shapka-{key}.png"; im.save(p); outs.append(p)
    rgb.save(OUT / f"fav-shapka-{key}-preview.jpg", quality=90)

T = 220; sq = [p for p in outs if p.suffix == ".jpg"]
sheet = Image.new("RGB", (len(sq) * T, T + 90 + 240), (245, 245, 245))
for i, p in enumerate(sq):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
for i, key in enumerate(("tyomnyy", "svetlyy")):
    im = Image.open(OUT / f"fav-shapka-{key}-preview.jpg").convert("RGB").resize((720, 240), Image.LANCZOS); sheet.paste(im, (i * 760 + 20, T + 90))
sheet.save(OUT / "fav-sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
