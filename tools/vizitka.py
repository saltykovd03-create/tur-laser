#!/usr/bin/env python3
"""Визитка TUR-LASER 90×50 мм, две стороны. Печать: 300 dpi, вылеты 3 мм (файл 96×56 мм = 1134×661 px),
безопасная зона 3 мм от реза. → avito/vizitka/vizitka-lico.png, vizitka-oborot.png, vizitka.pdf, preview.jpg"""
import random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_M

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "avito" / "vizitka"; OUT.mkdir(parents=True, exist_ok=True); FD = ROOT / "tools" / "fonts"
DPI = 300; MM = DPI / 25.4
W, H = round(96 * MM), round(56 * MM)        # с вылетами
BLEED = round(3 * MM); SAFE = round(6 * MM)   # рез и безопасная зона от края файла
NAVY = (10, 37, 88); BLUE = (16, 52, 118); SKY = (124, 196, 255); WHITE = (255, 255, 255); RUST = (171, 84, 38)
PHONE = "+7 950 254-55-50"
# Мессенджер для QR: по умолчанию MAX. Ссылку на профиль Славы в MAX передать аргументом:
#   python3 tools/vizitka.py https://max.ru/u/XXXXXXXX      (берётся в MAX: профиль → «Пригласить друзей» → «Скопировать ссылку»)
# Без аргумента — запасной вариант с Telegram @auto_slav.
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    QR_URL = sys.argv[1]; QR_LABEL = "Написать в MAX"; QR_SUB = "Telegram: @auto_slav"
else:
    QR_URL = "https://t.me/auto_slav"; QR_LABEL = "Написать в Telegram"; QR_SUB = "@auto_slav"
NAME = "Вячеслав"

def fnt(name, size, w=None):
    f = ImageFont.truetype(str(FD / name), size)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
def gradient(c1=NAVY, c2=BLUE):
    g = Image.new("RGB", (2, 2)); g.putdata([c1, c1, c2, c2]); return g.resize((W, H), Image.BILINEAR)
def rust_texture(w, h, seed=29):
    rnd = random.Random(seed); im = Image.new("RGB", (w, h), RUST); d = ImageDraw.Draw(im)
    for _ in range(max(w * h // 90, 50)):
        x, y, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(2, 9)
        d.ellipse((x-r, y-r, x+r, y+r), fill=rnd.choice([(120, 56, 22), (150, 70, 30), (205, 112, 60), (96, 44, 18)]))
    return im.filter(ImageFilter.GaussianBlur(0.6))
def glow_line(base, p1, p2, core=6, glow=40):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (120,), width=glow)
    layer = layer.filter(ImageFilter.GaussianBlur(12)); d = ImageDraw.Draw(layer)
    d.line([p1, p2], fill=SKY + (255,), width=core + 6); d.line([p1, p2], fill=WHITE + (255,), width=core)
    base.paste(layer, (0, 0), layer)
def spark(base, c, r=16):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r*2.2, c[1]-r*2.2, c[0]+r*2.2, c[1]+r*2.2), fill=SKY + (150,))
    layer = layer.filter(ImageFilter.GaussianBlur(14)); d = ImageDraw.Draw(layer)
    d.ellipse((c[0]-r, c[1]-r, c[0]+r, c[1]+r), fill=WHITE + (255,)); base.paste(layer, (0, 0), layer)
def text_mask(text, font, spacing=0):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); l, t, r, b = d.textbbox((0, 0), text, font=font)
    w = int(r - l + spacing * (len(text) - 1)) + 4; h = int(b - t) + 4
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m); x = -l + 2
    for ch in text:
        md.text((x, -t + 2), ch, font=font, fill=255); x += d.textlength(ch, font=font) + spacing
    return m
def put(base, text, cx, cy, font, fill, spacing=0, align="center"):
    m = text_mask(text, font, spacing)
    x = int(cx - m.width / 2) if align == "center" else int(cx)
    base.paste(Image.new("RGB", m.size, fill), (x, int(cy - m.height / 2)), m); return m.size

def fade_wordmark(base, cx, cy, max_w, size):
    f = fnt("Unbounded.ttf", size, 800); m = text_mask("TUR-LASER", f, 2)
    if m.width > max_w:
        f = fnt("Unbounded.ttf", int(size * max_w / m.width), 800); m = text_mask("TUR-LASER", f, 2)
    x, y = int(cx - m.width / 2), int(cy - m.height / 2)
    ramp = Image.linear_gradient("L").rotate(90, expand=True).resize(m.size)
    ramp = ramp.point(lambda v: 0 if v < 70 else 255 if v > 150 else int((v - 70) * 255 / 80))
    fill = Image.composite(Image.new("RGB", m.size, WHITE), rust_texture(m.width, m.height), ramp)
    base.paste(fill, (x, y), m)
    sx = x + int(m.width * 0.43)
    glow_line(base, (sx, y - int(m.height * 0.75)), (sx, y + m.height + int(m.height * 0.75)), core=5, glow=34)
    spark(base, (sx, y - int(m.height * 0.75)), r=12)
    return x, y, m.width, m.height

# ---- лицо ----
front = gradient()
x, y, w, h = fade_wordmark(front, W // 2, H // 2 - 20, W - 2 * SAFE - 60, 150)
put(front, "ОЧИСТКА VIN ОТ РЖАВЧИНЫ", W // 2, y + h + 95, fnt("Manrope.ttf", 36, 700), WHITE)

# ---- оборот ----
back = gradient()
lx = SAFE + 20
put(back, "TUR-LASER", lx, SAFE + 40, fnt("Manrope.ttf", 40, 800), WHITE, 6, align="left")
put(back, "Лазерная очистка VIN, номера рамы и двигателя", lx, SAFE + 92, fnt("Manrope.ttf", 23, 600), SKY, align="left")
put(back, NAME, lx, H // 2 - 72, fnt("Manrope.ttf", 34, 700), WHITE, align="left")
put(back, PHONE, lx, H // 2 - 10, fnt("Unbounded.ttf", 50, 800), WHITE, align="left")
put(back, "Санкт-Петербург и область", lx, H // 2 + 70, fnt("Manrope.ttf", 28, 700), WHITE, align="left")
put(back, "выезд за 30 минут · чистка 10 минут", lx, H // 2 + 112, fnt("Manrope.ttf", 28, 600), SKY, align="left")
# QR на Telegram
qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M if len(QR_URL) > 40 else ERROR_CORRECT_H, box_size=10, border=0); qr.add_data(QR_URL); qr.make(fit=True)
qim = qr.make_image(fill_color=NAVY, back_color=WHITE).convert("RGB")
side = 270; qim = qim.resize((side - 36, side - 36), Image.NEAREST)
px, py = W - SAFE - side + 4, (H - side) // 2 - 26
panel = Image.new("RGB", (side, side), WHITE); panel.paste(qim, (18, 18))
mk = Image.new("L", (side, side), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, side - 1, side - 1), 24, fill=255)
back.paste(panel, (px, py), mk)
put(back, QR_LABEL, px + side // 2, py + side + 34, fnt("Manrope.ttf", 24, 700), WHITE)
put(back, QR_SUB, px + side // 2, py + side + 66, fnt("Manrope.ttf", 22, 600), SKY)

for im, name in ((front, "vizitka-lico"), (back, "vizitka-oborot")):
    im.save(OUT / f"{name}.png", dpi=(DPI, DPI))
front.save(OUT / "vizitka.pdf", "PDF", resolution=DPI, save_all=True, append_images=[back])

# превью: обе стороны по линии реза, рядом
def trim(im): return im.crop((BLEED, BLEED, W - BLEED, H - BLEED))
a, b = trim(front), trim(back); gap = 40
sheet = Image.new("RGB", (a.width + b.width + gap * 3, a.height + gap * 2), (235, 235, 235))
sheet.paste(a, (gap, gap)); sheet.paste(b, (a.width + gap * 2, gap)); sheet.save(OUT / "preview.jpg", quality=90)
print("готово:", W, "x", H, "px (96×56 мм с вылетами), QR →", QR_URL)
