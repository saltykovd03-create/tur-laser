#!/usr/bin/env python3
"""Генерирует заглушки «до/после» для галереи, пока нет настоящих фото.

Запуск: python3 tools/placeholders.py  →  img/before-N.jpg, img/after-N.jpg
Настоящие фото кладите под теми же именами — разметка менять не нужно.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent.parent / "img"
OUT.mkdir(exist_ok=True)

FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]


def font(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def metal(w, h, seed):
    """Шлифованный металл: горизонтальные штрихи + мягкий градиент."""
    rnd = random.Random(seed)
    base = Image.new("RGB", (w, h), (168, 174, 181))
    px = base.load()
    for y in range(h):
        tone = rnd.randint(-10, 10)
        for x in range(w):
            v = 160 + tone + rnd.randint(-6, 6) + int(22 * (x / w))
            px[x, y] = (v, v + 3, v + 7)
    return base.filter(ImageFilter.GaussianBlur(0.6))


def stamp(img, text, size, fill, shadow):
    d = ImageDraw.Draw(img)
    f = font(size)
    w, h = img.size
    bbox = d.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (w - tw) // 2, (h - th) // 2
    d.text((x + 2, y + 2), text, font=f, fill=shadow)
    d.text((x, y), text, font=f, fill=fill)


def rust_layer(w, h, seed, strength):
    """Пятна ржавчины: шум → размытие → порог → цвет."""
    rnd = random.Random(seed)
    small = Image.new("L", (w // 8, h // 8))
    sp = small.load()
    for y in range(h // 8):
        for x in range(w // 8):
            sp[x, y] = rnd.randint(0, 255)
    mask = small.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(14))
    mask = mask.point(lambda v: max(0, min(255, int((v - 128) * 3.2 + 128 * strength))))
    grain = Image.new("L", (w, h))
    gp = grain.load()
    for y in range(h):
        for x in range(w):
            gp[x, y] = rnd.randint(0, 255)
    grain = grain.filter(ImageFilter.GaussianBlur(1.2))
    mask = Image.blend(mask, grain, 0.18)
    colour = Image.new("RGB", (w, h), (134, 72, 34))
    streak = Image.new("RGB", (w, h), (92, 46, 22))
    colour = Image.blend(colour, streak, 0.35)
    return colour, mask


def make_pair(n, vin, w=960, h=640):
    rnd = random.Random(n)
    after = metal(w, h, seed=n * 7)
    # кант пластины
    d = ImageDraw.Draw(after)
    d.rectangle([24, 24, w - 25, h - 25], outline=(120, 126, 134), width=3)
    stamp(after, vin, size=int(w / 11), fill=(70, 76, 86), shadow=(222, 226, 232))
    after.filter(ImageFilter.GaussianBlur(0.3)).save(OUT / f"after-{n}.jpg", quality=82)

    before = after.copy()
    colour, mask = rust_layer(w, h, seed=n * 13, strength=1.0 + rnd.random() * 0.4)
    before.paste(colour, (0, 0), mask)
    before = before.filter(ImageFilter.GaussianBlur(0.4))
    before.save(OUT / f"before-{n}.jpg", quality=82)


if __name__ == "__main__":
    vins = ["XW8TURLASER260001", "X9F TUR 0L4S 3R00 2", "Z8T TURL ASE R2603", "XTA LASER 00 2604"]
    for i, v in enumerate(vins, start=1):
        make_pair(i, v)
    print("ok:", sorted(p.name for p in OUT.iterdir()))
