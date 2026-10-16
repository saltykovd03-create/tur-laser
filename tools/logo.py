#!/usr/bin/env python3
"""Значок TUR-LASER (3 варианта) и аватар на кадре из видео.
Запуск: python3 tools/logo.py → avito/logo/znachok-*.jpg, avito/profil/13-video-tur-laser.jpg, avito/logo/sheet.jpg"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "avito" / "logo"; LOGO.mkdir(parents=True, exist_ok=True)
PROF = ROOT / "avito" / "profil"
FONT = ROOT / "tools" / "fonts" / "Manrope.ttf"
S = 1024
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255)
RUST = (171, 84, 38); RUST2 = (120, 56, 22); STEEL = (214, 224, 236); INK = (60, 70, 90)

def fnt(size, w=800):
    f = ImageFont.truetype(str(FONT), size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f

def gradient(c1, c2):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((S, S), Image.BILINEAR)

def glow_line(base, p1, p2, core=6, glow=40, color=SKY):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (120,), width=glow)
    layer = layer.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=color + (255,), width=core + 6)
    d.line([p1, p2], fill=WHITE + (255,), width=core)
    base.paste(layer, (0, 0), layer)

def spark(base, c, r=26, color=SKY):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r*2.2, c[1]-r*2.2, c[0]+r*2.2, c[1]+r*2.2), fill=color + (150,))
    layer = layer.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r, c[1]-r, c[0]+r, c[1]+r), fill=WHITE + (255,))
    base.paste(layer, (0, 0), layer)

def name_small(base, cy=800, size=58, fill=WHITE, spacing=10):
    d = ImageDraw.Draw(base); f = fnt(size); text = "TUR-LASER"
    tw = sum(d.textlength(ch, font=f) for ch in text) + spacing * (len(text) - 1)
    x = (S - tw) / 2; l, t, r, b = d.textbbox((0, 0), text, font=f); y = cy - (b - t) / 2 - t
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + spacing

# ---------- 1. Пластина: слева ржавчина, справа чистый металл, между ними луч ----------
def znachok_plastina(with_name=True):
    base = gradient(NAVY, BLUE); d = ImageDraw.Draw(base)
    pw, ph = 620, 230; x0, y0 = (S - pw) // 2, 330 if with_name else 400
    plate = Image.new("RGB", (pw, ph), STEEL); pd = ImageDraw.Draw(plate)
    rnd = random.Random(7)
    split = int(pw * 0.46)
    pd.rectangle((0, 0, split, ph), fill=RUST)
    for _ in range(2600):                       # пятна ржавчины
        x, y = rnd.randint(0, split), rnd.randint(0, ph); r = rnd.randint(2, 9)
        pd.ellipse((x-r, y-r, x+r, y+r), fill=rnd.choice([RUST2, (150, 70, 30), (200, 110, 60)]))
    for i in range(7):                          # «выбитые» знаки: слева тусклые, справа чёткие
        cx = 60 + i * 78; dark = INK if cx > split else (95, 45, 20)
        pd.rounded_rectangle((cx, 85, cx + 44, 145), 8, fill=dark)
    mask = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw-1, ph-1), 36, fill=255)
    base.paste(plate, (x0, y0), mask)
    glow_line(base, (x0 + split, y0 - 70), (x0 + split, y0 + ph + 70), core=7, glow=46)
    spark(base, (x0 + split, y0 - 70), r=16)
    if with_name: name_small(base, cy=720)
    return base

# ---------- 2. Буква T, перекладина — луч ----------
def znachok_bukva_t(with_name=True):
    base = gradient(NAVY, BLUE); d = ImageDraw.Draw(base)
    cx, top = S // 2, 300 if with_name else 340
    d.rounded_rectangle((cx - 52, top + 40, cx + 52, top + 400), 22, fill=WHITE)      # ножка
    glow_line(base, (cx - 250, top), (cx + 250, top), core=14, glow=70)              # перекладина-луч
    spark(base, (cx + 250, top), r=30)
    if with_name: name_small(base, cy=800)
    return base

# ---------- 3. Кольцо-сканер с VIN внутри и лучом ----------
def znachok_skaner(with_name=True):
    base = gradient(NAVY, BLUE); d = ImageDraw.Draw(base)
    cx, cy, R = S // 2, 470 if with_name else 512, 250
    d.arc((cx - R, cy - R, cx + R, cy + R), start=300, end=240, fill=SKY, width=34)  # кольцо с разрывом вверху справа
    f = fnt(150); t = "VIN"; l, tt, r, b = d.textbbox((0, 0), t, font=f)
    d.text((cx - (r - l) / 2 - l, cy - (b - tt) / 2 - tt), t, font=f, fill=WHITE)
    ang = math.radians(300); ex, ey = cx + R * math.cos(ang), cy + R * math.sin(ang)  # точка разрыва
    glow_line(base, (ex + 150, ey - 150), (cx + 60, cy - 50), core=8, glow=44)
    spark(base, (cx + 60, cy - 50), r=18)
    if with_name: name_small(base, cy=800)
    return base

# ---------- аватар на кадре из видео ----------
def avatar_video():
    src = ROOT / "avito" / "08-process.jpg"                   # кадр 628350 ~20 с, уже вырезан и подтянут
    im = Image.open(src).convert("RGB"); w, h = im.size
    m = min(w, h); im = im.crop((0, int((h - m) * 0.35), m, int((h - m) * 0.35) + m)).resize((S, S), Image.LANCZOS)
    im = Image.blend(im.filter(ImageFilter.GaussianBlur(1.5)), Image.new("RGB", (S, S), NAVY), 0.42)
    d = ImageDraw.Draw(im)
    for text, cy, size, fill in (("TUR", 440, 236, WHITE), ("LASER", 624, 236, SKY)):
        f = fnt(size); l, t, r, b = d.textbbox((0, 0), text, font=f)
        sp = 6; tw = (r - l) + sp * (len(text) - 1); x = (S - tw) / 2 - l; y = cy - (b - t) / 2 - t
        for ch in text: d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + sp
    f = fnt(50, 700); t = "ОЧИСТКА VIN ОТ РЖАВЧИНЫ"; l, tt, r, b = d.textbbox((0, 0), t, font=f)
    d.text(((S - (r - l)) / 2 - l, 800 - (b - tt) / 2 - tt), t, font=f, fill=WHITE)
    return im

outs = []
for name, fn in (("znachok-1-plastina", znachok_plastina), ("znachok-2-bukva-t", znachok_bukva_t), ("znachok-3-skaner", znachok_skaner)):
    for wn in (True, False):
        p = LOGO / f"{name}{'' if wn else '-bez-imeni'}.jpg"; fn(wn).save(p, quality=92); outs.append(p)
p = PROF / "13-video-tur-laser.jpg"; avatar_video().save(p, quality=92); outs.append(p)

T = 220; cols = 7
sheet = Image.new("RGB", (cols * T, T + 90), (245, 245, 245))
for i, p in enumerate(outs):
    im = Image.open(p).convert("RGB")
    for size, y in ((160, 20), (64, 200)):
        mk = Image.new("L", (size, size), 0); ImageDraw.Draw(mk).ellipse((0, 0, size-1, size-1), fill=255)
        sheet.paste(im.resize((size, size), Image.LANCZOS), (i * T + (T - size) // 2, y), mk)
sheet.save(LOGO / "sheet.jpg", quality=88)
print("готово:", *[p.name for p in outs], sep="\n  ")
