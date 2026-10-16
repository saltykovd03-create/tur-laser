#!/usr/bin/env python3
"""Карточки для ролика 1080×1920: заставка, концовка, подпись «ускорено». → avito/video_cards/"""
import sys
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "video_cards"; OUT.mkdir(parents=True, exist_ok=True); FD = ROOT / "tools" / "fonts"
W, H = 1080, 1920
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255); RUST = (171, 84, 38)
def fnt(name, size, w=None):
    f = ImageFont.truetype(str(FD / name), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
def gradient():
    g = Image.new("RGB", (2, 2)); g.putdata([NAVY, NAVY, BLUE, BLUE]); return g.resize((W, H), Image.BILINEAR)
def rust_texture(w, h, seed=29):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), RUST); d = ImageDraw.Draw(im)
    for _ in range(max(w * h // 90, 50)):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(2, 9)
        d.ellipse((x-r, y-r, x+r, y+r), fill=rnd.choice([(120, 56, 22), (150, 70, 30), (205, 112, 60), (96, 44, 18)]))
    return im.filter(ImageFilter.GaussianBlur(0.6))
def glow_line(base, p1, p2, core=6, glow=40):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (120,), width=glow); layer = layer.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (255,), width=core + 6); d.line([p1, p2], fill=WHITE + (255,), width=core); base.paste(layer, (0, 0), layer)
def spark(base, c, r=16):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r*2.2, c[1]-r*2.2, c[0]+r*2.2, c[1]+r*2.2), fill=SKY + (150,)); layer = layer.filter(ImageFilter.GaussianBlur(18)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r, c[1]-r, c[0]+r, c[1]+r), fill=WHITE + (255,)); base.paste(layer, (0, 0), layer)
def text_mask(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text: md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m
def put(base, text, cy, font, fill, spacing=0):
    m = text_mask(text, font, spacing); base.paste(Image.new("RGB", m.size, fill), ((W - m.width) // 2, int(cy - m.height / 2)), m); return m.size
def wordmark(base, cy, size, max_w, beam=True):
    f = fnt("Unbounded.ttf", size, 800); m = text_mask("TUR-LASER", f, 2)
    if m.width > max_w: f = fnt("Unbounded.ttf", int(size * max_w / m.width), 800); m = text_mask("TUR-LASER", f, 2)
    x, y = (W - m.width) // 2, int(cy - m.height / 2)
    ramp = Image.linear_gradient("L").rotate(90, expand=True).resize(m.size).point(lambda v: 0 if v < 70 else 255 if v > 150 else int((v - 70) * 255 / 80))
    base.paste(Image.composite(Image.new("RGB", m.size, WHITE), rust_texture(m.width, m.height), ramp), (x, y), m)
    if beam:
        sx = x + int(m.width * 0.43); glow_line(base, (sx, y - int(m.height * 0.8)), (sx, y + m.height + int(m.height * 0.8)), core=6, glow=40); spark(base, (sx, y - int(m.height * 0.8)), r=14)
    return y, m.height

title = gradient(); y, h = wordmark(title, 900, 150, 960)
put(title, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", y + h + 110, fnt("Manrope.ttf", 44, 700), WHITE)
put(title, "Санкт-Петербург и область", y + h + 175, fnt("Manrope.ttf", 36, 600), SKY)
title.save(OUT / "title.png")

end = gradient(); y, h = wordmark(end, 640, 110, 820, beam=False)
put(end, "+7 950 254-55-50", 900, fnt("Unbounded.ttf", 84, 800), WHITE)
put(end, "Вячеслав", 820, fnt("Manrope.ttf", 40, 700), SKY)
put(end, "Санкт-Петербург и область", 1010, fnt("Manrope.ttf", 40, 700), WHITE)
put(end, "выезд 30 минут · чистка 10 минут", 1075, fnt("Manrope.ttf", 38, 600), SKY)
put(end, "Telegram: @auto_slav", 1200, fnt("Manrope.ttf", 40, 700), WHITE)
end.save(OUT / "end.png")

cap = Image.new("RGBA", (620, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(cap)
d.rounded_rectangle((0, 0, 619, 109), 55, fill=(8, 22, 54, 200)); f = fnt("Manrope.ttf", 44, 800); t = f"чистка · ускорено ×{sys.argv[1] if len(sys.argv) > 1 else 8}"
l, tt, r, b = d.textbbox((0, 0), t, font=f); d.text(((620 - (r - l)) / 2 - l, (110 - (b - tt)) / 2 - tt), t, font=f, fill=WHITE + (255,))
cap.save(OUT / "caption.png")
print("cards ok")
