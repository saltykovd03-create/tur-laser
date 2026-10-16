#!/usr/bin/env python3
"""Логотипы, серия 2: пластина с выбитым TUR-LASER наполовину под ржавчиной, ржавые буквы без пластины,
шестиугольный шильдик, круглая печать, пиктограмма лазера. → avito/logo/logo2-*.jpg + logo2-sheet.jpg"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "logo"; FD = ROOT / "tools" / "fonts"
S = 1024
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255)
RUST = (171, 84, 38); STEEL = (214, 224, 236); INK = (52, 62, 84)

def fnt(name, size, w=None):
    f = ImageFont.truetype(str(FD / name), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f

def gradient(c1=NAVY, c2=BLUE):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((S, S), Image.BILINEAR)

def rust_texture(w, h, seed=3, base=RUST):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), base); d = ImageDraw.Draw(im)
    for _ in range(w * h // 90):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(2, 9)
        d.ellipse((x-r, y-r, x+r, y+r), fill=rnd.choice([(120, 56, 22), (150, 70, 30), (205, 112, 60), (96, 44, 18)]))
    return im.filter(ImageFilter.GaussianBlur(0.6))

def glow_line(base, p1, p2, core=6, glow=40, color=SKY):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (120,), width=glow)
    layer = layer.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (255,), width=core + 6); d.line([p1, p2], fill=WHITE + (255,), width=core)
    base.paste(layer, (0, 0), layer)

def spark(base, c, r=22, color=SKY):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r*2.2, c[1]-r*2.2, c[0]+r*2.2, c[1]+r*2.2), fill=color + (150,))
    layer = layer.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r, c[1]-r, c[0]+r, c[1]+r), fill=WHITE + (255,)); base.paste(layer, (0, 0), layer)

def text_mask(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text:
        md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m

def centered_text(base, text, cy, font, fill, spacing=0):
    m = text_mask(text, font, spacing); x = (S - m.width) // 2; y = int(cy - m.height / 2)
    base.paste(Image.new("RGB", m.size, fill), (x, y), m)

def sub_line(base, cy=800, text="ОЧИСТКА VIN ОТ РЖАВЧИНЫ", size=48, fill=WHITE):
    centered_text(base, text, cy, fnt("Manrope.ttf", size, 700), fill)

# ---- 1. Пластина с выбитым TUR-LASER, слева ржавчина ----
def plate_stamped(font_name, weight, key):
    base = gradient(); pw, ph = 720, 250; x0, y0 = (S - pw) // 2, 372
    plate = Image.new("RGB", (pw, ph), STEEL)
    split = int(pw * 0.47)
    plate.paste(rust_texture(split, ph, 5), (0, 0))
    f = fnt(font_name, 150, weight); m = text_mask("TUR-LASER", f, 6)
    if m.width > pw - 60:
        k = (pw - 60) / m.width; f = fnt(font_name, int(150 * k), weight); m = text_mask("TUR-LASER", f, 6)
    tx, ty = (pw - m.width) // 2, (ph - m.height) // 2
    # тень «выбитости»: тёмные буквы справа, тусклые и смещённые слева
    letters = Image.new("RGB", m.size, INK); plate.paste(letters, (tx + 3, ty + 3), m)
    plate.paste(Image.new("RGB", m.size, (235, 240, 248)), (tx, ty), m)
    # слева буквы закрыты ржавчиной: перекрываем полупрозрачным слоем ржавчины
    rust_over = rust_texture(split, ph, 9).convert("RGBA"); rust_over.putalpha(120)
    plate.paste(rust_over, (0, 0), rust_over)
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw-1, ph-1), 34, fill=255)
    base.paste(plate, (x0, y0), mask)
    glow_line(base, (x0 + split, y0 - 80), (x0 + split, y0 + ph + 80), core=7, glow=46)
    spark(base, (x0 + split, y0 - 80), r=16)
    sub_line(base, 790)
    base.save(OUT / f"logo2-{key}.jpg", quality=92); return OUT / f"logo2-{key}.jpg"

# ---- 2. Буквы наполовину ржавые, без пластины ----
def rusty_wordmark():
    base = gradient(); f = fnt("Unbounded.ttf", 150, 800); m = text_mask("TUR-LASER", f, 2)
    if m.width > 900:
        k = 900 / m.width; f = fnt("Unbounded.ttf", int(150 * k), 800); m = text_mask("TUR-LASER", f, 2)
    x, y = (S - m.width) // 2, 512 - m.height // 2; split = int(m.width * 0.45)
    fill = Image.new("RGB", m.size, WHITE); fill.paste(rust_texture(split, m.height, 11), (0, 0))
    base.paste(fill, (x, y), m)
    glow_line(base, (x + split, y - 90), (x + split, y + m.height + 90), core=7, glow=46)
    spark(base, (x + split, y - 90), r=16)
    sub_line(base, 740, size=44)
    p = OUT / "logo2-rzhavye-bukvy.jpg"; base.save(p, quality=92); return p

# ---- 3. Шестиугольный шильдик с монограммой TL и лучом ----
def hex_badge():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 440, 250
    pts = [(cx + R * math.cos(math.radians(60 * i - 30)), cy + R * math.sin(math.radians(60 * i - 30))) for i in range(6)]
    d.polygon(pts, outline=SKY, fill=None, width=26)
    centered_text(base, "TL", cy + 8, fnt("Unbounded.ttf", 210, 800), WHITE, 6)
    glow_line(base, (cx + 330, cy - 330), (cx + 70, cy - 70), core=7, glow=40); spark(base, (cx + 70, cy - 70), r=14)
    centered_text(base, "TUR-LASER", 790, fnt("Manrope.ttf", 60, 800), WHITE, 8)
    p = OUT / "logo2-shildik.jpg"; base.save(p, quality=92); return p

# ---- 4. Круглая печать ----
def round_seal():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 512, 330
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=SKY, width=22)
    d.ellipse((cx - R + 60, cy - R + 60, cx + R - 60, cy + R - 60), outline=SKY, width=6)
    centered_text(base, "VIN", cy - 20, fnt("Unbounded.ttf", 190, 800), WHITE)
    centered_text(base, "ОЧИСТКА ЛАЗЕРОМ", cy + 120, fnt("Manrope.ttf", 40, 800), SKY, 3)
    # имя по дуге сверху
    f = fnt("Manrope.ttf", 54, 800); text = "TUR-LASER"; r = R - 30
    total = sum(d.textlength(ch, font=f) for ch in text) + 10 * (len(text) - 1)
    ang = -90 - math.degrees(total / 2 / r)
    for ch in text:
        w = d.textlength(ch, font=f); a = ang + math.degrees((w / 2) / r)
        glyph = Image.new("RGBA", (int(w) + 20, 80), (0, 0, 0, 0)); ImageDraw.Draw(glyph).text((10, 0), ch, font=f, fill=WHITE + (255,))
        glyph = glyph.rotate(-(a + 90), expand=True, resample=Image.BICUBIC)
        gx, gy = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        base.paste(glyph, (int(gx - glyph.width / 2), int(gy - glyph.height / 2)), glyph)
        ang += math.degrees((w + 10) / r)
    p = OUT / "logo2-pechat.jpg"; base.save(p, quality=92); return p

# ---- 5. Пиктограмма лазерной «чистилки» ----
def gun_icon():
    base = gradient(); d = ImageDraw.Draw(base)
    gx, gy = 300, 330
    d.rounded_rectangle((gx, gy, gx + 300, gy + 110), 30, fill=WHITE)                  # корпус
    d.rounded_rectangle((gx + 60, gy + 100, gx + 150, gy + 290), 26, fill=WHITE)        # рукоять
    d.rounded_rectangle((gx + 290, gy + 30, gx + 360, gy + 80), 14, fill=SKY)           # сопло
    glow_line(base, (gx + 360, gy + 55), (gx + 620, gy + 55), core=10, glow=56)         # луч
    spark(base, (gx + 630, gy + 55), r=26)
    # пластина с номером под лучом: слева ржавая, справа чистая
    pw, ph = 560, 120; px, py = 232, 560
    plate = Image.new("RGB", (pw, ph), STEEL); plate.paste(rust_texture(int(pw * 0.5), ph, 13), (0, 0))
    for i in range(8):
        cx = 30 + i * 68; ImageDraw.Draw(plate).rounded_rectangle((cx, 38, cx + 34, 82), 6, fill=INK if cx > pw * 0.5 else (95, 45, 20))
    mk = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, pw-1, ph-1), 24, fill=255)
    base.paste(plate, (px, py), mk)
    centered_text(base, "TUR-LASER", 800, fnt("Manrope.ttf", 60, 800), WHITE, 8)
    p = OUT / "logo2-chistilka.jpg"; base.save(p, quality=92); return p

outs = [plate_stamped("Oswald.ttf", 700, "plastina-tur-laser-oswald"),
        plate_stamped("RussoOne-Regular.ttf", None, "plastina-tur-laser-russo"),
        rusty_wordmark(), hex_badge(), round_seal(), gun_icon()]
T = 220; sheet = Image.new("RGB", (len(outs) * T, T + 90), (245, 245, 245))
for i, p in enumerate(outs):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
sheet.save(OUT / "logo2-sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
