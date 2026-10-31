#!/usr/bin/env python3
"""Proof sheet: letters cut from the printed 1869 alphabet chart (left) vs Beehive (right).

    python3 period_proof.py bookofmormdeseretalpha00.pdf OUT.png

Needs pymupdf, numpy, pillow. The chart is page 2 of the 1869 Deseret Alphabet Book of Mormon scan.
"""
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
NAMES = ("long_i long_e long_a long_ah long_o long_oo short_i short_e short_a short_ah short_o short_oo ay ow wu yee h "
         "pee bee tee dee chee jee kay gay ef vee eth thee es zee esh zhee er el em en eng").split()
import skeletons as sk

pdf, out = sys.argv[1], sys.argv[2]
page = fitz.open(pdf)[1].get_pixmap(dpi=500)
gray = np.array(Image.frombytes("RGB", (page.width, page.height), page.samples).convert("L"))
img = Image.fromarray(gray)
h = gray.shape[0]
dark = gray < 120


def bands(x0, x1, y0, y1, gap=10, minh=30):
    prof = dark[y0:y1, x0:x1].sum(axis=1) > 1
    res, start, last = [], None, None
    for i, v in enumerate(prof):
        if v:
            start = i if start is None else start
            last = i
        elif start is not None and i - last > gap:
            if last - start >= minh:
                res.append((start + y0, last + y0))
            start = None
    if start is not None and last - start >= minh:
        res.append((start + y0, last + y0))
    return res


left = bands(340, 455, int(h * .2), int(h * .93))
right = bands(1365, 1480, int(h * .17), int(h * .93))
crops = [img.crop((335, a - 10, 450, b + 10)) for a, b in left] + [img.crop((1360, a - 10, 1475, b + 10)) for a, b in right]
assert len(crops) == len(NAMES), (len(left), len(right))

font = ImageFont.truetype(str(ROOT / "fonts" / "BeehiveDeseretMono-Regular.ttf"), 464)
cols, cw, chh = 5, 330, 215
sheet = Image.new("RGB", (cols * cw, (len(NAMES) + cols - 1) // cols * chh), "white")
d = ImageDraw.Draw(sheet)
label = ImageFont.load_default(15)
for i, (nm, crop) in enumerate(zip(NAMES, crops)):
    x, y = (i % cols) * cw, (i // cols) * chh
    sheet.paste(crop.convert("RGB"), (x + 8, y + 8))
    ch = chr(0x10428 + sk.DESERET_ORDER.index(nm))
    tile = Image.new("L", (900, 900), 255)
    ImageDraw.Draw(tile).text((100, 20), ch, font=font, fill=0)
    box = Image.eval(tile, lambda v: 255 - v).getbbox()
    glyph = tile.crop(box)
    s = (crops[i].height - 20) / (620 / 1000 * 464)
    glyph = glyph.resize((max(1, int(glyph.width * s)), max(1, int(glyph.height * s))), Image.LANCZOS)
    sheet.paste(glyph.convert("RGB"), (x + 170, y + 18 + (crops[i].height - 20 - glyph.height) // 2 + 0))
    d.text((x + 8, y + chh - 24), nm, fill=(180, 40, 40), font=label)
sheet.save(out)
print(out)
