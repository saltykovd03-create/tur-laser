#!/usr/bin/env python3
"""Логотип для шапки сайта: выбранный вариант «ржавчина переходит в чистое» (tools/logo4.py, fade_wordmark),
без подписи, на прозрачном фоне. → img/logo.png. Запуск: python3 tools/logo_shapka.py"""
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
FD = ROOT / "tools" / "fonts"
SKY = (124, 196, 255); WHITE = (255, 255, 255); RUST = (171, 84, 38)
SIZE = 280                 # кегль; в исходнике было ~135 (150, ужатое под 900 px)
K = SIZE / 135             # во столько раз крупнее исходника — так же масштабируем пятна ржавчины и свечение

def fnt(name, size, w=None):
    f = ImageFont.truetype(str(FD / name), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f

def text_mask(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text:
        md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m

def rust_texture(w, h, seed=29):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), RUST); d = ImageDraw.Draw(im)
    for _ in range(max(int(w * h / (90 * K * K)), 50)):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(round(2 * K), round(9 * K))
        d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice([(120, 56, 22), (150, 70, 30), (205, 112, 60), (96, 44, 18)]))
    return im.filter(ImageFilter.GaussianBlur(0.6 * K))

def glow_line(base, p1, p2, core=7, glow=46):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (120,), width=round(glow * K))
    layer = layer.filter(ImageFilter.GaussianBlur(14 * K)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (255,), width=round((core + 6) * K)); d.line([p1, p2], fill=WHITE + (255,), width=round(core * K))
    base.alpha_composite(layer)

def spark(base, c, r=16):
    r = r * K
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0] - r * 2.2, c[1] - r * 2.2, c[0] + r * 2.2, c[1] + r * 2.2), fill=SKY + (150,))
    layer = layer.filter(ImageFilter.GaussianBlur(18 * K)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=WHITE + (255,))
    base.alpha_composite(layer)

f = fnt("Unbounded.ttf", SIZE, 800); m = text_mask("TUR-LASER", f, round(2 * K))
mw, mh = m.size
over = round(90 * K * 0.6)          # луч выходит за буквы; в шапке короче, чем в аватарке (там 90 px при буквах ~110)
pad = round(60 * K)
W, H = mw + 2 * pad, mh + 2 * over + 2 * pad
x, y = pad, pad + over
base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rust = rust_texture(mw, mh); white = Image.new("RGB", m.size, WHITE)
ramp = Image.linear_gradient("L").rotate(90, expand=True).resize(m.size)      # 0 слева (ржавчина) → 255 справа (чистое)
ramp = ramp.point(lambda v: 0 if v < 70 else 255 if v > 150 else int((v - 70) * 255 / 80))
fill = Image.composite(white, rust, ramp).convert("RGBA"); fill.putalpha(m)
base.alpha_composite(fill, (x, y))
sx = x + int(mw * 0.43)
glow_line(base, (sx, y - over), (sx, y + mh + over)); spark(base, (sx, y - over))

# обрезаем по видимому (альфа > 6), оставляя 4 px
a = base.getchannel("A").point(lambda v: 255 if v > 6 else 0); bb = a.getbbox()
crop = (max(0, bb[0] - 4), max(0, bb[1] - 4), min(W, bb[2] + 4), min(H, bb[3] + 4))
out = base.crop(crop)
letters_top = y - crop[1]
out_path = ROOT / "img" / "logo.png"
out.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(out_path, optimize=True)   # палитра: 35 КБ вместо 177
print(f"размер {out.size[0]}x{out.size[1]}; буквы: высота {mh}px, верх на {letters_top}px, доля букв {mh / out.size[1]:.3f}; {out_path.stat().st_size // 1024} КБ")
