#!/usr/bin/env python3
"""Логотипы, серия 4: акцент на TUR-LASER и монограмму TL. → avito/logo/logo4-*.jpg + logo4-sheet.jpg"""
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
def gradient(c1=NAVY, c2=BLUE):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((S, S), Image.BILINEAR)
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
    base.paste(Image.new("RGB", m.size, fill), (x, y), m); return x, y, m.width, m.height
def name(base, cy=800, fill=WHITE, size=60): centered_text(base, "TUR-LASER", cy, fnt("Manrope.ttf", size, 800), fill, 8)
def hexagon(d, cx, cy, R, **kw):
    d.polygon([(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)], **kw)

# 1. TL: ножка L — луч
def tl_beam_foot():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy = S // 2, 430
    x, y, w, h = centered_text(base, "T", cy, fnt("Unbounded.ttf", 330, 800), WHITE, cx=cx - 120)
    d.rounded_rectangle((cx + 20, y, cx + 90, y + h), 10, fill=WHITE)                  # вертикаль L
    glow_line(base, (cx + 55, y + h - 20), (cx + 330, y + h - 20), core=14, glow=60)   # ножка L — луч
    spark(base, (cx + 330, y + h - 20), r=24)
    name(base, 800)
    p = OUT / "logo4-tl-nozhka-luch.jpg"; base.save(p, quality=92); return p

# 2. TL: перекладина T — луч
def tl_beam_bar():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy = S // 2, 430
    _, y, _, h = centered_text(base, "L", cy, fnt("Unbounded.ttf", 330, 800), WHITE, cx=cx + 120)
    d.rounded_rectangle((cx - 150, y + 10, cx - 70, y + h), 10, fill=WHITE)             # ножка T
    glow_line(base, (cx - 330, y + 12), (cx - 20, y + 12), core=14, glow=60)             # перекладина T — луч
    spark(base, (cx - 330, y + 12), r=24)
    name(base, 800)
    p = OUT / "logo4-tl-perekladina-luch.jpg"; base.save(p, quality=92); return p

# 3. TL в круге
def tl_circle():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 440, 250
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=SKY, width=26)
    centered_text(base, "TL", cy + 8, fnt("Unbounded.ttf", 210, 800), WHITE, 6)
    glow_line(base, (cx + 330, cy - 330), (cx + 70, cy - 70), core=7, glow=40); spark(base, (cx + 70, cy - 70), r=14)
    name(base, 800)
    p = OUT / "logo4-tl-krug.jpg"; base.save(p, quality=92); return p

# 4. TL на голубом квадрате (иконка)
def tl_square():
    base = gradient(); d = ImageDraw.Draw(base); a = 540; x0, y0 = (S - a) // 2, 160
    d.rounded_rectangle((x0, y0, x0 + a, y0 + a), 110, fill=SKY)
    centered_text(base, "TL", y0 + a // 2 + 10, fnt("Unbounded.ttf", 230, 800), NAVY, 6)
    glow_line(base, (x0 + a - 40, y0 + 40), (S // 2 + 90, y0 + a // 2 - 70), core=8, glow=44, color=WHITE); spark(base, (S // 2 + 90, y0 + a // 2 - 70), r=16, color=WHITE)
    name(base, 820)
    p = OUT / "logo4-tl-kvadrat.jpg"; base.save(p, quality=92); return p

# 5. Узкий TL (Oswald) в шестиугольнике, ржавая T
def tl_hex_oswald():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 440, 250
    hexagon(d, cx, cy, R, outline=SKY, width=26)
    f = fnt("Oswald.ttf", 300, 700); m = text_mask("TL", f, 10); x, y = cx - m.width // 2, cy + 6 - m.height // 2; split = int(m.width * 0.5)
    fill = Image.new("RGB", m.size, WHITE); fill.paste(rust_texture(split, m.height, 23), (0, 0)); base.paste(fill, (x, y), m)
    glow_line(base, (x + split, cy - R - 60), (x + split, cy + R + 60), core=7, glow=44); spark(base, (x + split, cy - R - 60), r=16)
    name(base, 800)
    p = OUT / "logo4-tl-hex-oswald.jpg"; base.save(p, quality=92); return p

# 6. TUR / LASER в две строки, луч вместо дефиса
def two_lines_beam():
    base = gradient(); f = fnt("Unbounded.ttf", 230, 800)
    x1, y1, w1, h1 = centered_text(base, "TUR", 360, f, WHITE, 6)
    x2, y2, w2, h2 = centered_text(base, "LASER", 580, f, SKY, 6)
    mid = (y1 + h1 + y2) // 2
    glow_line(base, (S // 2 - 330, mid), (S // 2 + 330, mid), core=8, glow=46); spark(base, (S // 2 + 330, mid), r=18)
    centered_text(base, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 780, fnt("Manrope.ttf", 46, 700), WHITE)
    p = OUT / "logo4-dve-stroki-luch.jpg"; base.save(p, quality=92); return p

# 7. TUR-LASER: ржавчина плавно переходит в чистое
def fade_wordmark():
    base = gradient(); f = fnt("Unbounded.ttf", 150, 800); m = text_mask("TUR-LASER", f, 2)
    if m.width > 900:
        f = fnt("Unbounded.ttf", int(150 * 900 / m.width), 800); m = text_mask("TUR-LASER", f, 2)
    x, y = (S - m.width) // 2, 470 - m.height // 2
    rust = rust_texture(m.width, m.height, 29); white = Image.new("RGB", m.size, WHITE)
    ramp = Image.linear_gradient("L").rotate(90, expand=True).resize(m.size)            # 0 слева (ржавчина) → 255 справа (чистое)
    ramp = ramp.point(lambda v: 0 if v < 70 else 255 if v > 150 else int((v - 70) * 255 / 80))
    fill = Image.composite(white, rust, ramp); base.paste(fill, (x, y), m)
    sx = x + int(m.width * 0.43)
    glow_line(base, (sx, y - 90), (sx, y + m.height + 90), core=7, glow=46); spark(base, (sx, y - 90), r=16)
    centered_text(base, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 700, fnt("Manrope.ttf", 44, 700), WHITE)
    p = OUT / "logo4-perehod-rzhavchiny.jpg"; base.save(p, quality=92); return p

# 8. Имя внутри шестиугольника, две строки
def name_in_hex():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 470, 330
    hexagon(d, cx, cy, R, outline=SKY, width=26)
    f = fnt("Unbounded.ttf", 120, 800)
    x1, y1, w1, h1 = centered_text(base, "TUR", cy - 90, f, WHITE, 6)
    x2, y2, w2, h2 = centered_text(base, "LASER", cy + 70, f, SKY, 6)
    mid = (y1 + h1 + y2) // 2; glow_line(base, (cx - 220, mid), (cx + 220, mid), core=6, glow=36); spark(base, (cx + 220, mid), r=12)
    centered_text(base, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", 880, fnt("Manrope.ttf", 40, 700), WHITE)
    p = OUT / "logo4-imya-v-hex.jpg"; base.save(p, quality=92); return p

outs = [tl_beam_foot(), tl_beam_bar(), tl_circle(), tl_square(), tl_hex_oswald(), two_lines_beam(), fade_wordmark(), name_in_hex()]
T = 220; sheet = Image.new("RGB", (len(outs) * T, T + 90), (245, 245, 245))
for i, p in enumerate(outs):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
sheet.save(OUT / "logo4-sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
