#!/usr/bin/env python3
"""Логотипы, серия 3. → avito/logo/logo3-*.jpg + logo3-sheet.jpg"""
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
def rust_texture(w, h, seed=3):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), RUST); d = ImageDraw.Draw(im)
    for _ in range(max(w * h // 90, 50)):
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
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text:
        md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m
def centered_text(base, text, cy, font, fill, spacing=0, cx=None):
    m = text_mask(text, font, spacing); x = int((cx or S / 2) - m.width / 2); y = int(cy - m.height / 2)
    base.paste(Image.new("RGB", m.size, fill), (x, y), m)
def name(base, cy=800, size=60, fill=WHITE): centered_text(base, "TUR-LASER", cy, fnt("Manrope.ttf", size, 800), fill, 8)

# 1. Буква T: верх ржавый, низ чистый, луч поперёк
def letter_half():
    base = gradient(); f = fnt("Unbounded.ttf", 520, 800); m = text_mask("T", f)
    x, y = (S - m.width) // 2, 440 - m.height // 2; split = int(m.height * 0.42)
    fill = Image.new("RGB", m.size, WHITE); fill.paste(rust_texture(m.width, split, 21), (0, 0))
    base.paste(fill, (x, y), m)
    glow_line(base, (x - 120, y + split), (x + m.width + 120, y + split), core=8, glow=50); spark(base, (x + m.width + 120, y + split), r=18)
    name(base, 820)
    p = OUT / "logo3-bukva-t-popolam.jpg"; base.save(p, quality=92); return p

# 2. VIN с косым разрезом: слева-сверху ржавчина, справа-снизу чистое
def vin_slash():
    base = gradient(); f = fnt("Unbounded.ttf", 300, 800); m = text_mask("VIN", f, 4)
    x, y = (S - m.width) // 2, 470 - m.height // 2
    fill = Image.new("RGB", m.size, WHITE); rust = rust_texture(m.width, m.height, 31)
    cut = Image.new("L", m.size, 0); ImageDraw.Draw(cut).polygon([(0, 0), (int(m.width * 0.62), 0), (int(m.width * 0.38), m.height), (0, m.height)], fill=255)
    fill.paste(rust, (0, 0), cut); base.paste(fill, (x, y), m)
    p1 = (x + int(m.width * 0.62) + 60, y - 90); p2 = (x + int(m.width * 0.38) - 60, y + m.height + 90)
    glow_line(base, p1, p2, core=8, glow=50); spark(base, p1, r=16)
    name(base, 800)
    p = OUT / "logo3-vin-razrez.jpg"; base.save(p, quality=92); return p

# 3. Щит с пластиной и лентой
def shield():
    base = gradient(); d = ImageDraw.Draw(base); cx, top, w, h = S // 2, 170, 560, 640
    pts = [(cx - w/2, top), (cx + w/2, top), (cx + w/2, top + h*0.55), (cx, top + h), (cx - w/2, top + h*0.55)]
    d.polygon(pts, fill=(14, 46, 104), outline=SKY, width=22)
    pw, ph = 380, 120; px, py = cx - pw // 2, top + 150
    plate = Image.new("RGB", (pw, ph), STEEL); plate.paste(rust_texture(int(pw * 0.46), ph, 41), (0, 0))
    pd = ImageDraw.Draw(plate)
    for i in range(6):
        lx = 26 + i * 58; pd.rounded_rectangle((lx, 38, lx + 30, 82), 6, fill=INK if lx > pw * 0.46 else (95, 45, 20))
    mk = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, pw-1, ph-1), 20, fill=255)
    base.paste(plate, (px, py), mk)
    glow_line(base, (px + int(pw * 0.46), py - 50), (px + int(pw * 0.46), py + ph + 50), core=6, glow=36)
    # лента
    ry = top + 360; d.polygon([(cx - 330, ry - 50), (cx + 330, ry - 50), (cx + 300, ry + 50), (cx - 300, ry + 50)], fill=SKY)
    centered_text(base, "TUR-LASER", ry, fnt("Manrope.ttf", 58, 800), NAVY, 6)
    centered_text(base, "VIN", top + 500, fnt("Unbounded.ttf", 90, 800), WHITE)
    p = OUT / "logo3-shchit.jpg"; base.save(p, quality=92); return p

# 4. Иконка приложения: скруглённый квадрат, T и луч-точка
def app_icon():
    base = gradient(); d = ImageDraw.Draw(base); a = 560; x0, y0 = (S - a) // 2, 170
    d.rounded_rectangle((x0, y0, x0 + a, y0 + a), 120, fill=SKY)
    centered_text(base, "T", y0 + a // 2 + 10, fnt("Unbounded.ttf", 380, 800), NAVY, cx=S // 2 - 30)
    glow_line(base, (x0 + a - 60, y0 + 60), (S // 2 + 120, y0 + a // 2 - 60), core=8, glow=44, color=WHITE); spark(base, (S // 2 + 120, y0 + a // 2 - 60), r=16, color=WHITE)
    name(base, 830)
    p = OUT / "logo3-ikonka.jpg"; base.save(p, quality=92); return p

# 5. Прицел лазера
def crosshair():
    base = gradient(); d = ImageDraw.Draw(base); cx, cy, R = S // 2, 440, 230
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=SKY, width=18)
    d.ellipse((cx - R//2, cy - R//2, cx + R//2, cy + R//2), outline=SKY, width=10)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.line([(cx + dx * (R // 2 - 40), cy + dy * (R // 2 - 40)), (cx + dx * (R + 50), cy + dy * (R + 50))], fill=SKY, width=14)
    spark(base, (cx, cy), r=24)
    centered_text(base, "VIN", cy + R + 110, fnt("Unbounded.ttf", 96, 800), WHITE)
    name(base, 880, 52)
    p = OUT / "logo3-pritsel.jpg"; base.save(p, quality=92); return p

# 6. Силуэт машины и луч в порог
def car():
    base = gradient(); d = ImageDraw.Draw(base); cx, gy = S // 2, 560
    body = [(cx-330, gy), (cx-330, gy-90), (cx-250, gy-110), (cx-170, gy-230), (cx+90, gy-230), (cx+230, gy-120), (cx+330, gy-100), (cx+330, gy)]
    d.polygon(body, fill=WHITE)
    for wx in (cx-190, cx+190): d.ellipse((wx-70, gy-70, wx+70, gy+70), fill=NAVY); d.ellipse((wx-62, gy-62, wx+62, gy+62), fill=WHITE); d.ellipse((wx-30, gy-30, wx+30, gy+30), fill=NAVY)
    d.polygon([(cx-150, gy-215), (cx-95, gy-130), (cx+60, gy-130), (cx+60, gy-215)], fill=NAVY)      # стёкла
    d.rounded_rectangle((cx-60, gy-40, cx+60, gy-12), 8, fill=INK)                                       # табличка VIN на пороге
    glow_line(base, (cx + 300, gy - 420), (cx, gy - 26), core=7, glow=44); spark(base, (cx, gy - 26), r=18)
    name(base, 800)
    p = OUT / "logo3-mashina.jpg"; base.save(p, quality=92); return p

outs = [letter_half(), vin_slash(), shield(), app_icon(), crosshair(), car()]
T = 220; sheet = Image.new("RGB", (len(outs) * T, T + 90), (245, 245, 245))
for i, p in enumerate(outs):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
sheet.save(OUT / "logo3-sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
