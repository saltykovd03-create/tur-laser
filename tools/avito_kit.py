#!/usr/bin/env python3
"""Фото для Авито: квадратные пары «до/после» из живых снимков, без дизайна.

Запуск:  python3 tools/avito_kit.py  →  avito/01.jpg, 02.jpg …  (первая = обложка)
Пары задаются списком PAIRS ниже: (фото до, фото после, точка кадра до, точка кадра после).
Точка кадра — (x, y) в долях, куда смотреть при обрезке (где на снимке номер).

Формат: квадрат 1200×1200, верхняя половина — «до», нижняя — «после», тонкая
белая линия между ними, две маленькие подписи. Больше ничего.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"
OUT = ROOT / "avito"
OUT.mkdir(exist_ok=True)
FONT = ROOT / "tools" / "fonts" / "Manrope.ttf"

S = 1200            # сторона квадрата
GAP = 6             # белая линия между половинами
C = (0.5, 0.5)      # центр кадра по умолчанию

# (до, после, фокус до, фокус после) — пути относительно img/
# Оригиналы из TG-группы «Tur laser» (Слава, 15.10.2026), номер файла = id сообщения.
PAIRS = [
    ("tg/628335.jpg", "tg/628336.jpg", (0.5, 0.45), (0.5, 0.5)),    # рамка грузовика, табличка под ней
    ("tg/628341.jpg", "tg/628342.jpg", (0.5, 0.55), (0.5, 0.5)),    # арка колеса: чёрное пятно → номер
    ("tg/628345.jpg", "tg/628346.jpg", (0.5, 0.37), (0.5, 0.55)),   # под герметиком с линейкой → чистая табличка
    ("tg/628343.jpg", "tg/628344.jpg", (0.45, 0.42), (0.45, 0.4)),  # лонжерон с отверстиями
    ("tg/628337.jpg", "tg/628338.jpg", (0.45, 0.4), (0.5, 0.55)),   # табличка в проёме
    ("tg/628339.jpg", "tg/628340.jpg", (0.5, 0.38), (0.5, 0.6)),    # тёмный снимок → номер
    ("tg/628348.jpg", "tg/628349.jpg", (0.5, 0.5), (0.45, 0.5)),    # жёлтая заводская краска до → голый металл после
]


def load(name):
    im = Image.open(IMG / name)
    im = ImageOps.exif_transpose(im)      # фото с телефона часто повёрнуты в EXIF
    return im.convert("RGB")


def crop(im, w, h, focus):
    sw, sh = im.size
    k = max(w / sw, h / sh)
    im = im.resize((round(sw * k), round(sh * k)), Image.LANCZOS)
    nw, nh = im.size
    x = min(max(round(nw * focus[0] - w / 2), 0), nw - w)
    y = min(max(round(nh * focus[1] - h / 2), 0), nh - h)
    return im.crop((x, y, x + w, y + h))


def label(base, text, corner, size=34, dy=0, cy=None):
    """Подпись: полупрозрачная тёмная плашка, белый текст. corner — угол,
    dy — сдвиг от угла, cy — вместо угла по вертикали центрировать на этой высоте."""
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([700])
    except Exception:
        pass
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    tw, th = r - l, b - t
    pw, ph = tw + 40, th + 22
    x = 28 if corner[0] == "l" else S - 28 - pw
    y = 28 + dy if corner[1] == "t" else S - 28 - ph - dy
    if cy is not None:
        y = cy - ph // 2
    d.rounded_rectangle((x, y, x + pw, y + ph), ph // 2, fill=(0, 0, 0, 120))
    d.text((x + 20 - l, y + 11 - t), text, font=f, fill=(255, 255, 255, 255))
    base.paste(layer, (0, 0), layer)


COVER_TITLE = "Чистка без вреда металлу"
COVER_TITLE2 = "выезд 30 минут"
COVER_SUB = "СПб и ЛО"


SKY = (124, 196, 255)   # голубой из палитры сайта — для цифр


def label_rich(base, parts, corner, size=46, dy=0):
    """Подпись из кусков разного цвета: [("выезд ", белый), ("30 минут", голубой)]."""
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([800])
    except Exception:
        pass
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    text = "".join(t for t, _ in parts)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    tw, th = r - l, b - t
    pw, ph = tw + 40, th + 22
    x = 28 if corner[0] == "l" else S - 28 - pw
    y = 28 + dy if corner[1] == "t" else S - 28 - ph - dy
    if cy is not None:
        y = cy - ph // 2
    d.rounded_rectangle((x, y, x + pw, y + ph), ph // 2, fill=(0, 0, 0, 130))
    cx = x + 20 - l
    for txt, color in parts:
        d.text((cx, y + 11 - t), txt, font=f, fill=color + (255,))
        cx += d.textlength(txt, font=f)
    base.paste(layer, (0, 0), layer)


def band_center(base, lines, pad=34, gap=14, fill=(8, 22, 54, 225)):
    """Полоса посередине кадра (на линии раздела) с центрированными строками.
    lines — список строк, строка — список кусков (текст, цвет, размер)."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fonts = {}

    def fnt(size):
        if size not in fonts:
            f = ImageFont.truetype(str(FONT), size)
            try:
                f.set_variation_by_axes([800])
            except Exception:
                pass
            fonts[size] = f
        return fonts[size]

    measured = []
    for line in lines:
        w = sum(d.textlength(t, font=fnt(sz)) for t, _, sz in line)
        h = max(sz for _, _, sz in line)
        measured.append((w, h))
    total_h = sum(h for _, h in measured) + gap * (len(lines) - 1)
    top = S // 2 - total_h // 2 - pad
    d.rectangle((0, top, S, top + total_h + pad * 2), fill=fill)
    y = top + pad
    for line, (w, h) in zip(lines, measured):
        x = (S - w) // 2
        for t, color, sz in line:
            f = fnt(sz)
            l, tt, r, b = d.textbbox((0, 0), t, font=f)
            d.text((x - l, y + (h - (b - tt)) // 2 - tt), t, font=f, fill=color + (255,))
            x += d.textlength(t, font=f)
        y += h + gap
    base.paste(layer, (0, 0), layer)


def make(before, after, fb, fa, path, cover=False):
    h = (S - GAP) // 2
    base = Image.new("RGB", (S, S), (255, 255, 255))
    base.paste(crop(load(before), S, h, fb), (0, 0))
    base.paste(crop(load(after), S, h, fa), (0, S - h))
    # подписи слева, по центру каждой половины
    label(base, "до", ("l", "t"), size=44, cy=h // 2)
    label(base, "после", ("l", "b"), size=44, cy=S - h // 2)
    if cover:
        # немного текста только на обложке: заголовок сверху справа, город снизу справа
        W_ = (255, 255, 255)
        band_center(base, [
            [("Чистка лазером без вреда", W_, 72)],
            [("выезд ", W_, 60), ("30 минут", SKY, 72), ("  ·  СПб и ЛО", W_, 60)],
        ])
    base.save(path, quality=93, subsampling=0)


if __name__ == "__main__":
    for i, (b, a, fb, fa) in enumerate(PAIRS, 1):
        make(b, a, fb, fa, OUT / f"{i:02d}.jpg", cover=(i == 1))
    print("готово:", *(OUT / f"{i:02d}.jpg" for i in range(1, len(PAIRS) + 1)), sep="\n  ")
